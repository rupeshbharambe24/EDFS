# EDFS — Electricity Demand Forecasting System

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-web%20app-000000?logo=flask&logoColor=white)
![statsmodels](https://img.shields.io/badge/model-SARIMAX-4B8BBE)
![SIH 2024](https://img.shields.io/badge/SIH-2024%20%C2%B7%20PS%201624-orange)
![Status](https://img.shields.io/badge/status-superseded%20by%20Gridalytics-lightgrey)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

A Flask web application that predicts electricity demand at **daily, hourly, and 5-minute** resolutions using historical consumption data, real-time weather signals, and holiday information.

> [!IMPORTANT]
> **Superseded by [Gridalytics](https://github.com/rupeshbharambe24/Gridalytics).** EDFS was our Smart India Hackathon 2024
> prototype for problem statement **1624** (electricity demand projection for the Delhi power grid). Gridalytics is the
> maintained successor: gradient-boosted champion/challenger models evaluated with leak-free walk-forward
> cross-validation against a persistence baseline, extended beyond Delhi to other Indian states. This repo is kept,
> unchanged in substance, as the original implementation.

## Approach

- **Models:** `pmdarima.auto_arima` is used to explore orders, then a **SARIMAX** model with weather/holiday exogenous regressors is fitted per horizon (see `train/`). SARIMAX was chosen for its handling of exogenous regressors.
- **Data sources:** Historical demand + Visual Crossing Weather API (temperature, humidity, wind, rainfall) + Indian holidays.
- **Three trained models** for daily, hourly, and 5-minute horizons (each saved as a `.pkl` and selected per request).
- Retraining is manual: re-run the notebook for a horizon and replace its `.pkl` in `models/`.

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
├── train/                # Training notebooks (daily, hourly, 5-min SARIMAX)
├── models/               # Trained .pkl files go here (gitignored, produced by the notebooks)
├── templates/            # index, login, signup, model pages
├── static/               # CSS, JS, assets
├── Dockerfile            # Container build
├── requirements.txt
├── .env.example
└── LICENSE
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

# Train the models first (or copy existing ones) so these files exist:
#   models/daily-model.pkl, models/hourly-model.pkl, models/5Min-model.pkl
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
- The error metrics printed in the notebooks (MAPE roughly 0.3–5%) are computed after fitting SARIMAX on the full
  series, including the evaluation window, with a one-step shift of the predictions. They are in-sample and
  optimistic; Gridalytics re-did the evaluation leak-free.
- The trained `.pkl` files and the raw demand data are not included in the repo.

## Team

Built for SIH 2024 by Rupesh Bharambe (team lead), Harshal More, Onkar Kalyankar, Sanket Sarode and Aniket Wahul.

## Related repositories

| Repository | Description |
|------------|-------------|
| **EDFS** (this repo) | SIH 2024 prototype: Flask + SARIMAX, Delhi demand at daily / hourly / 5-min resolution |
| [Gridalytics](https://github.com/rupeshbharambe24/Gridalytics) | Successor: state-by-state demand forecasting with leak-free evaluation, FastAPI + Next.js |

## License

Released under the [MIT License](LICENSE).
