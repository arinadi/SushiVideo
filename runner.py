import os
import sys
import time
import subprocess
import shutil

# Record initialization time
os.environ['INIT_START'] = str(time.time())

REPO_URL = "https://github.com/arinadi/SushiVideo.git"
CLONE_DIR = "sushivideo_repo"

print("🍣 SushiVideo Runner: Bootstrapping environment...")

# 1. Clone or update repository
if not os.path.exists(CLONE_DIR):
    print("📥 Cloning repository...")
    subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)
else:
    print("🔄 Updating repository...")
    subprocess.run(["git", "-C", CLONE_DIR, "pull"], check=True)

# Change working directory to the cloned repo
os.chdir(CLONE_DIR)

# 2. Create required directories
for d in ['uploads', 'transcripts', 'video_clipper']:
    os.makedirs(d, exist_ok=True)
print("📁 Created working directories.")

# 3. Install dependencies
print("📦 Installing dependencies (this may take a minute)...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], check=True)

# 4. Launch start.py
print("🚀 Launching start.py...")
os.environ['PYTHONPATH'] = os.getcwd()
subprocess.run([sys.executable, "start.py"])
