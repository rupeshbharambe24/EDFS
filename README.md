# EDFS — Electricity Demand Forecasting System

A Flask web application that predicts electricity demand at **daily, hourly, and 5-minute** resolutions using historical consumption data, real-time weather signals, and holiday information.

> **Note:** This was my SIH 2024 prototype. The newer, significantly more accurate version is [**Gridalytics**](https://github.com/rupeshbharambe24/Gridalytics) — built with 7 ML models, walk-forward CV, and 0.18% MAPE on the same problem. This repo is preserved as the original implementation.

## Approach

- **Models:** SARIMAX, ARIMA, Transformers, and Regression — SARIMAX selected as the production model for its handling of weather/holiday exogenous regressors.
- **Data sources:** Historical demand + Visual Crossing Weather API (temperature, humidity, wind, rainfall) + Indian holidays.
- **Three trained models** for daily, hourly, and 5-minute horizons (each saved as a `.pkl` and selected per request).
- **Auto-training** scheduler refreshes models with new data.

## Tech Stack

- Backend: Flask
- ML: scikit-learn, statsmodels (SARIMAX), joblib
- Data: pandas, numpy
- Auth + DB: Firebase Authentication + Realtime Database
- Weather API: Visual Crossing
- Frontend: HTML, CSS, JavaScript (Jinja2 templates)
- Deployment: Docker + Google Cloud Run

## Project Structure

```
EDFS/
├── app.py                # Flask app: auth, prediction, weather fetch, contact form
├── train/                # Training notebooks (daily, hourly, 5-min)
├── models/               # Trained .pkl model files (gitignored)
├── templates/            # index, login, signup, model pages
├── static/               # CSS, JS, assets
├── Dockerfile            # Container build
├── requirements.txt
└── .env.example
```

## Setup

```bash
git clone https://github.com/rupeshbharambe24/EDFS.git
cd EDFS

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Fill in API_KEY, FIREBASE_*, FLASK_SECRET_KEY, CONTACT_* values

python app.py
```

Visit `http://localhost:5000`.

### Firebase setup

1. Create a Firebase project, enable Email/Password authentication and Realtime Database.
2. Download the Admin SDK JSON and set `FIREBASE_CREDENTIALS_PATH` in `.env` to its local path.
3. Set `FIREBASE_DATABASE_URL` to your project's Realtime Database URL.

### Docker / Cloud Run

```bash
docker build -t edfs .
docker run -p 5000:5000 --env-file .env edfs

# Or deploy to Cloud Run
gcloud run deploy edfs --source .
```

## What it does

- Login / signup via Firebase
- Pick a horizon (daily / hourly / 5-min)
- Fetches weather and constructs the feature window
- Loads the corresponding pre-trained SARIMAX model
- Returns the forecast as a chart on the model page

## Limitations

- Single SARIMAX model per horizon, no per-region forecasting
- No automated retraining trigger from the UI
- No drift detection or prediction tracking — see Gridalytics for the production-grade version
