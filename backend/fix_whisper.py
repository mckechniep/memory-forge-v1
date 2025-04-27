import subprocess
import sys
import os
import site

def main():
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Site packages: {site.getsitepackages()}")
    
    print("\nChecking for whisper installation...")
    try:
        import whisper
        print("✅ Whisper is already installed correctly!")
        print(f"Whisper found at: {whisper.__file__}")
        return
    except ImportError as e:
        print(f"❌ Whisper not found. Error: {e}")
        print("Attempting to install...")
    
    # Try to install the correct package
    try:
        print("Installing openai-whisper...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai-whisper"])
        print("✅ Successfully installed openai-whisper")
        
        # Verify installation
        try:
            import whisper
            print(f"✅ Whisper now available at: {whisper.__file__}")
        except ImportError as e:
            print(f"❌ Still can't import whisper after installation. Error: {e}")
            print("\nListing installed packages:")
            subprocess.check_call([sys.executable, "-m", "pip", "list"])
            print("\nPlease try manually running: pip install --force-reinstall openai-whisper")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install openai-whisper. Error: {e}")
        print("Please try manually running: pip install --force-reinstall openai-whisper")

if __name__ == "__main__":
    main()
