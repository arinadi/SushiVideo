import os
import sys
import subprocess

print("🍣 SushiVideo: Checking hardware...")

# 1. Check GPU via nvidia-smi
try:
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("nvidia-smi failed.")
    print("✅ GPU detected successfully.")
except Exception as e:
    print("\n❌ FATAL ERROR: No GPU detected!")
    print("SushiVideo requires a GPU to run Whisper and FFmpeg efficiently.")
    print("Please change your Colab runtime to T4 GPU (Runtime > Change runtime type > Hardware accelerator > T4 GPU).")
    sys.exit(1)

# 2. Set environment overrides
os.environ['TRANSCRIPTION_MODE'] = 'WHISPER'

# 3. Launch main orchestrator
print("🚀 Starting main application...")
try:
    # We will implement main.py in Module 8
    if os.path.exists("main.py"):
        subprocess.run([sys.executable, "main.py"])
    else:
        print("⚠️ main.py not found yet. (Module 8 implementation pending)")
except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
except Exception as e:
    print(f"\n❌ Application crashed: {e}")
    sys.exit(1)
