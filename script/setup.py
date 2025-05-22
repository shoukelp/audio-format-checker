import subprocess
import sys
import shutil
import socket

def command_exists(cmd):
    return shutil.which(cmd) is not None

def install_ffmpeg():
    print("\n[+] Checking and installing ffmpeg...")

    if command_exists("pkg"):
        print("Running: pkg install -y ffmpeg")
        subprocess.run(["pkg", "install", "-y", "ffmpeg"])
    elif command_exists("apt"):
        print("Running: apt update && apt install -y ffmpeg")
        subprocess.run(["apt", "update"])
        subprocess.run(["apt", "install", "-y", "ffmpeg"])
    else:
        print("[!] Unknown package manager. Please install ffmpeg manually.")
        sys.exit(1)

def install_pip_package(package):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print(f"[+] Python package '{package}' installed.")
    except subprocess.CalledProcessError:
        print(f"[!] Failed to install Python package '{package}'.")
        sys.exit(1)

def check_internet_connection():
    print("[+] Checking internet connection...")
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("    Internet connection OK.")
        return True
    except OSError:
        print("    No internet connection. Some features (like --import lyrics) will not work.")
        return False

def main():
    if not command_exists("ffmpeg") or not command_exists("ffprobe"):
        install_ffmpeg()
    else:
        print("[+] ffmpeg and ffprobe are already installed.")

    if not command_exists("python3"):
        print("[!] Python3 not found. Please install Python3 first.")
        sys.exit(1)
    else:
        print("[+] Python3 is already installed.")

    # Ensure pip is available
    if not command_exists("pip"):
        print("\n[+] pip not found, attempting to install...")
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"])

    # Install required Python packages
    print("\n[+] Installing required Python packages...")
    install_pip_package("requests")
    install_pip_package("beautifulsoup4")

    # Check internet
    check_internet_connection()

    print("\n[✓] Setup complete. You can now run:")
    print("    ./run.sh <audiofile> [--json output.json]")
    print("    ./run.sh lrc <audiofile> --import")

if __name__ == "__main__":
    main()