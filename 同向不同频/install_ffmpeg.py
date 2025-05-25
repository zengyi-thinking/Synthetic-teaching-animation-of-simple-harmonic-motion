import os
import sys
import subprocess
import platform
import zipfile
import urllib.request
import shutil

def install_ffmpeg_windows():
    """Download and extract FFmpeg for Windows"""
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = "ffmpeg.zip"
    extract_dir = "ffmpeg_temp"
    
    print("Downloading FFmpeg (this may take a while)...")
    try:
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
    except Exception as e:
        print(f"Error downloading FFmpeg: {e}")
        return False
    
    print("Extracting FFmpeg...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the bin directory in the extracted files
        bin_dir = None
        for root, dirs, files in os.walk(extract_dir):
            if "bin" in dirs:
                bin_dir = os.path.join(root, "bin")
                break
        
        if not bin_dir:
            print("Could not find bin directory in extracted files")
            return False
        
        # Create ffmpeg directory in the current directory
        if not os.path.exists("ffmpeg"):
            os.makedirs("ffmpeg")
        
        # Copy ffmpeg.exe, ffprobe.exe to ffmpeg directory
        for file in ["ffmpeg.exe", "ffprobe.exe"]:
            if os.path.exists(os.path.join(bin_dir, file)):
                shutil.copy2(os.path.join(bin_dir, file), os.path.join("ffmpeg", file))
        
        # Clean up
        os.remove(zip_path)
        shutil.rmtree(extract_dir)
        
        print("FFmpeg has been downloaded to the 'ffmpeg' directory")
        
        # Add to PATH temporarily
        os.environ["PATH"] += os.pathsep + os.path.abspath("ffmpeg")
        
        return True
    except Exception as e:
        print(f"Error extracting FFmpeg: {e}")
        return False

def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    print("FFmpeg Installation Helper")
    print("=========================")
    
    # Check if FFmpeg is already installed
    if check_ffmpeg():
        print("FFmpeg is already installed and available in your PATH.")
        return
    
    system = platform.system()
    
    if system == "Windows":
        print("FFmpeg not found. Installing FFmpeg for Windows...")
        success = install_ffmpeg_windows()
        
        if success:
            print("\nFFmpeg installed successfully!")
            print("\nTo run the harmonic motion simulation, use:")
            print("python main.py")
        else:
            print("\nFFmpeg installation failed. Please install it manually:")
            print("1. Download FFmpeg from https://ffmpeg.org/download.html")
            print("2. Extract the files")
            print("3. Add the bin folder to your PATH")
    else:
        print("This script can only install FFmpeg on Windows.")
        print("Please install FFmpeg manually for your platform:")
        
        if system == "Darwin":  # macOS
            print("Run: brew install ffmpeg")
        elif system == "Linux":
            print("Run: sudo apt install ffmpeg (for Ubuntu/Debian)")
            print("     sudo dnf install ffmpeg (for Fedora)")
            print("     sudo pacman -S ffmpeg (for Arch Linux)")

if __name__ == "__main__":
    main() 