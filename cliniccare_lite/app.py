# app.py
import os
import time
from functools import wraps
from flask import Flask, request, session, redirect, url_for, render_template, flash

from config import Config
from models import (
    bcrypt, User, InvalidIDError, HealthTask, Message,
    allowed_file, generate_safe_filename, send_notification_email,
    calculate_average_turnaround, calculate_category_breakdown
)

app = Flask(__name__)
app.config.from_object(Config)
bcrypt.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- in-memory "database" ---
users = {}
# TEMPORARY: seed one clinician test account for team testing.
# Public /register always creates patients only, by design.
users["99999999"] = User("Test Clinician", "99999999", "clinician123", role="clinician")
tasks = {}
next_task_id = [1]
messages = []
next_message_id = [1]


# --- decorators ---
def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.")
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped


def role_required(required_role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') != required_role:
                return "Access denied: insufficient permissions.", 403
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# --- auth routes ---
@app.route('/')
def home():
    return "ClinicCare-Lite is running"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        id_number = request.form['id_number']
        password = request.form['password']
        confirm = request.form.get('confirm_password', password)

        if password != confirm:
            flash("Passwords do not match.")
            return render_template('register.html')
        if id_number in users:
            flash("An account with this ID already exists.")
            return render_template('register.html')
        try:
            user = User(name, id_number, password)
        except InvalidIDError as e:
            flash(str(e))
            return render_template('register.html')

        users[id_number] = user
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id_number = request.form['id_number']
        password = request.form['password']
        user = users.get(id_number)
        if user and user.check_password(password):
            session['user_id'] = id_number
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        flash("Invalid ID or password.")
        return render_template('login.html')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    user = users.get(session['user_id'])
    return render_template('dashboard.html', name=user.name, role=user.role, id_number=user.id_number)


@app.route('/staff-only')
@role_required('clinician')
def staff_only():
    return "Welcome to the clinician-only area."


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- uploads ---
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in the request.")
            return render_template('upload.html')
        file = request.files['file']
        if file.filename == '':
            flash("No file selected.")
            return render_template('upload.html')
        if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
            flash("File type not allowed. Use .txt, .csv, or .pdf.")
            return render_template('upload.html')

        safe_name = generate_safe_filename(file.filename, session['user_id'])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
        file.save(filepath)
        flash(f"File uploaded successfully as {safe_name}")
        return redirect(url_for('dashboard'))

    return render_template('upload.html')


# --- tasks / review ---

@app.route('/tasks/submit', methods=['GET', 'POST'])
@login_required
def submit_task():
    if request.method == 'POST':
        description = request.form['description']

        task = HealthTask(
            task_id=next_task_id[0],
            patient_id=session['user_id'],
            description=description
        )
        tasks[task.task_id] = task
        next_task_id[0] += 1

        flash("Your request has been submitted.")
        return redirect(url_for('dashboard'))

    return render_template('submit_task.html')

@app.route('/tasks/review')
@role_required('clinician')
def review_queue():
    pending_tasks = [t for t in tasks.values() if t.category != "resolved"]
    return render_template('review_queue.html', tasks=pending_tasks)


@app.route('/tasks/<int:task_id>/update', methods=['POST'])
@role_required('clinician')
def update_task_category(task_id):
    task = tasks.get(task_id)
    if not task:
        return "Task not found", 404

    new_category = request.form['category']
    try:
        task.update_category(new_category)
    except ValueError as e:
        flash(str(e))
        return redirect(url_for('review_queue'))

    patient = users.get(task.patient_id)
    if patient and app.config.get('SMTP_USERNAME'):
        smtp_config = {
            'SMTP_SERVER': app.config['SMTP_SERVER'],
            'SMTP_PORT': app.config['SMTP_PORT'],
            'SMTP_USERNAME': app.config['SMTP_USERNAME'],
            'SMTP_PASSWORD': app.config['SMTP_PASSWORD'],
        }
        send_notification_email(
            smtp_config,
            to_address=f"{patient.id_number}@example.com",
            subject="Your ClinicCare-Lite task status changed",
            body=f"Task #{task.task_id} is now marked: {task.category}"
        )

    return redirect(url_for('review_queue'))


# --- messaging ---
@app.route('/messages', methods=['GET'])
@login_required
def view_messages():
    my_id = session['user_id']
    my_messages = [m for m in messages if m.recipient_id == my_id or m.sender_id == my_id]
    return render_template('messages.html', messages=my_messages)

@app.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    recipient_id = data['recipient_id']
    content = data['content']
    msg = Message(
        message_id=next_message_id[0],
        sender_id=session['user_id'],
        recipient_id=recipient_id,
        content=content,
        timestamp=time.time()
    )
    messages.append(msg)
    next_message_id[0] += 1
    return {"status": "sent", "message_id": msg.message_id}


@app.route('/messages/poll')
@login_required
def poll_messages():
    my_id = session['user_id']
    unread = [
        {"sender_id": m.sender_id, "content": m.content, "timestamp": m.timestamp}
        for m in messages if m.recipient_id == my_id
    ]
    return {"unread_count": len(unread), "messages": unread}


# --- analytics ---
@app.route('/analytics')
@role_required('clinician')
def analytics_dashboard():
    avg_turnaround = calculate_average_turnaround(tasks)
    breakdown = calculate_category_breakdown(tasks)
    return render_template('analytics.html', avg_turnaround=avg_turnaround, breakdown=breakdown)

@app.route('/api/tasks')
@role_required('clinician')
def api_tasks():
    task_list = [
        {
            "task_id": t.task_id,
            "patient_id": t.patient_id,
            "category": t.category,
            "created_at": t.created_at,
            "resolved_at": t.resolved_at,
        }
        for t in tasks.values()
    ]
    return {"tasks": task_list}


if __name__ == '__main__':
    app.run(debug=True)