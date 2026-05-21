import os
import sys
import subprocess

REPO_URL = "https://github.com/arinadi/SushiVideo.git"
CLONE_DIR = "sushivideo_repo"

print("🍣 SushiVideo Tests: Bootstrapping environment...")

# 1. Clone or update repository
if not os.path.exists(CLONE_DIR):
    print("📥 Cloning repository...")
    subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True)
else:
    print("🔄 Updating repository...")
    subprocess.run(["git", "-C", CLONE_DIR, "pull"], check=True)

os.chdir(CLONE_DIR)

# 2. Install dependencies
print("📦 Installing dependencies (flake8, pytest, pytest-asyncio)...")
subprocess.run([sys.executable, "-m", "pip", "install", "flake8", "pytest", "pytest-asyncio", "-q"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"], check=True)

# 3. Run Linter
print("🔍 Running flake8 on Python files...")
result_lint = subprocess.run([
    sys.executable, "-m", "flake8", ".",
    "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"
])

if result_lint.returncode == 0:
    print("✅ Linting passed successfully! No syntax or undefined name errors.")
else:
    print("❌ Linting failed.")

# 4. Run Pytest
print("\n🧪 Running Pytest (TDD)...")
result_test = subprocess.run([sys.executable, "-m", "pytest", "tests/"])

if result_lint.returncode == 0 and result_test.returncode == 0:
    print("\n✅ All checks (Lint & Tests) passed successfully!")
else:
    print("\n❌ Checks failed.")
    sys.exit(1)
