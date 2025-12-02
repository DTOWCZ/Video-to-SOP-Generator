@echo off
echo ========================================
echo  Testing Frontend Setup
echo ========================================
echo.

echo [1/3] Checking if frontend folder exists...
if exist "frontend\" (
    echo  Frontend folder found
) else (
    echo  Frontend folder NOT found
    exit /b 1
)
echo.

echo [2/3] Checking required files...
set "missing=0"

if exist "frontend\app.py" (echo  app.py) else (echo  app.py MISSING & set "missing=1")
if exist "frontend\config.py" (echo  config.py) else (echo  config.py MISSING & set "missing=1")
if exist "frontend\models.py" (echo  models.py) else (echo  models.py MISSING & set "missing=1")
if exist "frontend\requirements.txt" (echo  requirements.txt) else (echo  requirements.txt MISSING & set "missing=1")
if exist "frontend\.env.example" (echo  .env.example) else (echo  .env.example MISSING & set "missing=1")
if exist "frontend\templates" (echo  templates/) else (echo  templates/ MISSING & set "missing=1")
if exist "frontend\static" (echo  static/) else (echo  static/ MISSING & set "missing=1")

if %missing%==1 (
    echo.
    echo  Some files are missing!
    exit /b 1
)
echo.

echo [3/3] Checking HTML templates...
if exist "frontend\templates\index.html" (echo  index.html) else (echo  index.html MISSING)
if exist "frontend\templates\login.html" (echo  login.html) else (echo  login.html MISSING)
if exist "frontend\templates\register.html" (echo  register.html) else (echo  register.html MISSING)
if exist "frontend\templates\dashboard.html" (echo  dashboard.html) else (echo  dashboard.html MISSING)
if exist "frontend\templates\generate.html" (echo  generate.html) else (echo  generate.html MISSING)
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. cd frontend
echo 2. pip install -r requirements.txt
echo 3. Copy .env.example to .env and add your API keys
echo 4. python app.py
echo 5. Open http://localhost:5000
echo.
pause
