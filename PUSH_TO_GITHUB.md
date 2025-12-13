# How to Push to GitHub

## Current Issue
Git requires Xcode Command Line Tools on macOS, which are not currently installed.

## Solution Options

### Option 1: Install Xcode Command Line Tools (Recommended)

1. **Install the tools:**
   ```bash
   xcode-select --install
   ```
   A dialog will appear - click "Install" and wait 10-15 minutes.

2. **Once installed, run:**
   ```bash
   python3 prepare_for_github.py
   ```
   
   Or manually:
   ```bash
   git init
   git add .
   git commit -m "Add robot navigation training project"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

### Option 2: Use GitHub Desktop (Easiest - No Command Line Needed)

1. **Download GitHub Desktop:**
   - Visit: https://desktop.github.com/
   - Install the application

2. **Set up repository:**
   - Open GitHub Desktop
   - Click "File" → "Add Local Repository"
   - Navigate to: `/Users/alinazarov/Downloads/project_archive (1) 3`
   - Click "Add Repository"

3. **Create GitHub repository:**
   - Click "Publish repository" button
   - Choose a name and make it public/private
   - Click "Publish Repository"

### Option 3: Upload via GitHub Web Interface

1. **Create repository on GitHub:**
   - Go to: https://github.com/new
   - Create a new repository (don't initialize with README)
   - Note the repository URL

2. **Upload files:**
   - Go to your repository page
   - Click "uploading an existing file"
   - Drag and drop all files from your project folder
   - **Important:** Skip these folders/files (they're in .gitignore):
     - `checkpoints/`
     - `models/`
     - `logs/`
     - `tensorboard_logs/`
     - `*.mcap` files
     - `*.mcap.json` files
     - `__pycache__/`
   - Click "Commit changes"

### Option 4: Use the Automated Script (After Xcode Tools Install)

Once Xcode Command Line Tools are installed:

```bash
./push_to_github.sh
```

The script will guide you through adding your GitHub repository URL.

## Files to Include

✅ **Include these:**
- All `.py` files (source code)
- `requirements.txt`
- `README.md`
- `train.py`
- `robot_env.py`
- `robot_kinematics.py`
- `visualize.py`
- `mcap_writer.py`
- All files in `scripts/` folder
- `.gitignore`
- `push_to_github.sh`
- `prepare_for_github.py`

❌ **Exclude these (too large or generated):**
- `checkpoints/` folder
- `models/` folder  
- `logs/` folder
- `tensorboard_logs/` folder
- `*.mcap` files
- `*.mcap.json` files
- `__pycache__/` folders
- `*.png`, `*.jpg` (test images)

## Quick Start (Recommended)

**If you want the fastest solution right now:**

1. Install GitHub Desktop: https://desktop.github.com/
2. Open GitHub Desktop
3. File → Add Local Repository → Select your project folder
4. Click "Publish repository"
5. Done! ✅

This method doesn't require Xcode Command Line Tools.


