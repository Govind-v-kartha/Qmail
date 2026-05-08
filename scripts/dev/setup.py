"""
QMail Setup Script
Automates the setup process
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd, description):
    """Run a command and print status"""
    print(f"→ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stderr:
            print(f"  Error: {e.stderr}")
        return False


def setup_environment():
    """Set up virtual environment and dependencies"""
    print_header("QMail Setup - Step 1: Environment")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 10):
        print("⚠️  Warning: Python 3.10 or higher is recommended")
    
    # Create virtual environment
    if not Path("venv").exists():
        if run_command("python -m venv venv", "Creating virtual environment"):
            print("  Virtual environment created at: ./venv")
    else:
        print("✓ Virtual environment already exists")
    
    # Activate instructions
    print("\n📝 To activate virtual environment:")
    if sys.platform == "win32":
        print("   .\\venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")


def install_dependencies():
    """Install Python dependencies"""
    print_header("QMail Setup - Step 2: Dependencies")
    
    pip_cmd = "pip install -r requirements.txt"
    if run_command(pip_cmd, "Installing dependencies"):
        print("✓ All dependencies installed successfully")
    else:
        print("⚠️  Some dependencies may have failed to install")


def setup_environment_file():
    """Create .env file from template"""
    print_header("QMail Setup - Step 3: Configuration")
    
    if Path(".env").exists():
        print("✓ .env file already exists")
        overwrite = input("  Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("  Keeping existing .env file")
            return
    
    try:
        with open(".env.example", "r") as src:
            content = src.read()
        
        with open(".env", "w") as dst:
            dst.write(content)
        
        print("✓ Created .env file from template")
        print("\n📝 Important: Edit .env file with your settings:")
        print("   - Set a secure SECRET_KEY")
        print("   - Configure SMTP/IMAP settings")
        print("   - Adjust QKD settings if needed")
    
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")


def initialize_database():
    """Initialize the database"""
    print_header("QMail Setup - Step 4: Database")
    
    if run_command("python -m qmail.core.init_db", "Initializing database"):
        print("✓ Database initialized successfully")
        print("\n📝 Default admin credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  CHANGE THIS PASSWORD AFTER FIRST LOGIN!")
    else:
        print("⚠️  Database initialization may have failed")


def run_tests():
    """Run test suite"""
    print_header("QMail Setup - Step 5: Tests (Optional)")
    
    run_tests = input("Run tests? (Y/n): ").strip().lower()
    
    if run_tests != 'n':
        if run_command("pytest tests/ -v", "Running tests"):
            print("✓ All tests passed")
        else:
            print("⚠️  Some tests failed")


def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")
    
    print("🎉 QMail is ready to use!\n")
    print("Next steps:")
    print("  1. Activate virtual environment:")
    if sys.platform == "win32":
        print("     .\\venv\\Scripts\\activate")
    else:
        print("     source venv/bin/activate")
    
    print("\n  2. Edit .env file with your settings:")
    print("     notepad .env")
    
    print("\n  3. Run the application:")
    print("     python run.py")
    
    print("\n  4. Open browser and navigate to:")
    print("     http://localhost:5000")
    
    print("\n  5. Login with default credentials:")
    print("     Username: admin")
    print("     Password: admin123")
    
    print("\n📚 Documentation:")
    print("   - Quick Start: QUICKSTART.md")
    print("   - Full Docs: docs/CONTEXT.md")
    print("   - Demo: python demo.py")
    
    print("\n" + "=" * 60 + "\n")


def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("  QMail - Quantum-Secure Email Client")
    print("  Automated Setup Script")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Run setup steps
    setup_environment()
    
    print("\n" + "=" * 60)
    cont = input("Continue with dependency installation? (Y/n): ").strip().lower()
    if cont == 'n':
        print("Setup cancelled")
        return
    
    install_dependencies()
    setup_environment_file()
    initialize_database()
    run_tests()
    print_next_steps()


if __name__ == '__main__':
    main()
