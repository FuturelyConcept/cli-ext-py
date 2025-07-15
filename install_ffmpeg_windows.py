#!/usr/bin/env python3
"""
Download and install FFmpeg for Windows
This script downloads a portable version of FFmpeg for the video extension
"""

import os
import sys
import urllib.request
import zipfile
from pathlib import Path
import shutil

def download_ffmpeg():
    """Download portable FFmpeg for Windows"""
    print("Downloading FFmpeg for Windows...")
    
    # Create bin directory in the extension folder
    script_dir = Path(__file__).parent
    bin_dir = script_dir / "bin"
    bin_dir.mkdir(exist_ok=True)
    
    # FFmpeg download URL (portable version)
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    zip_path = bin_dir / "ffmpeg.zip"
    
    try:
        print("Downloading FFmpeg...")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        print(f"Downloaded to: {zip_path}")
        
        # Extract the zip file
        print("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract only the exe files we need
            for member in zip_ref.namelist():
                if member.endswith(('ffmpeg.exe', 'ffprobe.exe')):
                    # Extract to bin directory with simple name
                    filename = os.path.basename(member)
                    source = zip_ref.open(member)
                    target = open(bin_dir / filename, "wb")
                    shutil.copyfileobj(source, target)
                    target.close()
                    source.close()
                    print(f"Extracted: {filename}")
        
        # Clean up zip file
        zip_path.unlink()
        
        # Verify the files exist
        ffmpeg_exe = bin_dir / "ffmpeg.exe"
        ffprobe_exe = bin_dir / "ffprobe.exe"
        
        if ffmpeg_exe.exists() and ffprobe_exe.exists():
            print(f"✓ FFmpeg installed successfully!")
            print(f"FFmpeg: {ffmpeg_exe}")
            print(f"FFprobe: {ffprobe_exe}")
            
            # Test the installation
            import subprocess
            try:
                result = subprocess.run([str(ffmpeg_exe), '-version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print("✓ FFmpeg is working correctly!")
                    return True
                else:
                    print("✗ FFmpeg test failed")
                    return False
            except Exception as e:
                print(f"✗ FFmpeg test error: {e}")
                return False
        else:
            print("✗ FFmpeg files not found after extraction")
            return False
            
    except Exception as e:
        print(f"✗ Error downloading FFmpeg: {e}")
        return False

def main():
    """Main installation function"""
    print("FFmpeg Windows Installer for Video Recording Extension")
    print("=" * 60)
    
    # Check if we're on Windows
    if os.name != 'nt':
        print("This script is for Windows only")
        return 1
    
    # Check if FFmpeg is already available
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ FFmpeg is already installed and available in PATH")
            print("No need to download portable version.")
            return 0
    except:
        pass  # FFmpeg not in PATH, continue with download
    
    # Download and install portable FFmpeg
    if download_ffmpeg():
        print("\n" + "=" * 60)
        print("INSTALLATION COMPLETE!")
        print("=" * 60)
        print("FFmpeg has been installed as a portable version.")
        print("The video recording extension will now work properly.")
        print("\nYou can now run:")
        print("  python test_windows.py [video_file]")
        return 0
    else:
        print("\n" + "=" * 60)
        print("INSTALLATION FAILED!")
        print("=" * 60)
        print("Please install FFmpeg manually from https://ffmpeg.org/download.html")
        return 1

if __name__ == "__main__":
    sys.exit(main())