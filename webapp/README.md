# Video to SOP Generator - Web Application

## 🌐 Web Interface Setup

This web application provides a user-friendly interface for the Video-to-SOP Generator with authentication and company management.

### Features

- **User Authentication**: Secure login and registration system
- **Company Branding**: Add your company name to generated SOPs
- **Dashboard**: View all your generated SOPs in one place
- **File Upload**: Easy drag-and-drop video upload
- **Real-time Processing**: Track SOP generation progress
- **Download Management**: Access and download your SOPs anytime
- **User Profiles**: Manage your account information

### Tech Stack

- **Backend**: Flask 3.1.2
- **Database**: SQLAlchemy with SQLite
- **Authentication**: Flask-Login with password hashing
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Gunicorn WSGI server

### Local Setup

1. **Activate Virtual Environment**:
   ```powershell
   .\myvenv\Scripts\Activate.ps1
   ```

2. **Install Dependencies** (if not already installed):
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   GROQ_API_KEY=your-groq-api-key
   GEMINI_API_KEY=your-gemini-api-key
   ```

4. **Initialize Database**:
   The database will be created automatically on first run.

5. **Run the Application**:
   ```powershell
   cd webapp
   python app.py
   ```

6. **Access the Web Interface**:
   Open your browser and navigate to: `http://localhost:5000`

### Project Structure

```
webapp/
├── app.py                  # Main Flask application
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Home page
│   ├── register.html      # Registration page
│   ├── login.html         # Login page
│   ├── dashboard.html     # User dashboard
│   ├── generate.html      # SOP generation page
│   ├── view_sop.html      # View SOP details
│   └── profile.html       # User profile
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css      # Application styles
│   └── js/
│       └── main.js        # JavaScript functionality
├── uploads/                # User uploaded videos (gitignored)
└── generated_sops/         # Generated PDF files (gitignored)
```

### Database Schema

**User Model**:
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `password_hash`: Hashed password
- `company_name`: Company name for SOPs
- `created_at`: Registration timestamp

**SOP Model**:
- `id`: Primary key
- `title`: SOP title
- `description`: SOP description
- `video_filename`: Uploaded video filename
- `pdf_filename`: Generated PDF filename
- `context`: User-provided context
- `steps_count`: Number of steps in SOP
- `processing_time`: Time taken to generate (seconds)
- `created_at`: Creation timestamp
- `user_id`: Foreign key to User

### Deployment to Heroku

1. **Create Heroku App**:
   ```bash
   heroku create your-app-name
   ```

2. **Set Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set GROQ_API_KEY=your-groq-key
   heroku config:set GEMINI_API_KEY=your-gemini-key
   ```

3. **Install FFmpeg Buildpack**:
   ```bash
   heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
   heroku buildpacks:add --index 2 heroku/python
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Initialize Database**:
   ```bash
   heroku run python -c "from webapp.app import app, db; app.app_context().push(); db.create_all()"
   ```

### Deployment to GitHub Pages (Alternative)

**Note**: GitHub Pages only supports static sites. For full functionality with backend processing, use Heroku, Render, or AWS.

For GitHub deployment with backend:
1. Use GitHub Actions to deploy to a cloud provider
2. Store database on cloud storage (PostgreSQL on Heroku/Render)
3. Configure CORS for frontend-backend separation

### Usage

1. **Register an Account**:
   - Go to the registration page
   - Fill in username, email, company name, and password
   - Submit to create your account

2. **Login**:
   - Enter your username and password
   - Check "Remember me" for persistent login

3. **Generate SOP**:
   - Click "Generate New SOP" from dashboard
   - Upload a video file (MP4, AVI, MOV, WebM, MKV)
   - Add optional context about the procedure
   - Click "Generate SOP" and wait for processing (~2 minutes)

4. **View SOPs**:
   - Access all your SOPs from the dashboard
   - Click on any SOP to view details
   - Download PDFs with one click

5. **Manage Account**:
   - View your profile information
   - See account statistics
   - Logout when done

### Security Features

- **Password Hashing**: Uses Werkzeug's secure password hashing
- **Session Management**: Flask-Login handles secure sessions
- **CSRF Protection**: Built-in Flask security features
- **File Upload Validation**: File type and size validation
- **User Isolation**: Users can only access their own SOPs

### Performance Optimization

- **FFmpeg Integration**: 15x faster frame extraction
- **Background Processing**: Non-blocking SOP generation
- **Automatic Cleanup**: Temporary files deleted after processing
- **Database Indexing**: Optimized queries with proper indexes
- **Static File Caching**: CSS/JS cached for faster loading

### Troubleshooting

**Database not created**:
```python
cd webapp
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

**Port already in use**:
Change port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

**Upload fails**:
- Check file size (max 500MB)
- Verify file format (MP4, AVI, MOV, WebM, MKV)
- Ensure `uploads/` directory exists and is writable

**PDF generation fails**:
- Verify API keys in `.env` file
- Check FFmpeg installation
- Review logs for specific errors

### API Keys Required

1. **Groq API Key**: For Whisper audio transcription
   - Get it from: https://console.groq.com/

2. **Google Gemini API Key**: For AI analysis
   - Get it from: https://makersuite.google.com/app/apikey

### Contributing

This web interface extends the CLI tool. For core functionality improvements, see the main project README.

### License

MIT License - See LICENSE file for details

### Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

---

**Note**: This is v2.0 of the Video-to-SOP Generator with full web interface. The CLI version is still available in the root directory.
