# AI Rate Prediction

## 1) Umumiy yondashuv — nima qilasiz (qisqacha)
- Markaziy bank API (CBU) dan USD—so‘m kursining arxiv ma’lumotlarini (2018-12-01 dan hozirgi kungacha) yuklab olasiz. 
- Ma’lumotni tozalaysiz (sanani datetime qilib, yo‘qolgan kunlar/mahalliy bayramlarni tekshirish).
- EDA (vizualizatsiya): trend, mavsumiylik, o‘zgarishlar (kunlik o‘zgarishlar).
- Xususiyat yaratish (laglar, oynalik o‘rtacha, hafta/kalendar xususiyatlari).
- Model qurish — bir nechta variantni sinaysiz (baseline + statistik + mashinaviy o‘rganish + neyron tarmoq).
- Baholash — backtesting (walk-forward), MAE/RMSE/MAPE, 7 va 30 kunlik forward forecast.
- Grafik chizish: real qiymat, prognoz qiymat, va “ko‘tarilgan” / “tushgan” kunlarni belgilash.
- 

## 2) Ma’lumot olish (CBU API)
- CBU API orqali JSON yoki XML formatda so‘rov yuborish mumkin. Misol endpointlar (rasmiy hujjatda, fetch_data.py):
- https://cbu.uz/uz/arkhiv-kursov-valyut/json/ — parametrsiz so‘rov joriy sanadagi kurslarni qaytaradi.
- https://cbu.uz/uz/arkhiv-kursov-valyut/json/all/2018-12-11/ — berilgan sanadagi barcha valyutalar.
- https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/2019-01-01/ kabi xususiy valyuta+sanani ham so‘rash mumkin. Rasmiy sahifada bu misollar keltirilgan. 

Amalga oshirish: kunlar bo‘yicha sikl qilib, 2018-12-01 dan hozirgi kungacha API dan kerakli sanalar bo‘yicha USD qiymatlarini yig‘ish mumkin.

## 3) Ma’lumotni yuklash va preprocessing
- Yo‘qolgan kunlar (agar ba’zi sanalar uchun API qiymat bermasa) uchun interpolate yoki oldingi qiymat bilan to‘ldirish (business decision: real dunyoda dam olish kunlarida ham MB rasmiy kursi beriladi, shuning uchun avval API formatini tekshirish kerak).
- Sanani index qilib, rate ustunini floatga o‘tkazing.

## 4) EDA (Exploratory Data Analysis)
- Vizual: matplotlib yoki plotly bilan ustunli chiziqli grafik — umumiy trend ko‘rinishi.
- Kunlik returns: df['diff'] = df['rate'].diff() va df['pct'] = df['rate'].pct_change() — hodisalar va o‘zgarmalar histogrami.
- Mavsumiylik: rolling(7).mean(), rolling(30).mean() bilan oynalik o‘rtachalar ko‘rsatiladi.
- Outlier-larni tekshirish va kerak bo‘lsa winsorize qilish.

## 5) Xususiyatlar (feature engineering)
- Forecast uchun odatda quyidagilar ishlaydi:
- Lag features: rate(t-1), rate(t-2), ..., rate(t-7)
- Rolling stats: rolling_mean_7, rolling_std_7, rolling_mean_30
- Calendar features: weekday, is_month_start, day_of_month, is_holiday (agar mavjud bo‘lsa)

## 6) Modellar (Har birida test qilib, eng yaxshisini olish uchun)
- Prophet
- Srima
- XGBoost
- LSTM 
- NBeats

## 7) Train, Validation va Test
- Train / validation split sodda holda oxirgi N kunni (masalan so‘nggi 90 kun) testga ajrating. Ammo vaqt qatorlarida an’anaviy random split noto‘g‘ri.
- Baholash metrikalari: MAE, RMSE, R2 Score.


## 8) Code structure
Repository tuzilishi misoli:

Ai_rate_prediction/
- ├─ data/                    # API orqali olingan datalar
- ├─ src/
- │  ├─ fetch_data.py
- │  ├─ feature_ext_eng.ipynb
- │  ├─ preprocess_data.ipynb
- │  ├─ prophet_model.ipynb
- │  ├─ sarima_model.ipynb
- │  ├─ xgboost_model.ipynb
- │  ├─ lstm_model.ipynb
- │  └─ nbeats_model.ipynb
- ├─ requirements.txt
- ├─ README.md
- └─ LICENSE

## 9) Texnologiyalar va kutubxonalar (tavsiya)
- Python 3.10+
- matplotlib yoki plotly (interaktiv) — tavsiya: plotly (presentation uchun)
- statsmodels (ARIMA/SARIMA), prophet (fbprophet yoki prophet), scikit-learn, xgboost
- tensorflow/keras yoki pytorch (LSTM) — agar chuqur model ishlatsangiz
- jupyterlab / notebooks

## 10) Yuklab olish va ishga tushirish
- git clone https://github.com/username/currency-forecast.git
- python -m venv .venv
- pip install -r requirements.txt
