from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='patient')  # admin/doctor/patient

    patient_profile = db.relationship('Patient', backref='user', uselist=False)
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False)

    def set_password(self, pw):
        self.password_hash = generate_password_hash(pw)

    def check_password(self, pw):
        return check_password_hash(self.password_hash, pw)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(500))
    doctors = db.relationship('Doctor', backref='department', lazy=True)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    fullname = db.Column(db.String(120), nullable=False)
    specialization = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.String(500))
    is_blacklisted = db.Column(db.Boolean, default=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))

    availabilities = db.relationship('Availability', backref='doctor', lazy=True, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    fullname = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(50))
    is_blacklisted = db.Column(db.Boolean, default=False)

    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    histories = db.relationship('Treatment', backref='patient', lazy=True)

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='Booked')  # Booked / Completed / Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    treatment = db.relationship('Treatment', uselist=False, backref='appointment')

    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'date', 'time', name='uix_doctor_date_time'),
    )

class Treatment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    diagnosis = db.Column(db.String(500))
    prescription = db.Column(db.String(1000))
    notes = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# helper: initialize DB and seed admin & some departments
def init_db(app):
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@hospital.local', role='admin')
            admin.set_password('Admin@123')
            db.session.add(admin)
            db.session.commit()
        if Department.query.count() == 0:
            for name in ['Cardiology', 'Oncology', 'General']:
                db.session.add(Department(name=name, description=f'{name} department'))
            db.session.commit()
