"""
Main Flask application for SOP Generator
"""
import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from config import config
from models import db, User, SOP

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from video_processor import extract_frames
from whisper_transcription import transcribe_audio
from sop_analyzer import analyze_frames_for_sop
from pdf_generator import create_sop_pdf

app = Flask(__name__)
app.config.from_object(config['development'])

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name')
        if not all([username, email, password, confirm_password, company_name]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        user = User(username=username, email=email, company_name=company_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    sops = SOP.query.filter_by(user_id=current_user.id).order_by(SOP.created_at.desc()).all()
    return render_template('dashboard.html', sops=sops)

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No video file uploaded.', 'danger')
            return redirect(url_for('generate'))
        file = request.files['video']
        if file.filename == '':
            flash('No video file selected.', 'danger')
            return redirect(url_for('generate'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            title = request.form.get('title', 'Untitled SOP')
            sop = SOP(title=title, video_filename=filename, status='processing', user_id=current_user.id)
            db.session.add(sop)
            db.session.commit()
            flash('Video uploaded! Processing started...', 'info')
            return redirect(url_for('process_sop', sop_id=sop.id))
        flash('Invalid file type. Allowed: mp4, avi, mov, webm, mkv', 'danger')
    return render_template('generate.html')

@app.route('/process/<int:sop_id>')
@login_required
def process_sop(sop_id):
    sop = SOP.query.get_or_404(sop_id)
    if sop.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('processing.html', sop=sop)

@app.route('/api/process/<int:sop_id>', methods=['POST'])
@login_required
def api_process_sop(sop_id):
    sop = SOP.query.get_or_404(sop_id)
    if sop.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    try:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], sop.video_filename)
        frames_dir = os.path.join(app.config['OUTPUT_FOLDER'], f'frames_{sop.id}')
        os.makedirs(frames_dir, exist_ok=True)
        extract_frames(video_path, frames_dir, interval=2)
        transcript_segments = transcribe_audio(video_path)
        sop_content = analyze_frames_for_sop(frames_dir, current_user.company_name, transcript_segments)
        pdf_filename = f"SOP_{sop.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], pdf_filename)
        create_sop_pdf(sop_content, pdf_path, frames_dir)
        sop.pdf_filename = pdf_filename
        sop.status = 'completed'
        sop.completed_at = datetime.utcnow()
        db.session.commit()
        import shutil
        if os.path.exists(frames_dir):
            shutil.rmtree(frames_dir)
        return jsonify({'success': True, 'redirect': url_for('view_sop', sop_id=sop.id)})
    except Exception as e:
        sop.status = 'failed'
        db.session.commit()
        return jsonify({'error': str(e)}), 500

@app.route('/sop/<int:sop_id>')
@login_required
def view_sop(sop_id):
    sop = SOP.query.get_or_404(sop_id)
    if sop.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    return render_template('view_sop.html', sop=sop)

@app.route('/download/<int:sop_id>')
@login_required
def download_sop(sop_id):
    sop = SOP.query.get_or_404(sop_id)
    if sop.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    if sop.pdf_filename:
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], sop.pdf_filename)
        return send_file(pdf_path, as_attachment=True, download_name=f"{sop.title}.pdf")
    flash('PDF not available.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/delete/<int:sop_id>', methods=['POST'])
@login_required
def delete_sop(sop_id):
    sop = SOP.query.get_or_404(sop_id)
    if sop.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('dashboard'))
    if sop.video_filename:
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], sop.video_filename)
        if os.path.exists(video_path):
            os.remove(video_path)
    if sop.pdf_filename:
        pdf_path = os.path.join(app.config['OUTPUT_FOLDER'], sop.pdf_filename)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
    db.session.delete(sop)
    db.session.commit()
    flash('SOP deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
