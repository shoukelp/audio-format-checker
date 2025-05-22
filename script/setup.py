import subprocess
import sys
import shutil

def command_exists(cmd):
    return shutil.which(cmd) is not None

def install_ffmpeg():
    print("Checking and installing ffmpeg...")

    if command_exists("pkg"):
        print("Running: pkg install -y ffmpeg")
        subprocess.run(["pkg", "install", "-y", "ffmpeg"])
    elif command_exists("apt"):
        print("Running: apt update && apt install -y ffmpeg")
        subprocess.run(["apt", "update"])
        subprocess.run(["apt", "install", "-y", "ffmpeg"])
    else:
        print("Unknown package manager. Please install ffmpeg manually.")
        sys.exit(1)

def main():
    if not command_exists("ffprobe"):
        print("ffprobe not found.")
        install_ffmpeg()
    else:
        print("ffprobe is already installed.")

    if not command_exists("python3"):
        print("Python3 not found. Please install Python3 first.")
        sys.exit(1)
    else:
        print("Python3 is already installed.")

    print("Setup complete. Run the script using: ./run.sh <file> [--json output.json]")

if __name__ == "__main__":
    main()