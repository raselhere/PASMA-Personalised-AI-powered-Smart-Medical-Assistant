from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import json
import os
import secrets
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, template_folder='../templates')
app.secret_key = 'admin_secret_key_for_pasma'

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Data file paths
DOCTORS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../doctors.json'))
PATIENTS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../user_details.json'))
MEDICINES_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../purchase_medicines.json'))
ADMINS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/admins.json'))

# Ensure data directory exists
os.makedirs(os.path.dirname(ADMINS_FILE), exist_ok=True)


# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize data files if they don't exist
for file_path in [DOCTORS_FILE, PATIENTS_FILE, MEDICINES_FILE, ADMINS_FILE]:
    if not os.path.exists(file_path):
        save_data({}, file_path)

# Default admin account
def create_default_admin():
    admins = load_data(ADMINS_FILE)
    if not admins:
        admins = {
            "admin@pasma.com": {
                "name": "Admin",
                "password": "admin123",
                "role": "super_admin"
            }
        }
        save_data(admins, ADMINS_FILE)

create_default_admin()

# Authentication routes
@app.route('/')
def index():
    if 'admin_email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admins = load_data(ADMINS_FILE)

        if email in admins and admins[email]['password'] == password:
            session['admin_email'] = email
            session['admin_name'] = admins[email]['name']
            session['admin_role'] = admins[email]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    doctors = load_data(DOCTORS_FILE)
    patients = load_data(PATIENTS_FILE)
    medicines = load_data(MEDICINES_FILE)

    stats = {
        'doctors_count': len(doctors),
        'patients_count': len(patients),
        'medicines_count': len(medicines)
    }

    return render_template('dashboard.html', stats=stats)

# Doctor management routes
@app.route('/doctors')
def doctors():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    doctors_data = load_data(DOCTORS_FILE)
    return render_template('doctors.html', doctors=doctors_data)

@app.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        phone = request.form.get('phone')
        password = request.form.get('password')

        doctors = load_data(DOCTORS_FILE)

        if email in doctors:
            flash('Doctor with this email already exists!', 'danger')
            return redirect(url_for('add_doctor'))

        # Handle profile picture upload
        profile_pic = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                profile_pic = f"uploads/{unique_filename}"

        # Create new doctor
        new_doctor = {
            "email": email,
            "name": name,
            "specialization": specialization,
            "phone": phone,
            "password": password,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        doctors.append(new_doctor)

        save_data(doctors, DOCTORS_FILE)
        flash('Doctor added successfully!', 'success')
        return redirect(url_for('doctors'))

    return render_template('add_doctor.html')

@app.route('/doctors/edit/<email>', methods=['GET', 'POST'])
def edit_doctor(email):
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    doctors = load_data(DOCTORS_FILE)

    if email not in doctors:
        flash('Doctor not found!', 'danger')
        return redirect(url_for('doctors'))

    if request.method == 'POST':
        doctors[email]['name'] = request.form.get('name')
        doctors[email]['specialization'] = request.form.get('specialization')
        doctors[email]['phone'] = request.form.get('phone')

        if request.form.get('password'):
            doctors[email]['password'] = request.form.get('password')

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                doctors[email]['profile_pic'] = f"uploads/{unique_filename}"

        save_data(doctors, DOCTORS_FILE)
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('doctors'))

    return render_template('edit_doctor.html', doctor=doctors[email], email=email)

@app.route('/doctors/delete/<email>')
def delete_doctor(email):
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    doctors = load_data(DOCTORS_FILE)

    if email in doctors:
        del doctors[email]
        save_data(doctors, DOCTORS_FILE)
        flash('Doctor deleted successfully!', 'success')
    else:
        flash('Doctor not found!', 'danger')

    return redirect(url_for('doctors'))

# Patient management routes
@app.route('/patients')
def patients():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    patients_data = load_data(PATIENTS_FILE)
    return render_template('patients.html', patients=patients_data)

@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        password = request.form.get('password')

        patients = load_data(PATIENTS_FILE)

        if email in patients:
            flash('Patient with this email already exists!', 'danger')
            return redirect(url_for('add_patient'))

        # Handle profile picture upload
        profile_pic = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                profile_pic = f"uploads/{unique_filename}"

        # Create new patient
        patients[email] = {
            "name": name,
            "phone": phone,
            "password": password,
            "profile_pic": profile_pic,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        save_data(patients, PATIENTS_FILE)
        flash('Patient added successfully!', 'success')
        return redirect(url_for('patients'))

    return render_template('add_patient.html')

@app.route('/patients/edit/<email>', methods=['GET', 'POST'])
def edit_patient(email):
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    patients = load_data(PATIENTS_FILE)

    if email not in patients:
        flash('Patient not found!', 'danger')
        return redirect(url_for('patients'))

    if request.method == 'POST':
        patients[email]['name'] = request.form.get('name')
        patients[email]['phone'] = request.form.get('phone')

        if request.form.get('password'):
            patients[email]['password'] = request.form.get('password')

        # Handle profile picture upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                patients[email]['profile_pic'] = f"uploads/{unique_filename}"

        save_data(patients, PATIENTS_FILE)
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients'))

    return render_template('edit_patient.html', patient=patients[email], email=email)

@app.route('/patients/delete/<email>')
def delete_patient(email):
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    patients = load_data(PATIENTS_FILE)

    if email in patients:
        del patients[email]
        save_data(patients, PATIENTS_FILE)
        flash('Patient deleted successfully!', 'success')
    else:
        flash('Patient not found!', 'danger')

    return redirect(url_for('patients'))

# Medicine management routes
@app.route('/medicines')
def medicines():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    medicines_data = load_data(MEDICINES_FILE)
    return render_template('medicines.html', medicines=medicines_data)

@app.route('/medicines/add', methods=['GET', 'POST'])
def add_medicine():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        id = f"med_{secrets.token_hex(4)}"
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        company = request.form.get('company')
        stock = int(request.form.get('stock'))

        medicines = load_data(MEDICINES_FILE)

        # Handle medicine image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image = f"uploads/{unique_filename}"

        # Create new medicine
        new_medicine = {
            "id": id,
            "name": name,
            "category": category,
            "price": price,
            "description": description,
            "company": company,
            "stock": stock,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        medicines.append(new_medicine)

        save_data(medicines, MEDICINES_FILE)
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('medicines'))

    return render_template('add_medicine.html')

@app.route('/medicines/edit/<id>', methods=['GET', 'POST'])
def edit_medicine(id):
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    medicines = load_data(MEDICINES_FILE)

    if id not in medicines:
        flash('Medicine not found!', 'danger')
        return redirect(url_for('medicines'))

    if request.method == 'POST':
        medicines[id]['name'] = request.form.get('name')
        medicines[id]['category'] = request.form.get('category')
        medicines[id]['price'] = float(request.form.get('price'))
        medicines[id]['description'] = request.form.get('description')
        medicines[id]['company'] = request.form.get('company')
        medicines[id]['stock'] = int(request.form.get('stock'))

        # Handle medicine image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                medicines[id]['image'] = f"uploads/{unique_filename}"

        save_data(medicines, MEDICINES_FILE)
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines'))

    return render_template('edit_medicine.html', medicine=medicines[id], id=id)

@app.route('/medicines/delete/<id>')
def delete_medicine(id):
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    medicines = load_data(MEDICINES_FILE)

    if id in medicines:
        del medicines[id]
        save_data(medicines, MEDICINES_FILE)
        flash('Medicine deleted successfully!', 'success')
    else:
        flash('Medicine not found!', 'danger')

    return redirect(url_for('medicines'))

# Admin management routes
@app.route('/admins')
def admins():
    if 'admin_email' not in session:
        flash('Please login first!', 'warning')
        return redirect(url_for('login'))

    # Only super_admin can access admin management
    if session.get('admin_role') != 'super_admin':
        flash('You do not have permission to access this page!', 'danger')
        return redirect(url_for('dashboard'))

    admins_data = load_data(ADMINS_FILE)
    return render_template('admins.html', admins=admins_data)

@app.route('/admins/add', methods=['GET', 'POST'])
def add_admin():
    if 'admin_email' not in session or session.get('admin_role') != 'super_admin':
        flash('You do not have permission to access this page!', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role')

        admins = load_data(ADMINS_FILE)

        if email in admins:
            flash('Admin with this email already exists!', 'danger')
            return redirect(url_for('add_admin'))

        # Create new admin
        admins[email] = {
            "name": name,
            "password": password,
            "role": role,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        save_data(admins, ADMINS_FILE)
        flash('Admin added successfully!', 'success')
        return redirect(url_for('admins'))

    return render_template('add_admin.html')

@app.route('/admins/edit/<email>', methods=['GET', 'POST'])
def edit_admin(email):
    if 'admin_email' not in session or session.get('admin_role') != 'super_admin':
        flash('You do not have permission to access this page!', 'danger')
        return redirect(url_for('dashboard'))

    admins = load_data(ADMINS_FILE)

    if email not in admins:
        flash('Admin not found!', 'danger')
        return redirect(url_for('admins'))

    if request.method == 'POST':
        admins[email]['name'] = request.form.get('name')
        admins[email]['role'] = request.form.get('role')

        if request.form.get('password'):
            admins[email]['password'] = request.form.get('password')

        save_data(admins, ADMINS_FILE)
        flash('Admin updated successfully!', 'success')
        return redirect(url_for('admins'))

    return render_template('edit_admin.html', admin=admins[email], email=email)

@app.route('/admins/delete/<email>')
def delete_admin(email):
    if 'admin_email' not in session or session.get('admin_role') != 'super_admin':
        flash('You do not have permission to access this page!', 'danger')
        return redirect(url_for('dashboard'))

    # Prevent deleting yourself
    if email == session.get('admin_email'):
        flash('You cannot delete your own account!', 'danger')
        return redirect(url_for('admins'))

    admins = load_data(ADMINS_FILE)

    if email in admins:
        del admins[email]
        save_data(admins, ADMINS_FILE)
        flash('Admin deleted successfully!', 'success')
    else:
        flash('Admin not found!', 'danger')

    return redirect(url_for('admins'))

# API endpoints for data
@app.route('/api/doctors')
def api_doctors():
    if 'admin_email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    doctors = load_data(DOCTORS_FILE)
    return jsonify(doctors)

@app.route('/api/patients')
def api_patients():
    if 'admin_email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    patients = load_data(PATIENTS_FILE)
    return jsonify(patients)

@app.route('/api/medicines')
def api_medicines():
    if 'admin_email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    medicines = load_data(MEDICINES_FILE)
    return jsonify(medicines)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Using port 5001 to avoid conflict with main app
