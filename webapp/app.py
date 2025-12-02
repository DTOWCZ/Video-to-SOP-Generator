"""
Flask Web Application for Video-to-SOP Generator
With user authentication and company management
"""

import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///video_sop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['GENERATED_FOLDER'] = os.path.join(os.path.dirname(__file__), 'generated_sops')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Allowed video extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm', 'mkv'}

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create upload and generated folders if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)


# Database Models
class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sops = db.relationship('SOP', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches"""
        return check_password_hash(self.password_hash, password)


class SOP(db.Model):
    """SOP document model"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_filename = db.Column(db.String(255), nullable=False)
    pdf_filename = db.Column(db.String(255), nullable=False)
    context = db.Column(db.String(500))
    steps_count = db.Column(db.Integer, default=0)
    processing_time = db.Column(db.Float)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID"""
    return db.session.get(User, int(user_id))


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Routes
@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        company_name = request.form.get('company_name')
        
        # Validation
        if not all([username, email, password, confirm_password, company_name]):
            flash('All fields are required!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long!', 'error')
            return render_template('register.html')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            company_name=company_name
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        
        flash('Invalid username or password!', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's SOPs
    user_sops = SOP.query.filter_by(user_id=current_user.id).order_by(SOP.created_at.desc()).all()
    
    return render_template('dashboard.html', sops=user_sops)


@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_sop():
    """Generate new SOP from video"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'video' not in request.files:
            flash('No video file uploaded!', 'error')
            return redirect(request.url)
        
        file = request.files['video']
        context = request.form.get('context', '').strip()
        
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Save video file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{current_user.id}_{timestamp}_{filename}"
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(video_path)
            
            # Generate unique PDF filename
            pdf_filename = f"{current_user.id}_{timestamp}_sop.pdf"
            pdf_path = os.path.join(app.config['GENERATED_FOLDER'], pdf_filename)
            
            try:
                # Import SOP generator
                from video_processor import VideoFrameExtractor
                from sop_analyzer import SOPAnalyzer
                from pdf_generator import SOPPDFGenerator
                from whisper_transcription import transcribe_video_audio
                import time
                from dotenv import load_dotenv
                
                load_dotenv()
                
                # Process video
                start_time = time.time()
                
                video_processor = VideoFrameExtractor(interval_seconds=2)
                analyzer = SOPAnalyzer()
                pdf_generator = SOPPDFGenerator()
                
                # Extract frames
                frames_dir = os.path.join(app.config['UPLOAD_FOLDER'], f'frames_{timestamp}')
                os.makedirs(frames_dir, exist_ok=True)
                
                frames = video_processor.extract_frames(video_path, output_dir=frames_dir)
                
                # Extract audio transcript
                audio_transcript = ""
                groq_api_key = os.getenv("GROQ_API_KEY")
                if groq_api_key:
                    audio_transcript = transcribe_video_audio(video_path, groq_api_key) or ""
                
                # Analyze and generate SOP
                sop_data = analyzer.analyze_video_frames(frames, context, audio_transcript)
                
                # Generate PDF with company name
                pdf_generator.generate_sop_pdf(
                    sop_data,
                    frames,
                    pdf_path,
                    current_user.company_name
                )
                
                # Cleanup frames
                import shutil
                if os.path.exists(frames_dir):
                    shutil.rmtree(frames_dir)
                
                processing_time = time.time() - start_time
                
                # Save to database
                new_sop = SOP(
                    title=sop_data['title'],
                    description=sop_data.get('description', ''),
                    video_filename=unique_filename,
                    pdf_filename=pdf_filename,
                    context=context,
                    steps_count=len(sop_data['steps']),
                    processing_time=processing_time,
                    user_id=current_user.id
                )
                
                db.session.add(new_sop)
                db.session.commit()
                
                flash(f'SOP generated successfully in {int(processing_time)} seconds!', 'success')
                return redirect(url_for('view_sop', sop_id=new_sop.id))
                
            except Exception as e:
                flash(f'Error generating SOP: {str(e)}', 'error')
                # Cleanup on error
                if os.path.exists(video_path):
                    os.remove(video_path)
                return redirect(url_for('generate_sop'))
        
        else:
            flash('Invalid file type! Allowed types: mp4, avi, mov, webm, mkv', 'error')
            return redirect(request.url)
    
    return render_template('generate.html')


@app.route('/sop/<int:sop_id>')
@login_required
def view_sop(sop_id):
    """View SOP details"""
    sop = SOP.query.get_or_404(sop_id)
    
    # Check if user owns this SOP
    if sop.user_id != current_user.id:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('view_sop.html', sop=sop)


@app.route('/download/<int:sop_id>')
@login_required
def download_sop(sop_id):
    """Download SOP PDF"""
    sop = SOP.query.get_or_404(sop_id)
    
    # Check if user owns this SOP
    if sop.user_id != current_user.id:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    pdf_path = os.path.join(app.config['GENERATED_FOLDER'], sop.pdf_filename)
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name=f"{sop.title}.pdf")
    else:
        flash('PDF file not found!', 'error')
        return redirect(url_for('dashboard'))


@app.route('/delete/<int:sop_id>', methods=['POST'])
@login_required
def delete_sop(sop_id):
    """Delete SOP"""
    sop = SOP.query.get_or_404(sop_id)
    
    # Check if user owns this SOP
    if sop.user_id != current_user.id:
        flash('Access denied!', 'error')
        return redirect(url_for('dashboard'))
    
    # Delete files
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], sop.video_filename)
    pdf_path = os.path.join(app.config['GENERATED_FOLDER'], sop.pdf_filename)
    
    if os.path.exists(video_path):
        os.remove(video_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    
    # Delete from database
    db.session.delete(sop)
    db.session.commit()
    
    flash('SOP deleted successfully!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html')


if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
