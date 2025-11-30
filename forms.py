from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField, TimeField, TextAreaField
from wtforms.validators import DataRequired, Length, Email

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class DoctorAvailabilityForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Save')

class AppointmentForm(FlaskForm):
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    submit = SubmitField('Book')

class TreatmentForm(FlaskForm):
    diagnosis = TextAreaField('Diagnosis')
    prescription = TextAreaField('Prescription')
    notes = TextAreaField('Notes')
    submit = SubmitField('Save')
