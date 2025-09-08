#!/usr/bin/env python3
"""
TBMCG News Dashboard Setup Script
Automates the initial setup process for new installations.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    # Check if venv exists and has pip
    if os.name == 'nt':
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    if venv_path.exists() and pip_path.exists() and python_path.exists():
        print("✅ Virtual environment already exists and is valid")
        return
    
    # Remove incomplete venv if it exists
    if venv_path.exists():
        print("⚠️  Incomplete virtual environment detected, recreating...")
        shutil.rmtree(venv_path)
    
    print("📦 Creating virtual environment...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        sys.exit(1)

def get_python_command():
    """Get the correct python command for the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "python.exe")
    else:  # macOS/Linux
        return os.path.join("venv", "bin", "python")

def install_dependencies():
    """Install Python dependencies in virtual environment"""
    python_cmd = get_python_command()
    
    # Check if python executable exists
    if not os.path.exists(python_cmd):
        print(f"❌ Virtual environment Python not found at {python_cmd}")
        print("   Please run the script again to recreate the virtual environment")
        sys.exit(1)
    
    print("📚 Installing dependencies...")
    try:
        # Upgrade pip first using python -m pip
        print("   Upgrading pip...")
        subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        print("   Installing requirements...")
        subprocess.run([python_cmd, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"   Error details: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ Could not find Python executable: {e}")
        print("   Please ensure the virtual environment was created correctly")
        sys.exit(1)

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("⚠️  .env.example not found, skipping .env creation")
        return
    
    print("📝 Creating .env file from template...")
    shutil.copy(env_example, env_file)
    print("✅ .env file created - please edit it with your Microsoft Azure credentials")

def display_next_steps():
    """Display instructions for next steps"""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit the .env file with your Microsoft Azure credentials:")
    print("   - MICROSOFT_CLIENT_ID=your-client-id")
    print("   - MICROSOFT_CLIENT_SECRET=your-client-secret")
    print("   - SECRET_KEY=generate-a-random-secret-key")
    print()
    print("2. Activate the virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print()
    print("3. Start the application:")
    print("   python app.py")
    print()
    print("4. Visit http://localhost:5000 in your browser")
    print("\n📚 See README.md for detailed setup instructions")

def main():
    """Main setup function"""
    print("🚀 TBMCG News Dashboard Setup")
    print("=" * 40)
    
    # Check requirements
    check_python_version()
    
    # Setup steps
    create_virtual_environment()
    install_dependencies()
    create_env_file()
    
    # Show next steps
    display_next_steps()

if __name__ == "__main__":
    main()