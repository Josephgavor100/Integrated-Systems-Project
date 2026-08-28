# models.py
import re
import time
import smtplib
from email.mime.text import MIMEText
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

bcrypt = Bcrypt()

ID_PATTERN = r"^\d{8}$"
MIN_PASSWORD_LENGTH = 8


class InvalidIDError(Exception):
    pass


class WeakPasswordError(Exception):
    pass


class User:
    def __init__(self, name, id_number, password, email=None, role="patient"):
        if not re.fullmatch(ID_PATTERN, id_number):
            raise InvalidIDError(f"'{id_number}' is not a valid 8-digit ID")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters")
        self.name = name
        self.id_number = id_number
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.role = role

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def generate_safe_filename(original_filename, id_number):
    safe_original = secure_filename(original_filename)
    timestamp = int(time.time())
    return f"{id_number}_{timestamp}_{safe_original}"


class HealthTask:
    VALID_CATEGORIES = {"pending", "in_review", "resolved", "flagged_urgent"}

    def __init__(self, task_id, patient_id, description, filename=None):
        self.task_id = task_id
        self.patient_id = patient_id
        self.description = description
        self.filename = filename
        self.category = "pending"
        self.created_at = time.time()
        self.resolved_at = None

    def update_category(self, new_category):
        if new_category not in self.VALID_CATEGORIES:
            raise ValueError(f"'{new_category}' is not a valid category")
        self.category = new_category
        if new_category == "resolved":
            self.resolved_at = time.time()


class Message:
    def __init__(self, message_id, sender_id, recipient_id, content, timestamp):
        self.message_id = message_id
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
        self.timestamp = timestamp


def send_notification_email(smtp_config, to_address, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_config['SMTP_USERNAME']
    msg['To'] = to_address
    try:
        with smtplib.SMTP(smtp_config['SMTP_SERVER'], smtp_config['SMTP_PORT']) as server:
            server.starttls()
            server.login(smtp_config['SMTP_USERNAME'], smtp_config['SMTP_PASSWORD'])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False


def calculate_average_turnaround(tasks):
    resolved = [t for t in tasks.values() if t.resolved_at is not None]
    if not resolved:
        return None
    total_seconds = sum(t.resolved_at - t.created_at for t in resolved)
    return round((total_seconds / len(resolved)) / 3600, 2)


def calculate_category_breakdown(tasks):
    breakdown = {cat: 0 for cat in HealthTask.VALID_CATEGORIES}
    for task in tasks.values():
        breakdown[task.category] += 1
    return breakdown