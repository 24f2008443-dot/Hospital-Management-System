🏥 Hospital Management System (HMS)

A complete Hospital Management System built using Flask, SQLite, Jinja2, HTML/CSS, and Bootstrap.
The system provides separate role-based access for Admins, Doctors, and Patients, ensuring smooth management of hospital operations.

📌 Overview

Hospitals often struggle with manual record keeping, scheduling conflicts, missing patient history, and inefficient coordination.
This HMS web application solves these problems by bringing patient, doctor, appointment, and treatment management into a single system.

This project contains:

Role-based authentication

Appointment booking system

Doctor availability management

Patient treatment history

Admin dashboard & controls

Fully programmatically created database (NO manual DB creation allowed)


🛠 Technologies Used

| Component | Technology                                             |
| --------- | ------------------------------------------------------ |
| Backend   | **Flask** (Python)                                     |
| Frontend  | **HTML**, **CSS**, **Bootstrap**, **Jinja2** Templates |
| Database  | **SQLite**                                             |
| ORM       | **Flask-SQLAlchemy**                                   |
| Auth      | **Flask-Login**                                        |



👥 User Roles & Functionalities
1. Admin (Superuser)

Admin is automatically created when the database is initialized (no manual signup allowed).
Admin can:

View dashboard statistics: total doctors, patients, appointments

Add / update / delete doctor profiles

Manage upcoming & past appointments

Search:

Doctors by name/specialization

Patients by name, ID, or contact

Edit doctor & patient information

Blacklist/remove doctors or patients

View complete patient history

Prevent appointment conflicts

2. Doctor

Doctors can:

Log in to their dashboard

View today’s / weekly appointments

View assigned patients

Mark appointments as:

Completed

Cancelled

Add treatment details:

Diagnosis

Prescription

Notes

View entire medical history of patients

Update their 7-day availability

3. Patient

Patients can:

Register & log in

Search doctors by specialization & availability

Book / reschedule / cancel appointments

View:

Upcoming appointments

Past appointment history

Diagnosis & prescriptions

Update their profile

View all hospital departments

📅 Appointment Rules

No two patients can book the same doctor at the same time

Appointment flow:
Booked → Completed → Cancelled

Treatment records stored permanently

Doctors & patients can view full treatment history

🏥 Core System Features

Admin dashboard with statistics

Doctor availability for next 7 days

Role-based views (Admin / Doctor / Patient)

Patient medical history tracking

Dynamic appointment status

Search system for doctors, patients, and departments

Automatic database creation on first run

CRUD operations on doctors & appointments

Secure authentication using Flask-Login

🗂 Database Structure (Simplified)

The system includes at minimum:

Patients

patient_id

name

email

contact

gender

password hash

medical history

Doctors

doctor_id

name

specialization / department

availability

status (Active / Blacklisted)

Appointments

appointment_id

patient_id

doctor_id

date & time

status (Booked/Completed/Cancelled)

Treatments

treatment_id

appointment_id

diagnosis

prescription

doctor notes

Departments

department_id

name

description

(Students may add extra fields as needed.)

🗃 Database Creation (Important)

✔ Database MUST be created programmatically
✘ Manual creation via DB Browser or external tools is NOT allowed

This means:

Your code should automatically generate all tables on first run

Admin user must be auto-created in code

✨ UI Inspiration

You may design your own frontend OR take inspiration from:
🔗 https://mocdoc.com/

Replication is not required, only functionality matters.

🎯 Application Flow (Wireframe Summary)

Patient → Login → Dashboard → View doctors → Book appointment

Doctor → Login → View today's appointments → Update status → Add treatment

Admin → Login → Dashboard → Manage doctors → View all appointments

🚀 Running the Application Locally
pip install -r requirements.txt
python app.py


Database will auto-generate on the first run.

📁 Folder Structure (Recommended)
project/
│ app.py
│ requirements.txt
│ README.md
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── admin/
│   ├── doctor/
│   └── patient/
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── models/
    └── tables.py

📌 Future Enhancements (Optional)

Chart.js reports for admin

Email / SMS notifications

Pagination & advanced search

AJAX-based dynamic availability

🏁 Conclusion

This Hospital Management System ensures seamless interaction between patients, doctors, and admin staff.
It provides all required features for managing hospital operations efficiently, following the academic project requirements.


See project instructions. Run python app.py after installing requirements.
Admin seeded: admin / Admin@123
