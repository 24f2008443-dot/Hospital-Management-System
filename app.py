from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from extensions import db, login_manager, mail
from models import User, Doctor, Patient, Appointment, Availability, Treatment, init_db
from forms import RegisterForm, LoginForm, AppointmentForm, DoctorAvailabilityForm, TreatmentForm
from flask_login import login_user, current_user, login_required, logout_user
from datetime import datetime, date, timedelta

# APIs
from api import api_bp
# Mail wrapper
from mailer import send_appointment_email
# Utilities
from utils import is_time_in_availabilities

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    app.register_blueprint(api_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # initialize DB & seed admin
    with app.app_context():
        init_db(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if User.query.filter_by(username=form.username.data).first():
                flash('Username taken', 'danger')
                return redirect(url_for('register'))
            u = User(username=form.username.data, email=form.email.data)
            u.set_password(form.password.data)
            db.session.add(u)
            patient = Patient(user=u, fullname=form.username.data)
            db.session.add(patient)
            db.session.commit()
            flash('Registered. Please login.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid credentials', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        if current_user.role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('patient_dashboard'))

    from sqlalchemy import func
    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Not authorized', 'danger')
            return redirect(url_for('index'))

        days = 14
        today = datetime.utcnow().date()
        start = today - timedelta(days=days-1)
        counts = db.session.query(Appointment.date, func.count(Appointment.id)).filter(Appointment.date >= start).group_by(Appointment.date).all()

        day_map = { (start + timedelta(days=i)).isoformat(): 0 for i in range(days) }
        for d, c in counts:
            day_map[d.isoformat()] = c

        labels = list(day_map.keys())
        values = list(day_map.values())
        total_doctors = Doctor.query.count()
        total_patients = Patient.query.count()
        total_appointments = Appointment.query.count()

        return render_template('admin_dashboard.html', labels=labels, values=values,
                            total_doctors=total_doctors, total_patients=total_patients,
                            total_appointments=total_appointments)

    @app.route('/admin/doctors')
    @login_required
    def admin_doctors():
        if current_user.role != 'admin':
            flash('Unauthorized', 'danger')
            return redirect(url_for('index'))
        q = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        per_page = 10
        query = Doctor.query
        if q:
            like = f"%{q}%"
            query = query.filter((Doctor.fullname.ilike(like)) | (Doctor.specialization.ilike(like)))
        pagination = query.order_by(Doctor.fullname).paginate(page=page, per_page=per_page, error_out=False)
        return render_template('admin_doctors.html', doctors=pagination.items, pagination=pagination, q=q)

    @app.route('/doctor')
    @login_required
    def doctor_dashboard():
        if current_user.role != 'doctor':
            flash('Unauthorized', 'danger')
            return redirect(url_for('index'))
        doc = Doctor.query.filter_by(user_id=current_user.id).first()
        assigned_appts = Appointment.query.filter_by(doctor_id=doc.id).order_by(Appointment.date).all()
        today = date.today()
        end = today + timedelta(days=7)
        avail = Availability.query.filter(Availability.doctor_id == doc.id, Availability.date >= today, Availability.date <= end).order_by(Availability.date).all()
        return render_template('doctor_dashboard.html', appts=assigned_appts, availabilities=avail, doc=doc)

    @app.route('/patient')
    @login_required
    def patient_dashboard():
        from datetime import date, timedelta
        today = date.today()
        end = today + timedelta(days=7)
        doctors = Doctor.query.filter(Doctor.is_blacklisted == False).all()
        upcoming = Appointment.query.join(Patient).filter(Patient.user_id == current_user.id).order_by(Appointment.date.desc()).all()
        return render_template('patient_dashboard.html', doctors=doctors, upcoming=upcoming)

    @app.route('/book', methods=['GET', 'POST'])
    @login_required
    def book():
        if current_user.role != 'patient':
            flash('Only patients can book', 'danger')
            return redirect(url_for('index'))
        form = AppointmentForm()
        form.doctor_id.choices = [(d.id, f"{d.fullname} - {d.specialization}") for d in Doctor.query.filter(Doctor.is_blacklisted==False).all()]
        if form.validate_on_submit():
            the_date = form.date.data
            the_time = form.time.data
            doctor_id = form.doctor_id.data
            avail_list = Availability.query.filter_by(doctor_id=doctor_id, date=the_date).all()
            from utils import is_time_in_availabilities
            if not is_time_in_availabilities(avail_list, the_time):
                flash('Doctor is not available at this time', 'danger')
                return redirect(url_for('book'))
            existing = Appointment.query.filter_by(doctor_id=doctor_id, date=the_date, time=the_time).first()
            if existing:
                flash('Slot already booked', 'danger')
                return redirect(url_for('book'))
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            appt = Appointment(doctor_id=doctor_id, patient_id=patient.id, date=the_date, time=the_time)
            db.session.add(appt)
            db.session.commit()

            try:
                recipient = current_user.email
                if recipient:
                    send_appointment_email(recipient, 'Appointment Confirmation', f'Your appointment is booked for {the_date} at {the_time}')
            except Exception:
                pass

            flash('Appointment booked', 'success')
            return redirect(url_for('patient_dashboard'))
        return render_template('book.html', form=form)

    @app.route('/appointment/<int:appt_id>/cancel')
    @login_required
    def cancel_appointment(appt_id):
        appt = Appointment.query.get_or_404(appt_id)
        if current_user.role == 'patient':
            patient = Patient.query.filter_by(user_id=current_user.id).first()
            if appt.patient_id != patient.id:
                flash('Not authorized', 'danger')
                return redirect(url_for('index'))
        appt.status = 'Cancelled'
        db.session.commit()
        flash('Appointment cancelled', 'success')
        return redirect(url_for('patient_dashboard'))

    @app.route('/appointment/<int:appt_id>/complete', methods=['GET', 'POST'])
    @login_required
    def complete_appointment(appt_id):
        appt = Appointment.query.get_or_404(appt_id)
        if current_user.role != 'doctor':
            flash('Only doctors can mark complete', 'danger')
            return redirect(url_for('index'))
        doc = Doctor.query.filter_by(user_id=current_user.id).first()
        if appt.doctor_id != doc.id:
            flash('Not authorized', 'danger')
            return redirect(url_for('index'))
        form = TreatmentForm()
        if form.validate_on_submit():
            appt.status = 'Completed'
            t = Treatment(appointment=appt, patient_id=appt.patient_id, diagnosis=form.diagnosis.data,
                        prescription=form.prescription.data, notes=form.notes.data)
            db.session.add(t)
            db.session.commit()
            flash('Saved treatment', 'success')
            return redirect(url_for('doctor_dashboard'))
        return render_template('treatment_form.html', form=form, appt=appt)

    return app

if __name__ == '__main__':
    create_app().run(debug=True)
