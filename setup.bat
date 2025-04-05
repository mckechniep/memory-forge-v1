@echo off

echo 🚀 Starting Memory Forge setup...

:: Move to script directory (safe no matter where it's launched from)
cd /d %~dp0

echo 📦 Installing frontend (Electron) dependencies...
call npm install

echo 🔍 Checking Python installation...

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found! Please install Python 3.8 or newer.
    pause
    exit /b 1
)

echo 🌐 Creating virtual environment...
cd backend
if not exist venv (
    python -m venv venv
) else (
    echo ✓ Virtual environment already exists
)

echo 🐍 Activating virtual environment and installing Python dependencies...
call venv\Scripts\activate.bat

:: Upgrade pip safely
python -m pip install --upgrade pip

:: Install backend requirements
pip install -r requirements.txt

echo ✅ Setup complete!
echo 🔁 You can now run the app with:
echo     npm start

pause
