import os
import sys
import subprocess

REPO_URL = "https://github.com/arinadi/SushiVideo.git"
CLONE_DIR = "sushivideo_repo"

print("🍣 SushiVideo Linter: Bootstrapping environment...")

# 1. Clone or update repository
if not os.path.exists(CLONE_DIR):
    print("📥 Cloning repository...")
    subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)
else:
    print("🔄 Updating repository...")
    subprocess.run(["git", "-C", CLONE_DIR, "pull"], check=True)

os.chdir(CLONE_DIR)

# 2. Install linter
print("📦 Installing flake8...")
subprocess.run([sys.executable, "-m", "pip", "install", "flake8", "-q"], check=True)

# 3. Run Linter
print("🔍 Running flake8 on Python files...")
# We check for syntax errors and undefined names
result = subprocess.run([
    sys.executable, "-m", "flake8", ".",
    "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
])

if result.returncode == 0:
    print("✅ Linting passed successfully! No syntax or undefined name errors.")
else:
    print("❌ Linting failed.")
    sys.exit(result.returncode)
