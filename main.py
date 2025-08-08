from flask import Flask, request, render_template, jsonify, redirect, url_for, session, flash
import numpy as np
import pandas as pd
import pickle
import json
import os
import datetime
import uuid
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SECRET_KEY'] = '2181'  # This replaces the existing app.secret_key line

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# File to store user credentials
USER_FILE = "users.json"
USER_DETAILS_FILE = "user_details.json"
DOCTOR_FILE = "doctors.json"
DOCTOR_CREDENTIALS_FILE = "doctor_credentials.json"
APPOINTMENT_FILE = "appointments.json"
MEDICATION_FILE = "medications.json"  # New file for medications
CHAT_HISTORY_FILE = "chat_history.json"  # For storing AI assistant chat history
NEWSLETTER_FILE = "newsletter_emails.json"  # For storing newsletter email subscriptions


def load_users():
    if not os.path.exists(USER_FILE):  # Check if file exists
        return {}  # Return empty dictionary if file is missing
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}  # If file is corrupted, return empty dictionary


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load_user_details():
    if not os.path.exists(USER_DETAILS_FILE):
        return {}
    try:
        with open(USER_DETAILS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_user_details(user_details):
    with open(USER_DETAILS_FILE, "w") as f:
        json.dump(user_details, f, indent=4)


# Helper functions for doctor data
def load_doctors():
    if not os.path.exists(DOCTOR_FILE):
        return []
    try:
        with open(DOCTOR_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_doctors(doctors):
    with open(DOCTOR_FILE, "w") as f:
        json.dump(doctors, f, indent=4)


def get_doctor_by_email(email):
    doctors = load_doctors()
    for doctor in doctors:
        if doctor.get('email') == email:
            return doctor
    return None


def load_doctor_credentials():
    if not os.path.exists(DOCTOR_CREDENTIALS_FILE):
        return {}
    try:
        with open(DOCTOR_CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_doctor_credentials(credentials):
    with open(DOCTOR_CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=4)


# Helper functions for appointments
def load_appointments():
    if not os.path.exists(APPOINTMENT_FILE):
        return []
    try:
        with open(APPOINTMENT_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_appointments(appointments):
    with open(APPOINTMENT_FILE, "w") as f:
        json.dump(appointments, f, indent=4)


# Helper functions for medications
def load_medications():
    if not os.path.exists(MEDICATION_FILE):
        return {}
    try:
        with open(MEDICATION_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_medications(medications):
    with open(MEDICATION_FILE, "w") as f:
        json.dump(medications, f, indent=4)


# Helper functions for chat history
def load_chat_history():
    if not os.path.exists(CHAT_HISTORY_FILE):
        return {}
    try:
        with open(CHAT_HISTORY_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_chat_history(chat_history):
    with open(CHAT_HISTORY_FILE, "w") as f:
        json.dump(chat_history, f, indent=4)


def load_newsletter_emails():
    if not os.path.exists(NEWSLETTER_FILE):
        return []
    try:
        with open(NEWSLETTER_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_newsletter_emails(emails):
    with open(NEWSLETTER_FILE, "w") as f:
        json.dump(emails, f, indent=4)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Loading dataset
sym_des = pd.read_csv("datasets/symtoms_df.csv")
precautions = pd.read_csv("datasets/precautions_df.csv")
workout = pd.read_csv("datasets/workout_df.csv")
description = pd.read_csv("datasets/description.csv")
medications = pd.read_csv('datasets/medications.csv')
diets = pd.read_csv("datasets/diets.csv")

# Loading model
svc = pickle.load(open('models/svc.pkl', 'rb'))


# Custom and helping functions
# 1. Helper functions
def helper(dis):
    desc = description[description['Disease'] == dis]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions[precautions['Disease'] == dis][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications[medications['Disease'] == dis]['Medication']
    med = [med for med in med.values]

    die = diets[diets['Disease'] == dis]['Diet']
    die = [die for die in die.values]

    wrkout = workout[workout['disease'] == dis]['workout']

    return desc, pre, med, die, wrkout


symptoms_dict = {'itching': 0, 'skin_rash': 1, 'nodal_skin_eruptions': 2, 'continuous_sneezing': 3, 'shivering': 4,
                 'chills': 5, 'joint_pain': 6, 'stomach_pain': 7, 'acidity': 8, 'ulcers_on_tongue': 9,
                 'muscle_wasting': 10, 'vomiting': 11, 'burning_micturition': 12, 'spotting_ urination': 13,
                 'fatigue': 14, 'weight_gain': 15, 'anxiety': 16, 'cold_hands_and_feets': 17, 'mood_swings': 18,
                 'weight_loss': 19, 'restlessness': 20, 'lethargy': 21, 'patches_in_throat': 22,
                 'irregular_sugar_level': 23, 'cough': 24, 'high_fever': 25, 'sunken_eyes': 26, 'breathlessness': 27,
                 'sweating': 28, 'dehydration': 29, 'indigestion': 30, 'headache': 31, 'yellowish_skin': 32,
                 'dark_urine': 33, 'nausea': 34, 'loss_of_appetite': 35, 'pain_behind_the_eyes': 36, 'back_pain': 37,
                 'constipation': 38, 'abdominal_pain': 39, 'diarrhoea': 40, 'mild_fever': 41, 'yellow_urine': 42,
                 'yellowing_of_eyes': 43, 'acute_liver_failure': 44, 'fluid_overload': 45, 'swelling_of_stomach': 46,
                 'swelled_lymph_nodes': 47, 'malaise': 48, 'blurred_and_distorted_vision': 49, 'phlegm': 50,
                 'throat_irritation': 51, 'redness_of_eyes': 52, 'sinus_pressure': 53, 'runny_nose': 54,
                 'congestion': 55, 'chest_pain': 56, 'weakness_in_limbs': 57, 'fast_heart_rate': 58,
                 'pain_during_bowel_movements': 59, 'pain_in_anal_region': 60, 'bloody_stool': 61,
                 'irritation_in_anus': 62, 'neck_pain': 63, 'dizziness': 64, 'cramps': 65, 'bruising': 66,
                 'obesity': 67, 'swollen_legs': 68, 'swollen_blood_vessels': 69, 'puffy_face_and_eyes': 70,
                 'enlarged_thyroid': 71, 'brittle_nails': 72, 'swollen_extremeties': 73, 'excessive_hunger': 74,
                 'extra_marital_contacts': 75, 'drying_and_tingling_lips': 76, 'slurred_speech': 77, 'knee_pain': 78,
                 'hip_joint_pain': 79, 'muscle_weakness': 80, 'stiff_neck': 81, 'swelling_joints': 82,
                 'movement_stiffness': 83, 'spinning_movements': 84, 'loss_of_balance': 85, 'unsteadiness': 86,
                 'weakness_of_one_body_side': 87, 'loss_of_smell': 88, 'bladder_discomfort': 89,
                 'foul_smell_of urine': 90, 'continuous_feel_of_urine': 91, 'passage_of_gases': 92,
                 'internal_itching': 93, 'toxic_look_(typhos)': 94, 'depression': 95, 'irritability': 96,
                 'muscle_pain': 97, 'altered_sensorium': 98, 'red_spots_over_body': 99, 'belly_pain': 100,
                 'abnormal_menstruation': 101, 'dischromic _patches': 102, 'watering_from_eyes': 103,
                 'increased_appetite': 104, 'polyuria': 105, 'family_history': 106, 'mucoid_sputum': 107,
                 'rusty_sputum': 108, 'lack_of_concentration': 109, 'visual_disturbances': 110,
                 'receiving_blood_transfusion': 111, 'receiving_unsterile_injections': 112, 'coma': 113,
                 'stomach_bleeding': 114, 'distention_of_abdomen': 115, 'history_of_alcohol_consumption': 116,
                 'fluid_overload.1': 117, 'blood_in_sputum': 118, 'prominent_veins_on_calf': 119, 'palpitations': 120,
                 'painful_walking': 121, 'pus_filled_pimples': 122, 'blackheads': 123, 'scurring': 124,
                 'skin_peeling': 125, 'silver_like_dusting': 126, 'small_dents_in_nails': 127,
                 'inflammatory_nails': 128, 'blister': 129, 'red_sore_around_nose': 130, 'yellow_crust_ooze': 131}

diseases_list = {15: 'Fungal infection', 4: 'Allergy', 16: 'GERD', 9: 'Chronic cholestasis', 14: 'Drug Reaction',
                 33: 'Peptic ulcer diseae', 1: 'AIDS', 12: 'Diabetes ', 17: 'Gastroenteritis', 6: 'Bronchial Asthma',
                 23: 'Hypertension ', 30: 'Migraine', 7: 'Cervical spondylosis', 32: 'Paralysis (brain hemorrhage)',
                 28: 'Jaundice', 29: 'Malaria', 8: 'Chicken pox', 11: 'Dengue', 37: 'Typhoid', 40: 'hepatitis A',
                 19: 'Hepatitis B', 20: 'Hepatitis C', 21: 'Hepatitis D', 22: 'Hepatitis E', 3: 'Alcoholic hepatitis',
                 36: 'Tuberculosis', 10: 'Common Cold', 34: 'Pneumonia', 13: 'Dimorphic hemmorhoids(piles)',
                 18: 'Heart attack', 39: 'Varicose veins', 26: 'Hypothyroidism', 24: 'Hyperthyroidism',
                 25: 'Hypoglycemia', 31: 'Osteoarthristis', 5: 'Arthritis',
                 0: '(vertigo) Paroymsal  Positional Vertigo', 2: 'Acne', 38: 'Urinary tract infection',
                 35: 'Psoriasis', 27: 'Impetigo'}


# 2. Model Prediction function
def get_predicted_value(patient_symptoms):
    input_vector = np.zeros(len(symptoms_dict))
    for item in patient_symptoms:
        input_vector[symptoms_dict[item]] = 1
    return diseases_list[svc.predict([input_vector])[0]]


# Add a new function to get the profile picture URL
def get_profile_picture(email):
    user_details = load_user_details()
    if email in user_details and 'profile_pic' in user_details[email]:
        return user_details[email]['profile_pic']
    return None


# Add a function to get doctor profile picture
def get_doctor_profile_picture(email):
    doctors = load_doctors()
    for doctor in doctors:
        if doctor.get('email') == email and 'profile_pic' in doctor:
            return doctor['profile_pic']
    return None


# Modify the existing context processor to also include doctor profile pictures
@app.context_processor
def inject_profile_picture():
    if 'user' in session:
        profile_pic = get_profile_picture(session['user'])
        return {'profile_picture': profile_pic}
    elif 'doctor' in session:
        profile_pic = get_doctor_profile_picture(session['doctor'])
        return {'profile_picture': profile_pic}
    return {'profile_picture': None}


# AI Assistant functions
def get_ai_response(query, user_email=None):
    """
    Generate AI response based on user query
    This is a simplified version - in a real app, you'd integrate with an AI service
    """
    # Check if query is about symptoms
    if re.search(r'(symptom|feeling|pain|ache|sick|ill)', query, re.IGNORECASE):
        return "It sounds like you're describing some symptoms. You can use our symptom checker on the home page to get a preliminary diagnosis. Would you like me to guide you there?"

    # Check if query is about appointments
    elif re.search(r'(appointment|schedule|book|doctor|visit)', query, re.IGNORECASE):
        return "I can help you schedule an appointment. You can go to the 'New Appointment' page to see available doctors and time slots. Would you like me to help you with that?"

    # Check if query is about medications
    elif re.search(r'(medication|medicine|drug|pill|prescription)', query, re.IGNORECASE):
        return "If you need to track your medications, you can use our medication management feature. Would you like me to show you how to add a new medication?"

    # Check if query is about profile
    elif re.search(r'(profile|account|settings|password)', query, re.IGNORECASE):
        return "You can update your profile information or account settings from the profile page. Would you like me to direct you there?"

    # Default response
    else:
        return "I'm your healthcare assistant. I can help you with symptom checking, appointment scheduling, medication tracking, and more. How can I assist you today?"


def save_user_chat(user_email, query, response):
    """Save chat history for a user"""
    chat_history = load_chat_history()

    if user_email not in chat_history:
        chat_history[user_email] = []

    chat_history[user_email].append({
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "response": response
    })

    # Keep only the last 50 messages
    if len(chat_history[user_email]) > 50:
        chat_history[user_email] = chat_history[user_email][-50:]

    save_chat_history(chat_history)


def get_user_chat_history(user_email, limit=10):
    """Get recent chat history for a user"""
    chat_history = load_chat_history()

    if user_email in chat_history:
        return chat_history[user_email][-limit:]

    return []


# Creating routes

# Landing Page
@app.route('/')
def landing():
    return render_template('landing.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()

        if email in users and users[email] == password:  # Check if user exists
            session['user'] = email
            session['login_success'] = True  # Set a session variable for success message
            return redirect(url_for('index'))  # Redirect to dashboard
        else:
            return render_template('login.html', error="Invalid email or password. Please try again.")
    return render_template('login.html')


# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        phone = request.form['phone']
        nid_birth_certificate = request.form['nid_birth_certificate']  # New field

        # Get additional fields from the form
        age = request.form.get('age', '')
        dob = request.form.get('dob', '')
        gender = request.form.get('gender', '')
        blood_group = request.form.get('blood_group', '')
        address = request.form.get('address', '')
        emergency_contact = request.form.get('emergency_contact', '')  # New field

        if password != confirm_password:
            return "Passwords do not match!", 400

        users = load_users()
        user_details = load_user_details()

        # Check if email already exists
        if email in users:
            return "User already exists!", 400

        # Check if NID/Birth Certificate Number already exists
        for user_email, details in user_details.items():
            if details.get('nid_birth_certificate') == nid_birth_certificate:
                return "NID/Birth Certificate Number already registered!", 400

        # Save user credentials
        users[email] = password
        save_users(users)

        # Save user details
        user_details[email] = {
            "name": name,
            "phone": phone,
            "nid_birth_certificate": nid_birth_certificate,  # New field
            # Add the additional fields
            "age": age,
            "dob": dob,
            "gender": gender,
            "blood_group": blood_group,
            "address": address,
            "emergency_contact": emergency_contact,  # New field
            "medications": []  # Initialize medications list
        }
        save_user_details(user_details)

        # Flask handles the redirect after signup
        return redirect(url_for('login'))

    return render_template('signup.html')  # Ensures signup form loads correctly


# Logout Route
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# Profile Page
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_details = load_user_details()
    email = session['user']

    if email not in user_details:
        user_details[email] = {
            "name": "User",
            "phone": "Not provided"
        }
        save_user_details(user_details)

    return render_template('my-profile.html', user_details=user_details[email])


# Update Profile
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    name = request.form['name']
    phone = request.form['phone']

    # Get additional fields from the form
    age = request.form.get('age', '')
    dob = request.form.get('dob', '')
    gender = request.form.get('gender', '')
    blood_group = request.form.get('blood_group', '')
    address = request.form.get('address', '')
    emergency_contact = request.form.get('emergency_contact', '')  # New field

    user_details = load_user_details()

    # Process profile picture if uploaded
    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        if profile_pic and profile_pic.filename != '' and allowed_file(profile_pic.filename):
            filename = secure_filename(f"{email}_profile_{profile_pic.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_pic.save(file_path)

            # Update user record with file path
            if email in user_details:
                user_details[email]['profile_pic'] = file_path

    if email in user_details:
        user_details[email]['name'] = name
        user_details[email]['phone'] = phone
        # Update additional fields
        user_details[email]['age'] = age
        user_details[email]['dob'] = dob
        user_details[email]['gender'] = gender
        user_details[email]['blood_group'] = blood_group
        user_details[email]['address'] = address
        user_details[email]['emergency_contact'] = emergency_contact  # New field
        # Note: We don't update nid_birth_certificate as it should be non-editable
    else:
        # This case should not happen normally, but handling it just in case
        return redirect(url_for('profile'))

    save_user_details(user_details)
    return redirect(url_for('profile'))


# Settings Page
@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    user_details = load_user_details()

    if email not in user_details:
        user_details[email] = {
            "name": "User",
            "phone": "Not provided"
        }
        save_user_details(user_details)

    return render_template('settings.html', user_details=user_details[email])


# Update Email
@app.route('/update_email', methods=['POST'])
def update_email():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_email = session['user']
    new_email = request.form['new_email']
    password = request.form['password']

    users = load_users()

    # Verify password
    if users.get(current_email) != password:
        return render_template('settings.html', message="Incorrect password", message_type="danger")

    # Check if new email already exists
    if new_email in users:
        return render_template('settings.html', message="Email already in use", message_type="danger")

    # Update email in users.json
    users[new_email] = users[current_email]
    del users[current_email]
    save_users(users)

    # Update email in user_details.json
    user_details = load_user_details()
    if current_email in user_details:
        user_details[new_email] = user_details[current_email]
        del user_details[current_email]
        save_user_details(user_details)

    # Update session
    session['user'] = new_email

    return render_template('settings.html', message="Email updated successfully", message_type="success")


# Update Password
@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    users = load_users()

    # Verify current password
    if users.get(email) != current_password:
        return render_template('settings.html', message="Incorrect current password", message_type="danger")

    # Check if new passwords match
    if new_password != confirm_password:
        return render_template('settings.html', message="New passwords do not match", message_type="danger")

    # Update password
    users[email] = new_password
    save_users(users)

    return render_template('settings.html', message="Password updated successfully", message_type="success")


# Index Page
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    login_success = False
    if 'login_success' in session:
        login_success = session.pop('login_success')  # Get and remove the flag

    email = session['user']
    user_details = load_user_details()

    if email not in user_details:
        user_details[email] = {
            "name": "User",
            "phone": "Not provided"
        }
        save_user_details(user_details)

    return render_template('index.html', login_success=login_success, user_details=user_details[email])


# Prediction Route
@app.route('/predict', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        print(symptoms)

        # Check if symptoms is empty or just "Symptoms"
        if not symptoms or symptoms == "Symptoms":
            flash("Please enter valid symptoms", "warning")
            return render_template('index.html', message="Please enter valid symptoms")

        # Split the symptoms and check if they are valid
        user_symptoms = [s.strip() for s in symptoms.split(',')]
        user_symptoms = [symptom.strip("[]' ") for symptom in user_symptoms]

        # Check if all symptoms are in the symptoms_dict
        invalid_symptoms = [symptom for symptom in user_symptoms if symptom not in symptoms_dict]

        if invalid_symptoms:
            flash(f"Invalid symptoms: {', '.join(invalid_symptoms)}. Please enter valid symptoms.", "warning")
            return render_template('index.html', message=f"Invalid symptoms: {', '.join(invalid_symptoms)}")

        # If all symptoms are valid, proceed with prediction
        try:
            predicted_disease = get_predicted_value(user_symptoms)
            dis_des, precautions, medications, rec_diet, workout = helper(predicted_disease)

            my_precautions = []
            for i in precautions[0]:
                my_precautions.append(i)

            # Store the symptoms and predicted disease in the user's medical history if logged in
            if 'user' in session:
                email = session['user']
                user_details = load_user_details()

                # Initialize medical_history if it doesn't exist
                if email in user_details:
                    if 'medical_history' not in user_details[email]:
                        user_details[email]['medical_history'] = []

                    # Add the current search to medical history
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_details[email]['medical_history'].append({
                        "date": timestamp,
                        "symptoms": symptoms,
                        "predicted_disease": predicted_disease
                    })

                    # Save the updated user details
                    save_user_details(user_details)

            return render_template('index.html', predicted_disease=predicted_disease, dis_des=dis_des,
                                   my_precautions=my_precautions, medications=medications, my_diet=rec_diet,
                                   workout=workout)

        except Exception as e:
            # If there's an error in prediction, show a friendly message
            print(f"Error in prediction: {str(e)}")
            flash("Unable to process these symptoms. Please try different symptoms or contact support.", "danger")
            return render_template('index.html', message="Error processing symptoms")

    return render_template('index.html')


# About Page
@app.route('/about')
def about():
    return render_template("about.html")


# Contact Page
@app.route('/contact')
def contact():
    return render_template("contact.html")


# Purchase Page
@app.route('/purchase')
def purchase():
    return render_template("purchase.html")


# Newsletter signup route
@app.route('/newsletter_signup', methods=['POST'])
def newsletter_signup():
    try:
        # Get email from form data
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
            
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({"success": False, "message": "Please enter a valid email address"}), 400
        
        # Load existing newsletter emails
        newsletter_emails = load_newsletter_emails()
        
        # Check if email already exists
        existing_emails = [entry['email'] for entry in newsletter_emails if isinstance(entry, dict)]
        if email in existing_emails:
            return jsonify({"success": False, "message": "This email is already subscribed to our newsletter"}), 400
        
        # Add new email subscription
        new_subscription = {
            "email": email,
            "subscribed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active",
            "source": "landing_page"
        }
        
        newsletter_emails.append(new_subscription)
        
        # Save updated newsletter emails
        save_newsletter_emails(newsletter_emails)
        
        return jsonify({
            "success": True, 
            "message": "Thank you for subscribing to our newsletter! You'll receive health tips and updates from PASMA."
        })
        
    except Exception as e:
        print(f"Error in newsletter signup: {str(e)}")
        return jsonify({"success": False, "message": "An error occurred. Please try again later."}), 500


# AI Assistant Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')

    # Get user email if logged in
    user_email = session.get('user', None)

    # Generate AI response
    response = get_ai_response(message, user_email)

    # Save chat history if user is logged in
    if user_email:
        save_user_chat(user_email, message, response)

    return jsonify({"response": response})


# Get chat history endpoint
@app.route('/get_chat_history', methods=['GET'])
def get_chat_history():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    user_email = session['user']
    limit = request.args.get('limit', 10, type=int)

    history = get_user_chat_history(user_email, limit)

    return jsonify({"success": True, "history": history})


# AI Assistant page
@app.route('/assistant')
def assistant():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session['user']
    user_details = load_user_details()

    if user_email not in user_details:
        return redirect(url_for('index'))

    # Get recent chat history
    chat_history = get_user_chat_history(user_email)

    return render_template('assistant.html', user_details=user_details[user_email], chat_history=chat_history)


# New Appointment Page
@app.route('/new-appointment')
def new_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    # Get doctors from doctors.json
    doctors_list = load_doctors()

    # Format doctors for display
    formatted_doctors = []
    for doctor in doctors_list:
        if doctor.get('specialization') and doctor.get('fee'):  # Only show doctors with complete profiles
            # Convert time slots to availability days
            availability = []
            for slot in doctor.get('timeSlots', []):
                if 'day' in slot:
                    availability.append(slot['day'])

            formatted_doctors.append({
                "id": doctor.get('id', ''),
                "name": doctor.get('name', ''),
                "specialty": doctor.get('specialization', ''),
                "experience": doctor.get('experience', '0'),
                "hospital": doctor.get('hospital', ''),
                "availability": availability,
                "fee": doctor.get('fee', '0'),
                "rating": 4,  # Default rating
                "profile_pic": doctor.get('profile_pic', None)  # Add profile picture
            })
    return render_template('new-appointment.html', doctors=formatted_doctors)


# Book Appointment
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    email = session['user']
    doctor_id = request.form['doctor_id']
    doctor_name = request.form['doctor_name']
    doctor_specialty = request.form['doctor_specialty']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    purpose = request.form['purpose']
    notes = request.form.get('notes', '')

    # Load user details
    user_details = load_user_details()

    # Initialize appointments list if it doesn't exist
    if email in user_details:
        if 'appointments' not in user_details[email]:
            user_details[email]['appointments'] = []
    else:
        user_details[email] = {
            "name": "User",
            "phone": "Not provided",
            "appointments": []
        }

    # Add the appointment
    appointment = {
        "id": str(len(user_details[email]['appointments']) + 1),
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "department": doctor_specialty,
        "date": appointment_date,
        "time": appointment_time,
        "purpose": purpose,
        "notes": notes,
        "status": "Upcoming",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    user_details[email]['appointments'].append(appointment)

    # Save user details
    save_user_details(user_details)

    # Also save to the appointments.json file for doctor access
    appointments = load_appointments()
    new_appointment = {
        "id": str(uuid.uuid4()),
        "patient_id": email,  # Using email as patient ID
        "patient_name": user_details[email].get('name', 'Patient'),
        "patient_email": email,
        "doctor_id": doctor_id,
        "doctor_name": doctor_name,
        "doctor_specialty": doctor_specialty,
        "date": appointment_date,
        "time": appointment_time,
        "purpose": purpose,
        "notes": notes,
        "status": "Upcoming",
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    appointments.append(new_appointment)
    save_appointments(appointments)

    # Redirect to profile page
    return redirect(url_for('profile'))


# Doctor Routes
@app.route('/doctor-login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        doctor_credentials = load_doctor_credentials()

        if email in doctor_credentials and doctor_credentials[email] == password:
            session['doctor'] = email
            session['doctor_email'] = email
            session['login_success'] = True
            return redirect(url_for('doctor_dashboard'))
        else:
            return render_template('doctor-login.html', error="Invalid credentials!")
    return render_template('doctor-login.html')


@app.route('/doctor-signup', methods=['GET', 'POST'])
def doctor_signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        gender = request.form['gender']
        phone = request.form['phone']
        age = request.form['age']
        dob = request.form['dob']
        license = request.form['license']
        nid = request.form['nid']  # Add this line to get NID/Birth Certificate Number

        if password != confirm_password:
            return render_template('doctor-signup.html', error="Passwords do not match!")

        doctor_credentials = load_doctor_credentials()
        doctors = load_doctors()

        # Check if email already exists
        if email in doctor_credentials:
            return render_template('doctor-signup.html', error="Email already exists!")

        # Check if license already exists
        for doctor in doctors:
            if doctor.get('license') == license:
                return render_template('doctor-signup.html', error="License number already registered!")

        # Check if NID/Birth Certificate Number already exists
        for doctor in doctors:
            if doctor.get('nid') == nid:
                return render_template('doctor-signup.html', error="NID/Birth Certificate Number already registered!")

        # Save doctor credentials
        doctor_credentials[email] = password
        save_doctor_credentials(doctor_credentials)

        # Create new doctor
        new_doctor = {
            "id": str(uuid.uuid4()),
            "name": name,
            "gender": gender,
            "email": email,
            "phone": phone,
            "age": age,
            "dob": dob,
            "license": license,
            "nid": nid,  # Add this line to store NID/Birth Certificate Number
            "specialization": "",
            "experience": "",
            "fee": "",
            "hospital": "",
            "bio": "",
            "languages": "",
            "address": "",
            "timeSlots": [],
            "createdAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        doctors.append(new_doctor)
        save_doctors(doctors)

        return redirect(url_for('doctor_login'))

    return render_template('doctor-signup.html')


@app.route('/doctor-logout')
def doctor_logout():
    session.pop('doctor', None)
    session.pop('doctor_email', None)
    return redirect(url_for('doctor_login'))


@app.route('/doctor-profile')
def doctor_profile():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    doctors = load_doctors()

    doctor_details = None
    for doctor in doctors:
        if doctor['email'] == email:
            doctor_details = doctor
            break

    if not doctor_details:
        # This should not happen normally, but handling it just in case
        return redirect(url_for('doctor_login'))

    # Get appointments for this doctor
    appointments = load_appointments()
    doctor_appointments = [
        appointment for appointment in appointments
        if appointment.get('doctor_id') == doctor_details.get('id')
    ]

    return render_template('doctor-profile.html', doctor_details=doctor_details, appointments=doctor_appointments)


@app.route('/doctor-settings')
def doctor_settings():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))
    return render_template('doctor-settings.html')


@app.route('/doctor-dashboard')
def doctor_dashboard():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    doctors = load_doctors()

    doctor_details = None
    for doctor in doctors:
        if doctor['email'] == email:
            doctor_details = doctor
            break

    if not doctor_details:
        return redirect(url_for('doctor_login'))

    # Get current date
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")

    # Get appointments for this doctor
    appointments = load_appointments()
    doctor_appointments = [
        appointment for appointment in appointments
        if appointment.get('doctor_id') == doctor_details.get('id')
    ]

    # Get today's appointments
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_appointments = [
        appointment for appointment in doctor_appointments
        if appointment.get('date') == today
    ]

    # Calculate statistics
    unique_patients = set(appointment.get('patient_email') for appointment in doctor_appointments)
    upcoming_appointments = len([a for a in doctor_appointments if a.get('status') == 'Upcoming'])
    completed_appointments = len([a for a in doctor_appointments if a.get('status') == 'Completed'])

    stats = {
        'today_appointments': len(today_appointments),
        'total_patients': len(unique_patients),
        'upcoming_appointments': upcoming_appointments,
        'completed_appointments': completed_appointments
    }

    # Generate recent activities (in a real app, this would come from a database)
    recent_activities = []

    # Add appointment activities
    for appointment in sorted(doctor_appointments, key=lambda x: x.get('created_at', ''), reverse=True)[:3]:
        if appointment.get('status') == 'Upcoming':
            recent_activities.append({
                'icon': 'fas fa-calendar-plus',
                'title': f"New appointment with {appointment.get('patient_name')}",
                'time': datetime.datetime.strptime(appointment.get('created_at', ''), "%Y-%m-%d %H:%M:%S").strftime(
                    "%b %d, %Y at %I:%M %p")
            })
        elif appointment.get('status') == 'Completed':
            recent_activities.append({
                'icon': 'fas fa-check-circle',
                'title': f"Completed appointment with {appointment.get('patient_name')}",
                'time': datetime.datetime.strptime(appointment.get('updated_at', appointment.get('created_at', '')),
                                                   "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y at %I:%M %p")
            })

    # Add profile update activity if available
    if doctor_details.get('updatedAt'):
        recent_activities.append({
            'icon': 'fas fa-user-edit',
            'title': "Updated your profile information",
            'time': datetime.datetime.strptime(doctor_details.get('updatedAt'), "%Y-%m-%d %H:%M:%S").strftime(
                "%b %d, %Y at %I:%M %p")
        })

    # Sort activities by time (most recent first) and limit to 5
    recent_activities = sorted(recent_activities,
                               key=lambda x: datetime.datetime.strptime(x['time'], "%b %d, %Y at %I:%M %p"),
                               reverse=True)[:5]

    return render_template('doctor-dashboard.html',
                           doctor_details=doctor_details,
                           current_date=current_date,
                           stats=stats,
                           today_appointments=today_appointments,
                           recent_activities=recent_activities)


# In the doctor_appointments route, modify the function to include patient profile pictures
@app.route('/doctor-appointments')
def doctor_appointments():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    doctors = load_doctors()

    doctor_details = None
    for doctor in doctors:
        if doctor['email'] == email:
            doctor_details = doctor
            break

    if not doctor_details:
        return redirect(url_for('doctor_login'))

    # Get appointments for this doctor
    appointments = load_appointments()
    doctor_appointments = [
        appointment for appointment in appointments
        if appointment.get('doctor_id') == doctor_details.get('id')
    ]

    # Load patient details for the appointments
    user_details = load_user_details()

    # Add profile pictures to patient details
    for email, details in user_details.items():
        if 'profile_pic' not in details:
            details['profile_pic'] = None

    return render_template('doctor-appointments.html', appointments=doctor_appointments, patient_details=user_details)


@app.route('/update-appointment', methods=['POST'])
def update_appointment():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    # This route is now disabled - just redirect back to appointments page
    return redirect(url_for('doctor_appointments'))


@app.route('/update-appointment-status', methods=['POST'])
def update_appointment_status():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    appointment_id = request.form['appointment_id']
    status = request.form['status']

    # Update in appointments.json
    appointments = load_appointments()
    patient_email = None

    for appointment in appointments:
        if appointment['id'] == appointment_id:
            # Store patient email for updating their record
            patient_email = appointment['patient_email']

            # Update appointment status
            appointment['status'] = status
            appointment['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break

    save_appointments(appointments)

    # Update in patient's user_details.json if patient email is found
    if patient_email:
        user_details = load_user_details()

        if patient_email in user_details and 'appointments' in user_details[patient_email]:
            for patient_appointment in user_details[patient_email]['appointments']:
                # Match appointment by doctor, date and time
                if (patient_appointment.get('doctor_id') == appointments[0].get('doctor_id') and
                        patient_appointment.get('id') != appointment_id):
                    # Update the patient's appointment status
                    patient_appointment['status'] = status
                    patient_appointment['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break

            save_user_details(user_details)

    return redirect(url_for('doctor_appointments'))


@app.route('/update-doctor-profile', methods=['POST'])
def update_doctor_profile():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    name = request.form['name']
    gender = request.form['gender']
    phone = request.form['phone']
    age = request.form['age']
    dob = request.form['dob']

    doctors = load_doctors()

    for doctor in doctors:
        if doctor['email'] == email:
            doctor['name'] = name
            doctor['gender'] = gender
            doctor['phone'] = phone
            doctor['age'] = age
            doctor['dob'] = dob
            doctor['updatedAt'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break

    save_doctors(doctors)
    return redirect(url_for('doctor_profile'))


@app.route('/update-doctor-professional', methods=['POST'])
def update_doctor_professional():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    # Get specialization as a list and join with commas for storage
    specialization = request.form.getlist('specialization')
    specialization_str = ','.join(specialization)

    license = request.form['license']
    experience = request.form['experience']
    fee = request.form['fee']
    hospital = request.form['hospital']

    # Process time slots for all days of the week
    time_slots = request.form.getlist('timeSlots')
    formatted_slots = []

    # Process Monday slots
    if 'monday-morning' in time_slots or 'monday-afternoon' in time_slots:
        day_slots = {"day": "Monday", "slots": []}
        if 'monday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'monday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    # Process Tuesday slots
    if 'tuesday-morning' in time_slots or 'tuesday-afternoon' in time_slots:
        day_slots = {"day": "Tuesday", "slots": []}
        if 'tuesday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'tuesday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    # Process Wednesday slots
    if 'wednesday-morning' in time_slots or 'wednesday-afternoon' in time_slots:
        day_slots = {"day": "Wednesday", "slots": []}
        if 'wednesday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'wednesday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    # Process Thursday slots
    if 'thursday-morning' in time_slots or 'thursday-afternoon' in time_slots:
        day_slots = {"day": "Thursday", "slots": []}
        if 'thursday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'thursday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    # Process Friday slots
    if 'friday-morning' in time_slots or 'friday-afternoon' in time_slots:
        day_slots = {"day": "Friday", "slots": []}
        if 'friday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'friday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    # Process Saturday slots
    if 'saturday-morning' in time_slots or 'saturday-afternoon' in time_slots:
        day_slots = {"day": "Saturday", "slots": []}
        if 'saturday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'saturday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    # Process Sunday slots
    if 'sunday-morning' in time_slots or 'sunday-afternoon' in time_slots:
        day_slots = {"day": "Sunday", "slots": []}
        if 'sunday-morning' in time_slots:
            day_slots["slots"].append("09:00 AM - 12:00 PM")
        if 'sunday-afternoon' in time_slots:
            day_slots["slots"].append("02:00 PM - 05:00 PM")
        formatted_slots.append(day_slots)

    doctors = load_doctors()

    for doctor in doctors:
        if doctor['email'] == email:
            doctor['specialization'] = specialization_str
            doctor['license'] = license
            doctor['experience'] = experience
            doctor['fee'] = fee
            doctor['hospital'] = hospital
            doctor['timeSlots'] = formatted_slots
            doctor['updatedAt'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break

    save_doctors(doctors)
    return redirect(url_for('doctor_profile'))


@app.route('/update-doctor-additional', methods=['POST'])
def update_doctor_additional():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    bio = request.form['bio']
    # Get languages as a list and join with commas for storage
    languages = request.form.getlist('languages')
    languages_str = ','.join(languages)
    address = request.form['address']

    doctors = load_doctors()

    for doctor in doctors:
        if doctor['email'] == email:
            doctor['bio'] = bio
            doctor['languages'] = languages_str
            doctor['address'] = address
            doctor['updatedAt'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break

    save_doctors(doctors)
    return redirect(url_for('doctor_profile'))


@app.route('/upload-doctor-documents', methods=['POST'])
def upload_doctor_documents():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']

    # Create upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    # Process license document
    if 'license_doc' in request.files:
        license_file = request.files['license_doc']
        if license_file and license_file.filename != '' and allowed_file(license_file.filename):
            filename = secure_filename(f"{email}_license_{license_file.filename}")
            license_file.save(os.path.join(UPLOAD_FOLDER, filename))

            # Update doctor record with file path
            doctors = load_doctors()
            for doctor in doctors:
                if doctor['email'] == email:
                    doctor['license_doc'] = os.path.join(UPLOAD_FOLDER, filename)
                    break
            save_doctors(doctors)

    # Process profile picture
    if 'profile_pic' in request.files:
        profile_pic = request.files['profile_pic']
        if profile_pic and profile_pic.filename != '' and allowed_file(profile_pic.filename):
            filename = secure_filename(f"{email}_profile_{profile_pic.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            profile_pic.save(file_path)

            # Update doctor record with file path
            doctors = load_doctors()
            for doctor in doctors:
                if doctor['email'] == email:
                    doctor['profile_pic'] = file_path
                    break
            save_doctors(doctors)

    # Process ID document
    if 'id_doc' in request.files:
        id_file = request.files['id_doc']
        if id_file and id_file.filename != '' and allowed_file(id_file.filename):
            filename = secure_filename(f"{email}_id_{id_file.filename}")
            id_file.save(os.path.join(UPLOAD_FOLDER, filename))

            # Update doctor record with file path
            doctors = load_doctors()
            for doctor in doctors:
                if doctor['email'] == email:
                    doctor['id_doc'] = os.path.join(UPLOAD_FOLDER, filename)
                    break
            save_doctors(doctors)

    return redirect(url_for('doctor_profile'))


@app.route('/update-doctor-email', methods=['POST'])
def update_doctor_email():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    current_email = session['doctor']
    new_email = request.form['new_email']
    password = request.form['password']

    doctor_credentials = load_doctor_credentials()

    # Verify password
    if doctor_credentials.get(current_email) != password:
        return render_template('doctor-settings.html', message="Incorrect password", message_type="danger")

    # Check if new email already exists
    if new_email in doctor_credentials:
        return render_template('doctor-settings.html', message="Email already in use", message_type="danger")

    # Update email in credentials
    doctor_credentials[new_email] = doctor_credentials[current_email]
    del doctor_credentials[current_email]
    save_doctor_credentials(doctor_credentials)

    # Update email in doctors.json
    doctors = load_doctors()
    for doctor in doctors:
        if doctor['email'] == current_email:
            doctor['email'] = new_email
            doctor['updatedAt'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break
    save_doctors(doctors)

    # Update session
    session['doctor'] = new_email
    session['doctor_email'] = new_email

    return render_template('doctor-settings.html', message="Email updated successfully", message_type="success")


@app.route('/update-doctor-password', methods=['POST'])
def update_doctor_password():
    if 'doctor' not in session:
        return redirect(url_for('doctor_login'))

    email = session['doctor']
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    doctor_credentials = load_doctor_credentials()

    # Verify current password
    if doctor_credentials.get(email) != current_password:
        return render_template('doctor-settings.html', message="Incorrect current password", message_type="danger")

    # Check if new passwords match
    if new_password != confirm_password:
        return render_template('doctor-settings.html', message="New passwords do not match", message_type="danger")

    # Update password
    doctor_credentials[email] = new_password
    save_doctor_credentials(doctor_credentials)

    return render_template('doctor-settings.html', message="Password updated successfully", message_type="success")


# Patient Appointment Page
@app.route('/patient-appointment')
def patient_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_details = load_user_details()
    email = session['user']

    if email not in user_details:
        user_details[email] = {
            "name": "User",
            "phone": "Not provided"
        }
        save_user_details(user_details)

    # Initialize medications list if it doesn't exist
    if 'medications' not in user_details[email]:
        user_details[email]['medications'] = []
        save_user_details(user_details)

    return render_template('patient-appointment.html', user_details=user_details[email])


# New routes for enhanced patient appointment features

# Add appointment notes
@app.route('/add_appointment_notes', methods=['POST'])
def add_appointment_notes():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    email = session['user']
    appointment_id = request.form['appointment_id']
    notes = request.form['notes']

    # Update in user_details.json
    user_details = load_user_details()
    if email in user_details and 'appointments' in user_details[email]:
        for appointment in user_details[email]['appointments']:
            if appointment['id'] == appointment_id:
                appointment['notes'] = notes
                appointment['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break

        save_user_details(user_details)

        # Also update in appointments.json
        appointments = load_appointments()
        for appointment in appointments:
            if appointment['id'] == appointment_id and appointment['patient_email'] == email:
                appointment['notes'] = notes
                appointment['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break

        save_appointments(appointments)

        return redirect(url_for('patient_appointment'))

    return jsonify({"success": False, "message": "Appointment not found"}), 404


# Add appointment feedback
@app.route('/add_appointment_feedback', methods=['POST'])
def add_appointment_feedback():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    email = session['user']
    appointment_id = request.form['appointment_id']
    rating = request.form['rating']
    feedback = request.form['feedback']

    # Update in user_details.json
    user_details = load_user_details()
    if email in user_details and 'appointments' in user_details[email]:
        for appointment in user_details[email]['appointments']:
            if appointment['id'] == appointment_id:
                appointment['rating'] = rating
                appointment['feedback'] = feedback
                appointment['feedback_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break

        save_user_details(user_details)

        # Also update in appointments.json
        appointments = load_appointments()
        for appointment in appointments:
            if appointment['id'] == appointment_id and appointment['patient_email'] == email:
                appointment['rating'] = rating
                appointment['feedback'] = feedback
                appointment['feedback_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break

        save_appointments(appointments)

        return redirect(url_for('patient_appointment'))

    return jsonify({"success": False, "message": "Appointment not found"}), 404


# Reschedule appointment
@app.route('/reschedule_appointment', methods=['POST'])
def reschedule_appointment():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    email = session['user']
    appointment_id = request.form['appointment_id']
    new_date = request.form['new_date']
    new_time = request.form['new_time']
    reason = request.form['reason']

    # Update in user_details.json
    user_details = load_user_details()
    if email in user_details and 'appointments' in user_details[email]:
        for appointment in user_details[email]['appointments']:
            if appointment['id'] == appointment_id:
                # Store old date and time for notification
                old_date = appointment['date']
                old_time = appointment['time']

                # Update appointment
                appointment['date'] = new_date
                appointment['time'] = new_time
                appointment['reschedule_reason'] = reason
                appointment['rescheduled_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                appointment['rescheduled_from'] = f"{old_date} at {old_time}"
                break

        save_user_details(user_details)

        # Also update in appointments.json
        appointments = load_appointments()
        for appointment in appointments:
            if appointment['id'] == appointment_id and appointment['patient_email'] == email:
                # Store old date and time
                old_date = appointment['date']
                old_time = appointment['time']

                # Update appointment
                appointment['date'] = new_date
                appointment['time'] = new_time
                appointment['reschedule_reason'] = reason
                appointment['rescheduled_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                appointment['rescheduled_from'] = f"{old_date} at {old_time}"
                break

        save_appointments(appointments)

        return redirect(url_for('patient_appointment'))

    return jsonify({"success": False, "message": "Appointment not found"}), 404


# Cancel appointment
@app.route('/cancel_appointment', methods=['POST'])
def cancel_appointment():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    email = session['user']
    appointment_id = request.form['appointment_id']

    # Update in user_details.json
    user_details = load_user_details()
    if email in user_details and 'appointments' in user_details[email]:
        for appointment in user_details[email]['appointments']:
            if appointment['id'] == appointment_id:
                appointment['status'] = "Cancelled"
                appointment['cancelled_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break

        save_user_details(user_details)

        # Also update in appointments.json
        appointments = load_appointments()
        for appointment in appointments:
            if appointment['id'] == appointment_id and appointment['patient_email'] == email:
                appointment['status'] = "Cancelled"
                appointment['cancelled_at'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                break

        save_appointments(appointments)

        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Appointment not found"}), 404


# Add medication
@app.route('/add_medication', methods=['POST'])
def add_medication():
    if 'user' not in session:
        flash("Please log in to manage medications", "error")
        return redirect(url_for('login'))

    try:
        email = session['user']
        medication_name = request.form['medication_name']
        dosage = request.form['dosage']
        frequency = request.form['frequency']
        start_date = request.form['start_date']
        end_date = request.form.get('end_date', '')
        instructions = request.form.get('instructions', '')
        set_reminder = 'set_reminder' in request.form

        # Debug logging
        print(f"Adding medication for {email}: {medication_name}, {dosage}, {frequency}")

        # Update in user_details.json
        user_details = load_user_details()
        if email in user_details:
            # Initialize medications list if it doesn't exist
            if 'medications' not in user_details[email]:
                user_details[email]['medications'] = []

            # Create new medication
            medication = {
                "id": str(uuid.uuid4()),
                "name": medication_name,
                "dosage": dosage,
                "frequency": frequency,
                "start_date": start_date,
                "end_date": end_date,
                "instructions": instructions,
                "reminder": set_reminder,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            user_details[email]['medications'].append(medication)
            save_user_details(user_details)
            print(f"Medication added to user_details: {medication}")

            # Also save to medications.json for potential future use
            medications_data = load_medications()
            if email not in medications_data:
                medications_data[email] = []

            medications_data[email].append(medication)
            save_medications(medications_data)
            print("Medication saved to medications.json")

            flash("Medication added successfully!", "success")
            return redirect(url_for('patient_appointment'))
        else:
            print(f"User {email} not found in user_details")
            flash("Failed to add medication: User not found", "error")
            return redirect(url_for('patient_appointment'))
    except Exception as e:
        print(f"Error adding medication: {str(e)}")
        flash(f"Failed to add medication: {str(e)}", "error")
        return redirect(url_for('patient_appointment'))


# Get medications list
@app.route('/get_medications', methods=['GET'])
def get_medications():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    try:
        email = session['user']
        user_details = load_user_details()

        print(f"Getting medications for {email}")

        if email in user_details:
            if 'medications' not in user_details[email]:
                user_details[email]['medications'] = []
                save_user_details(user_details)
                print(f"Initialized empty medications list for {email}")

            medications = user_details[email]['medications']
            print(f"Found {len(medications)} medications for {email}")
            return jsonify({"success": True, "medications": medications})
        else:
            print(f"User {email} not found in user_details")
            return jsonify({"success": True, "medications": []})
    except Exception as e:
        print(f"Error getting medications: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500


# Delete medication
@app.route('/delete_medication', methods=['POST'])
def delete_medication():
    if 'user' not in session:
        flash("Please log in to manage medications", "error")
        return redirect(url_for('login'))

    email = session['user']
    medication_id = request.form['medication_id']

    # Update in user_details.json
    user_details = load_user_details()
    if email in user_details and 'medications' in user_details[email]:
        # Find the medication to delete
        found = False
        for med in user_details[email]['medications']:
            if med['id'] == medication_id:
                found = True
                break

        if found:
            # Remove the medication
            user_details[email]['medications'] = [m for m in user_details[email]['medications'] if
                                                  m['id'] != medication_id]
            save_user_details(user_details)

            # Also update in medications.json
            medications_data = load_medications()
            if email in medications_data:
                medications_data[email] = [m for m in medications_data[email] if m['id'] != medication_id]
                save_medications(medications_data)

            flash("Medication deleted successfully!", "success")
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Medication not found"})


# Add this to your existing main.py file
import json
import os


# Update the route to serve the medicine_tracking.json file instead of medicines.json
@app.route('/medicines.json')
def get_medicines():
    try:
        with open('medicine_tracking.json', 'r') as f:
            medicines = json.load(f)
        return json.dumps(medicines)
    except Exception as e:
        print(f"Error loading medicine_tracking.json: {e}")
        # Return a sample list if file doesn't exist
        sample_medicines = [
            {"name": "Amoxicillin", "type": "Antibiotic"},
            {"name": "Lisinopril", "type": "Blood Pressure"},
            {"name": "Metformin", "type": "Diabetes"},
            {"name": "Atorvastatin", "type": "Cholesterol"},
            {"name": "Albuterol", "type": "Asthma"},
            {"name": "Omeprazole", "type": "Acid Reflux"},
            {"name": "Levothyroxine", "type": "Thyroid"},
            {"name": "Ibuprofen", "type": "Pain Relief"},
            {"name": "Acetaminophen", "type": "Pain Relief"},
            {"name": "Aspirin", "type": "Pain Relief"},
            {"name": "Simvastatin", "type": "Cholesterol"},
            {"name": "Metoprolol", "type": "Blood Pressure"},
            {"name": "Losartan", "type": "Blood Pressure"},
            {"name": "Gabapentin", "type": "Nerve Pain"},
            {"name": "Hydrochlorothiazide", "type": "Diuretic"}
        ]
        return json.dumps(sample_medicines)


@app.route('/purchase_medicines')
def purchase_medicines():
    try:
        with open('purchase_medicines.json', 'r') as f:
            medicines = json.load(f)
        return jsonify(medicines)
    except Exception as e:
        print(f"Error loading purchase_medicines.json: {e}")
        # Return a sample list if file doesn't exist
        return jsonify([])


if __name__ == '__main__':
    app.run(debug=True, port=5001)
