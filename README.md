# 🔌 Real-Time Electricity Demand Forecasting

## 🚀 Overview
This project is a real-time electricity demand forecasting system that predicts **daily, hourly, and 5-minute electricity demand** with an accuracy of over **98%**. The system utilizes **historical electricity consumption data**, real-time **weather data**, and **holiday information** to provide accurate forecasts.

The project integrates **Python, Flask, Firebase, Google Cloud Platform (GCP), and Visual Crossing API** to build a scalable, responsive, and secure web-based forecasting system.

## ✨ Features
- **High Accuracy Forecasting:** Uses **SARIMA**, ARIMA, Transformers, and Regression models, with SARIMA delivering the best results.
- **Three Prediction Models:** Supports **daily, hourly, and 5-minute** demand forecasting.
- **Real-Time Data Enrichment:** Fetches weather data (temperature, humidity, wind speed, rainfall) from **Visual Crossing API**.
- **Automated Training:** Models auto-update daily with new data for continuous improvement.
- **User Authentication:** Uses **Firebase Authentication** for secure access (admin approval required).
- **Cloud Deployment:** Fully deployed using **Docker and Google Cloud Run** for scalability.
- **Responsive Frontend:** Built with **HTML, CSS, and JavaScript** for an intuitive user experience.

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **Machine Learning Models:** SARIMA, ARIMA, Transformers, Regression
- **Authentication & Database:** Firebase (Realtime Database & Authentication)
- **Cloud & Deployment:** Google Cloud Platform (Cloud Run, Docker)
- **Weather Data API:** Visual Crossing API

## 📦 Installation & Setup
### 🔹 Prerequisites
Ensure you have the following installed:
- Python 3.x
- Flask
- Docker
- Firebase account
- Google Cloud SDK

### 🔹 Clone the Repository
```bash
git clone https://github.com/yourusername/electricity-demand-forecasting.git
cd electricity-demand-forecasting
```

### 🔹 Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 🔹 Set Up Firebase
1. Create a **Firebase Project** in the [Firebase Console](https://console.firebase.google.com/).
2. Enable **Authentication** (Email/Password) & **Realtime Database**.
3. Download `serviceAccountKey.json` from Firebase and place it in the project root.
4. Add Firebase configuration in `config.js` (for frontend authentication).

### 🔹 Set Up Environment Variables
Create a `.env` file in the project root and add:
```env
FIREBASE_CONFIG="your_firebase_config"
WEATHER_API_KEY="your_visual_crossing_api_key"
```

### 🔹 Run Flask Backend
```bash
python app.py
```

### 🔹 Run Frontend
Open `index.html` in a browser or use a local server:
```bash
python -m http.server 8000
```
Then visit `http://localhost:8080`.

### 🔹 Deploy Using Docker & Google Cloud Run
1. Build the Docker image:
```bash
docker build -t electricity-demand-forecast .
```
2. Push to Google Cloud:
```bash
gcloud auth configure-docker
docker tag electricity-demand-forecast gcr.io/YOUR_PROJECT_ID/electricity-demand-forecast
docker push gcr.io/YOUR_PROJECT_ID/electricity-demand-forecast
```
3. Deploy with Cloud Run:
```bash
gcloud run deploy electricity-demand-forecast --image gcr.io/YOUR_PROJECT_ID/electricity-demand-forecast --platform managed --allow-unauthenticated
```

## 🔍 Usage
1. **Login/Register** (requires admin approval via Firebase).
2. Select **Daily, Hourly, or 5-Minute Prediction**.
3. View real-time demand forecasts based on historical trends, weather, and holidays.

## 📈 Model Performance
| Model        | Accuracy |
|-------------|---------|
| Daily       | 98.5%   |
| Hourly      | 98.2%   |
| 5-Minute    | 98.1%   |

## 🏗️ Future Enhancements
- **More advanced deep learning models** for further accuracy improvements.
- **Integration with IoT devices** for real-time energy consumption tracking.
- **Mobile App** for easy access to predictions on the go.

## 🤝 Contributions
Feel free to fork, contribute, and submit PRs. Suggestions and improvements are always welcome!

## 📜 License
This project is licensed under the **MIT License**.

## 📬 Contact
For any queries, reach out via [LinkedIn](https://www.linkedin.com/in/yourprofile) or open an issue on GitHub.

---
🔗 **Try the live project here:** [Site](https://edfs-app-923630851302.us-central1.run.app/)  
🔑 **Trial Credentials:** [Your Trial ID: trial@gmail.com & Password: trial123]

