from flask import current_app
from flask_mail import Message
from extensions import mail


def send_appointment_email(recipient, subject, body):
    msg = Message(subject=subject, recipients=[recipient], body=body)
    try:
        mail.send(msg)
    except Exception as e:
        # In dev we may use a local debug smtp server; log and continue
        current_app.logger.error('Failed to send mail: %s', e)
