"""
CBU arxiv API dan USD kurslarini olib CSV faylga yozadigan FastAPI xizmati.

Ishga tushirish:
    uvicorn fetch_data:app --reload
So'ng chaqirish:
    GET /fetch (start_date, end_date parametrlarini ixtiyoriy o'rnating)
"""
from __future__ import annotations

import csv
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query


# API manzili va chiqish sozlamalari
BASE_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/{}/"
OUTPUT_PATH = Path("usd_rates.csv")
DEFAULT_START = date(2018, 12, 1)
DEFAULT_END = date(2025, 12, 9)

# Oddiy logger sozlamasi
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="USD to UZS Fetcher",
    description="Berilgan oraliqdagi har bir kunni tekshiradi, USD kurslarini oladi va CSV ga yozadi.",
    version="1.0.0",
)


def iter_days(start: date, end: date) -> Iterable[date]:
    """Boshlanishdan tugaguncha har bir kunni (inklyuziv) beradi."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def date_to_path_fragment(day: date) -> str:
    """CBU endpointi yetakchi nol holda yil-oy-kun ko'rinishini kutadi."""
    return f"{day.year}-{day.month}-{day.day}"


async def fetch_day(client: httpx.AsyncClient, day: date) -> Optional[List[dict]]:
    """
    Bir kun uchun ma'lumotni olib keladi.
    So'rov xatosida None, ma'lumot bo'lmasa bo'sh ro'yxat qaytaradi.
    """
    url = BASE_URL.format(date_to_path_fragment(day))
    try:
        response = await client.get(url, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError:
        # Kun yo'q yoki server xato qaytardi; ma'lumot yo'q deb qabul qilamiz
        logger.info("No data (HTTP error) for %s", day.isoformat())
        return []
    except httpx.RequestError as exc:
        # Tarmoq yoki ulanish muammosi; log qilib, tashlab ketamiz
        logger.warning("Request failed for %s: %s", day.isoformat(), exc)
        return None

    if not payload:
        logger.info("No data for %s", day.isoformat())
        return []

    if isinstance(payload, dict):
        # Ro'yxatga keltiramiz
        return [payload]

    if isinstance(payload, list):
        return payload

    logger.warning("Unexpected payload shape for %s: %s", day.isoformat(), type(payload))
    return []


def write_rows(path: Path, rows: List[dict], fieldnames: List[str], header_written: bool) -> bool:
    """CSV ga qator qo'shadi, kerak bo'lsa sarlavha yozadi. header_written holatini qaytaradi."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
        if not header_written:
            writer.writeheader()
            header_written = True
        writer.writerows(rows)
    return header_written


async def collect_rates(start_date: date, end_date: date, output: Path) -> dict:
    """
    Har bir kunni aylanib, ma'lumotlarni olib CSV ga yozadi.
    API javobi uchun qisqa natijaviy lug'at qaytaradi.
    """
    if end_date < start_date:
        raise ValueError("end_date must not be earlier than start_date")

    header_written = output.exists()
    written_rows = 0
    skipped_days = 0
    failed_days = 0
    fieldnames: List[str] = []

    async with httpx.AsyncClient() as client:
        for day in iter_days(start_date, end_date):
            payload = await fetch_day(client, day)
            if payload is None:
                failed_days += 1
                continue
            if not payload:
                skipped_days += 1
                continue

            if not fieldnames:
                # Ustunlarni doimiy ushlab turish uchun birinchi muvaffaqiyatli javob kalitlarini olamiz
                fieldnames = list(payload[0].keys())

            header_written = write_rows(output, payload, fieldnames, header_written)
            written_rows += len(payload)
            logger.info("Saved %d rows for %s", len(payload), day.isoformat())

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "written_rows": written_rows,
        "skipped_days": skipped_days,
        "failed_days": failed_days,
        "output_file": str(output),
    }


@app.get("/fetch")
async def fetch_endpoint(
    start_date: date = Query(default=DEFAULT_START, description="Boshlanish sanasi (YYYY-MM-DD)"),
    end_date: date = Query(default=DEFAULT_END, description="Tugash sanasi (YYYY-MM-DD)"),
) -> dict:
    """
    Kunma-kun ma'lumot yig'ish va CSV ga yozishni ishga tushiradi.
    """
    try:
        summary = await collect_rates(start_date, end_date, OUTPUT_PATH)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return summary


@app.get("/")
async def root() -> dict:
    """Xizmat ishlayotganini bildiruvchi health endpoint."""
    return {"message": "USD to UZS fetcher is running"}
