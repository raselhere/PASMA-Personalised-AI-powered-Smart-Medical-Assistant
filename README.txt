Personalised AI-Powered Health Care System (PAHCS)
===================================================

Overview:
---------
PAHCS is a web-based medical assistance system that allows admins to manage doctors, patients, and medicines. 
It also integrates chatbot functionality to support health inquiries and uses a structured JSON-based database 
for dynamic user and medicine record management.

Main Features:
--------------
- Admin authentication and role-based access
- Add/Edit/Delete doctors, patients, and medicine records
- Dashboard with statistics
- JSON-based data storage (no SQL required)
- Medical chatbot integration (chatbot.py)
- Health datasets for further training and development (under /datasets)

File Structure:
---------------
- main.py                      : Flask backend handling all admin routes
- doctors.json                 : Stores registered doctor data
- user_details.json            : Stores registered patient data
- purchase_medicines.json      : Stores medicine records
- chatbot.py                   : AI-based chatbot logic
- /datasets/                   : Includes medical CSV files for symptoms, training, and medications
- /templates/                  : HTML templates (login, dashboard, management views)
- /static/uploads/             : (Previously for profile pictures; currently not used)

How to Run:
-----------
1. Make sure Python 3.8+ is installed
2. Install dependencies:
   pip install flask

3. Run the application:
   python main.py
   source venv/bin/activate && python3 main.py

4. Open your browser and go to:
   http://localhost:5002/

Default Admin Login:
--------------------
Email: admin@pasma.com
Password: admin123

Note:
-----
- Profile image upload functionality is disabled in the current version.
- Make sure to keep JSON file structures consistent with list or dict formats expected in main.py.

