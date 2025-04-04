@echo off
echo 🚀 Starting Memory Forge setup...

:: Move to script directory
cd /d %~dp0

echo 📦 Installing frontend (Electron) dependencies...
call npm install

echo 🐍 Setting up Python virtual environment...
cd backend
python -m venv venv

echo 🐍 Activating virtual environment and installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Setup complete!
echo You can now run the app with:
echo     npm start
pause
