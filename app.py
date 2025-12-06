from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import random
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import speech_recognition as sr  # Missing import for speech recognition

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



# Create Database Model
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form['email']
        phone = request.form['phone']

        if password != confirm_password:
            flash("Passwords do not match!", 'danger')
            return redirect(url_for('register'))

        candidate = Candidate.query.filter_by(name=name).first()
        if candidate:
            flash("Username already exists!", 'danger')
            return redirect(url_for('register'))

        new_candidate = Candidate(name=name, password=password, email=email, phone=phone)
        db.session.add(new_candidate)
        db.session.commit()
        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    password = request.form['password']
    candidate = Candidate.query.filter_by(name=name).first()

    if candidate and candidate.password == password:
        session['candidate_id'] = candidate.id
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid credentials!", 'danger')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'candidate_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/feedback')
def feedback():
    # Generate mock feedback data
    data = {'high': 60, 'moderate': 30, 'poor': 10}
    
    # Create a pie chart for feedback
    labels = data.keys()
    sizes = data.values()
    plt.figure(figsize=(6,6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Save chart to a BytesIO object and encode as base64 string to send to client
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.read()).decode('utf-8')
    plt.close()

    return render_template('feedback.html', img_data=img_base64)

@app.route('/generate_question', methods=['GET'])
def generate_question():
    questions = ["What is your greatest strength?", "Tell me about a challenge you've faced.", "Why should we hire you?"]
    question = random.choice(questions)
    return question

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    # Initialize recognizer class (for recognizing speech)
    recognizer = sr.Recognizer()
    
    try:
        # Using the Microphone as source for listening
        with sr.Microphone() as source:
            print("Listening for answer...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        
        # Recognizing the speech using Google Web API
        answer = recognizer.recognize_google(audio)
        print("You said: " + answer)
        return answer  # Return the text to the frontend
    except sr.UnknownValueError:
        return "Sorry, I didn't catch that."
    except sr.RequestError as e:
        return f"Error with speech service: {e}"
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from catboost import CatBoostClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from io import BytesIO
import base64

@app.route('/confidence_feedback', methods=['GET'])
def confidence_feedback():
    # Generate mock feedback data
    


    # Step 1: Generate some dummy data for feedback categories
    np.random.seed(42)
    
    # Feature columns (e.g., 'age', 'satisfaction_level', 'response_time')
    n_samples = 500
    data = {
        'age': np.random.randint(18, 65, size=n_samples),
        'satisfaction_level': np.random.uniform(1, 5, size=n_samples),
        'response_time': np.random.uniform(5, 30, size=n_samples)
    }
    
    # Random target labels ('high', 'moderate', 'poor')
    feedback_labels = np.random.choice(['high', 'moderate', 'poor'], size=n_samples, p=[0.6, 0.3, 0.1])
    
    df = pd.DataFrame(data)
    df['feedback'] = feedback_labels
    
    # Step 2: Preprocess data and split into train/test sets
    X = df[['age', 'satisfaction_level', 'response_time']]
    y = df['feedback']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Step 3: Initialize and train the CatBoost model
    model = CatBoostClassifier(iterations=1000, learning_rate=0.1, depth=6, cat_features=[], verbose=200)
    model.fit(X_train, y_train)
    
    # Step 4: Make predictions and evaluate the model
    y_pred = model.predict(X_test)
    
    # Model evaluation
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Accuracy: {accuracy:.4f}')
    print('Classification Report:')
    print(classification_report(y_test, y_pred))
    
    # Step 5: Generate a pie chart for feedback distribution
    feedback_counts = df['feedback'].value_counts()
    
    labels = feedback_counts.index
    sizes = feedback_counts.values
    
    # Plotting the pie chart
    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Save chart to a BytesIO object and encode as base64 string to send to client
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    img_base64 = base64.b64encode(img.read()).decode('utf-8')
    plt.close()
    
    # Output the base64 string for the image
    print("Base64 image data:")
    print(img_base64[:100])  # Print the first 100 characters of the base64 data for reference
    



    return render_template('feedback.html', img_data=img_base64)

if __name__ == '__main__':
    app.run(debug=True)
