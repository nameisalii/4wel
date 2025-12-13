#!/usr/bin/env python3
"""
Prepare project for GitHub push
This script prepares everything needed to push to GitHub
"""

import os
import subprocess
import sys
from pathlib import Path

def check_git_available():
    """Check if git is available"""
    try:
        result = subprocess.run(['git', '--version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False

def init_repo():
    """Initialize git repository"""
    print("📦 Initializing git repository...")
    try:
        subprocess.run(['git', 'init'], check=True)
        print("✅ Git repository initialized")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    except FileNotFoundError:
        print("❌ Git not found. Please install Xcode Command Line Tools:")
        print("   Run: xcode-select --install")
        return False

def add_files():
    """Add all files to git"""
    print("📝 Adding files to git...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Files added")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to add files: {e}")
        return False

def commit():
    """Commit changes"""
    print("💾 Committing changes...")
    try:
        subprocess.run(['git', 'commit', '-m', 
                       'Add robot navigation training project with extended training scripts'], 
                      check=True)
        print("✅ Changes committed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to commit: {e}")
        return False

def create_branch():
    """Create main branch"""
    print("🌿 Creating main branch...")
    try:
        subprocess.run(['git', 'branch', '-M', 'main'], check=True)
        print("✅ Branch created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Branch creation failed (may already exist): {e}")
        return True  # Not critical

def main():
    print("=" * 70)
    print("🚀 Preparing Project for GitHub")
    print("=" * 70)
    print()
    
    if not check_git_available():
        print()
        print("=" * 70)
        print("❌ Git is not available")
        print("=" * 70)
        print()
        print("Please install Xcode Command Line Tools first:")
        print("  1. Run: xcode-select --install")
        print("  2. Wait for installation to complete (10-15 minutes)")
        print("  3. Run this script again: python3 prepare_for_github.py")
        print()
        print("Alternatively, you can:")
        print("  - Use GitHub Desktop (https://desktop.github.com/)")
        print("  - Upload files via GitHub web interface")
        print()
        return False
    
    os.chdir(Path(__file__).parent)
    
    success = True
    success = init_repo() and success
    success = add_files() and success
    success = commit() and success
    success = create_branch() and success
    
    if success:
        print()
        print("=" * 70)
        print("✅ Repository Ready for GitHub!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Create a repository on GitHub: https://github.com/new")
        print("   (Don't initialize with README, .gitignore, or license)")
        print()
        print("2. Add remote and push:")
        print("   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git")
        print("   git push -u origin main")
        print()
        print("Or use the automated script:")
        print("   ./push_to_github.sh")
        print()
    else:
        print()
        print("=" * 70)
        print("⚠️  Some steps failed. Please check the errors above.")
        print("=" * 70)
    
    return success

if __name__ == "__main__":
    sys.exit(0 if main() else 1)


