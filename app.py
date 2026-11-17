from flask import Flask, render_template, request, redirect, session, flash, jsonify
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from datetime import timedelta
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, auth, db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()  # Load environment variables from .env before reading any config

app = Flask(__name__)

# Initialize Firebase Admin SDK
# Set FIREBASE_CREDENTIALS_PATH and FIREBASE_DATABASE_URL in your .env file
firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
firebase_db_url = os.getenv('FIREBASE_DATABASE_URL')
cred = credentials.Certificate(firebase_cred_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': firebase_db_url
})

# Define model paths
DAILY_MODEL_PATH = os.path.join("models", "daily-model.pkl")
HOURLY_MODEL_PATH = os.path.join("models", "hourly-model.pkl")
MIN5_MODEL_PATH = os.path.join("models", "5Min-model.pkl")

# Define the API Key and base URL for the Visual Crossing Weather API
api_key = os.getenv('API_KEY')
base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

# Secret key for session management
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=10)

# Helper function to load models
def load_saved_model(model_path):
    with open(model_path, 'rb') as f:
        model = joblib.load(f)
    return model

@app.route('/')
def home():
    if 'loggedin' in session:
        print(f"User logged in: {session['email']}")  # Debug log
        return render_template('index.html', email=session['email'])
    print("User not logged in, redirecting to login")  # Debug log
    return redirect('/login')

# Firebase Authentication routes
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            # Save additional user details in Firebase Realtime Database
            ref = db.reference('users')
            ref.child(user.uid).set({
                'email': email,
                'status': 'pending'
            })
            flash('Signup successful! Your request has been sent to the admin for approval.', 'success')
            return redirect('/login')
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.get_user_by_email(email)
            print(f"User found: {user.uid}")  # Debug log
            # Check user status in Firebase Realtime Database
            ref = db.reference('users')
            user_status = ref.child(user.uid).child('status').get()
            print(f"User status: {user_status}")  # Debug log
            if user_status == 'approved':
                session.permanent = True
                session['loggedin'] = True
                session['id'] = user.uid
                session['email'] = email
                flash('Login successful!', 'success')
                return redirect('/')  # Redirect to home page after login
            else:
                flash('Your account is pending approval by the admin.', 'danger')
        except Exception as e:
            print(f"Error: {e}")  # Debug log
            flash(f"Error: {e}", 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/login')

@app.before_request
def session_timeout():
    session.modified = True

@app.route('/model', methods=['GET', 'POST'])
def model():
    if 'loggedin' not in session:
        print("User not logged in, redirecting to login")  # Debug log
        flash('Please log in to access this page.', 'danger')
        return redirect('/login')
    
    print(f"User logged in: {session['email']}")  # Debug log
    list_pre = None
    graph = None
    if request.method == "POST":
        date = request.form.get('date')
        model_type = request.form.get('model_type')  # Get selected model type
        location = "new delhi"

        if model_type == "daily":
            model_path = DAILY_MODEL_PATH
            prediction_results = predict_daily_demand(location, date, model_path)
        elif model_type == "hourly":
            model_path = HOURLY_MODEL_PATH
            prediction_results = predict_hourly_demand(location, date, model_path)
        elif model_type == "5min":
            model_path = MIN5_MODEL_PATH
            prediction_results = predict_5min_demand(location, date, model_path)
        else:
            flash('Invalid model type selected.', 'danger')
            return redirect('/model')

        if prediction_results is not None:
            list_pre = prediction_results.values.tolist()
            df = pd.DataFrame(prediction_results)

            plt.figure(figsize=(10, 6))
            if model_type == "daily":
                plt.bar(df['Date'], df['Predicted Demand (MW)'], color='b', label='Predicted Demand (MW)')
                plt.title(f'Predicted Electricity Demand for {location} on {date}')
                plt.xlabel('Date')
            elif model_type == "hourly":
                plt.plot(df['DateTime'], df['Predicted Demand (MW)'], marker='o', color='b', label='Predicted Demand (MW)')
                plt.title(f'Predicted Electricity Demand for {location} on {date} (24-Hour)')
                plt.xlabel('Time')
            elif model_type == "5min":
                plt.plot(df['DateTime'], df['Predicted Demand (MW)'], marker='o', color='b', label='Predicted Demand (MW)')
                plt.title(f'Predicted Electricity Demand for {location} on {date} (5-Minute Interval)')
                plt.xlabel('Time')
            plt.ylabel('Predicted Demand (MW)')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            graph = base64.b64encode(img.getvalue()).decode()
            plt.close()

    return render_template('model.html', email=session['email'], prediction=list_pre, graph=graph)

# Model-specific prediction functions
def predict_daily_demand(location, date, model_path):
    def fetch_daily_weather_data(location, date):
        params = {"unitGroup": "metric", "key": api_key, "contentType": "json"}
        url = f"{base_url}/{location}/{date}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "days" in data:
                day_data = data["days"][0]
                return {
                    "Temperature": day_data["temp"],
                    "Humidity": day_data["humidity"],
                    "Wind_speed": day_data["windspeed"],
                    "Conditions": day_data["conditions"]
                }
        return None

    def prepare_sarimax_data(weather_data):
        df = pd.DataFrame([weather_data])
        df['Season'] = np.where(df['Temperature'] <= 15, 'Winter', 
                                np.where(df['Temperature'] <= 30, 'Summer', 'Hot'))
        season_mapping = {'Winter': 0, 'Summer': 1, 'Hot': 2}
        df['Season'] = df['Season'].map(season_mapping)
        scaler = MinMaxScaler()
        df[['Humidity', 'Temperature', 'Wind_speed', 'Season']] = scaler.fit_transform(
            df[['Humidity', 'Temperature', 'Wind_speed', 'Season']])
        return df[['Temperature', 'Humidity', 'Wind_speed', 'Season']]

    weather_data = fetch_daily_weather_data(location, date)
    if weather_data:
        future_exog = prepare_sarimax_data(weather_data)
        model_fit = load_saved_model(model_path)
        future_prediction = model_fit.forecast(steps=1, exog=future_exog)
        return pd.DataFrame({
            'Date': [date],
            'Predicted Demand (MW)': [future_prediction.iloc[0] if not future_prediction.empty else None]
        })
    return None

def predict_hourly_demand(location, date, model_path):
    def fetch_hourly_weather_data(location, date):
        params = {"unitGroup": "metric", "key": api_key, "contentType": "json"}
        url = f"{base_url}/{location}/{date}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "days" in data:
                day_data = data["days"][0]
                hourly_data = day_data.get("hours", [])
                hours, temperatures, humidities, windspeeds, conditions = [], [], [], [], []
                for hour in hourly_data:
                    hours.append(hour["datetime"])
                    temperatures.append(hour["temp"])
                    humidities.append(hour["humidity"])
                    windspeeds.append(hour["windspeed"])
                    conditions.append(hour["conditions"])
                return np.array([hours, temperatures, humidities, windspeeds, conditions]).T
        return None

    def prepare_sarimax_data(df):
        if 'Date' not in df.columns:
            df['Date'] = pd.to_datetime(df.index)
        if 'Weekday' not in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Weekday'] = df['Date'].dt.dayofweek
        if 'Season' not in df.columns:
            df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
            df['Season'] = np.where(df['Temperature'] <= 15, 'Light Winter', 
                                    np.where(df['Temperature'] <= 30, 'Light Summer', 'Heavy Summer'))
        season_mapping = {'Light Winter': 0, 'Heavy Winter': 1, 'Light Summer': 2, 'Heavy Summer': 3,
                          'Light Rainy': 4, 'Rainy': 5, 'Autumn': 6}
        df['Season'] = df['Season'].map(season_mapping).fillna(-1)
        scaler = MinMaxScaler()
        df[['Humidity', 'Temperature', 'Wind_speed', 'Season']] = scaler.fit_transform(
            df[['Humidity', 'Temperature', 'Wind_speed', 'Season']])
        return df

    weather_array = fetch_hourly_weather_data(location, date)
    if weather_array is not None:
        future_weather_df = pd.DataFrame(weather_array, columns=["Hour", "Temperature", "Humidity", "Wind_speed", "Conditions"])
        future_weather_df = prepare_sarimax_data(future_weather_df)
        future_exog = future_weather_df[['Temperature', 'Humidity', 'Wind_speed', 'Season']]
        model_fit = load_saved_model(model_path)
        future_predictions = model_fit.predict(start=len(future_weather_df), end=len(future_weather_df) + 23, exog=future_exog)
        date_time_index = pd.date_range(start=f'{date} 00:00:00', periods=24, freq='H')
        return pd.DataFrame({
            'DateTime': date_time_index,
            'Predicted Demand (MW)': future_predictions
        })
    return None

def predict_5min_demand(location, date, model_path):
    def fetch_5min_weather_data(location, date):
        params = {"unitGroup": "metric", "key": api_key, "contentType": "json"}
        url = f"{base_url}/{location}/{date}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if "days" in data:
                day_data = data["days"][0]
                min5_data = day_data.get("hours", [])
                times, temperatures, humidities, season = [], [], [], []
                for hour in min5_data:
                    times.append(hour["datetime"])
                    temperatures.append(hour["temp"])
                    humidities.append(hour["humidity"])
                    season_value = hour.get("season") or "Unknown"
                    season.append(season_value)
                return np.array([times, temperatures, humidities, season]).T
        return None

    def prepare_5min_sarimax_data(df):
        if 'Date' not in df.columns:
            df['Date'] = pd.to_datetime(df.index)
        if 'Season' not in df.columns:
            df['Temperature'] = pd.to_numeric(df['Temperature'], errors='coerce')
            df['Season'] = np.where(df['Temperature'] <= 15, 'Winter', 
                                    np.where(df['Temperature'] <= 30, 'Summer'))
        season_mapping = {'Winter': 0, 'Summer': 1, 'Rainy': 2, 'Autumn': 3}
        df['Season'] = df['Season'].map(season_mapping).fillna(-1)
        scaler = MinMaxScaler()
        df[['Humidity', 'Temperature', 'Season']] = scaler.fit_transform(
            df[['Humidity', 'Temperature', 'Season']])
        return df

    weather_array = fetch_5min_weather_data(location, date)
    if weather_array is not None:
        future_weather_df = pd.DataFrame(weather_array, columns=["Time", "Temperature", "Humidity", "Season"])
        future_weather_df = prepare_5min_sarimax_data(future_weather_df)
        future_exog = future_weather_df[['Temperature', 'Humidity', 'Season']]
        model_fit = load_saved_model(model_path)
        future_predictions = model_fit.predict(start=len(future_weather_df), end=len(future_weather_df) + 287, exog=future_exog)
        time_index = pd.date_range(start=f'{date} 00:00:00', periods=288, freq='5T')
        return pd.DataFrame({
            'DateTime': time_index,
            'Predicted Demand (MW)': future_predictions
        })
    return None


@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    user_name = data.get('name')
    user_email = data.get('email')  # This is the email entered by the user
    user_message = data.get('message')

    receiver_email = os.getenv('CONTACT_RECEIVER_EMAIL')
    password = os.getenv('CONTACT_EMAIL_APP_PASSWORD')  # Gmail App Password from .env

    subject = "New Contact Form Submission"
    
    # Create email message
    msg = MIMEMultipart()
    msg["From"] = receiver_email  # Your email (since only authenticated emails can send)
    msg["To"] = receiver_email  # You receive the email
    msg["Subject"] = subject
    msg["Reply-To"] = user_email  # This makes replying easier

    # Email body
    body = f"Name: {user_name}\nEmail: {user_email}\nMessage: {user_message}"
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to Gmail SMTP Server
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(receiver_email, password)
        server.sendmail(receiver_email, receiver_email, msg.as_string())
        server.quit()
        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error sending message: {str(e)}"}), 500


# Additional routes
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/welcome-section')
def welcomesection():
    return render_template('index.html#welcome-section')

@app.route('/about')
def about():
    return render_template('index.html#about')

@app.route('/team')
def team():
    return render_template('index.html#team')

@app.route('/contact')
def contact():
    return render_template('index.html#contact')

if __name__ == '__main__':
    app.run(debug=True, port=8080)
