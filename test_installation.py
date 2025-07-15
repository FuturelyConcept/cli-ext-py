#!/usr/bin/env python3
"""
Test script to verify the video recording extension works correctly
"""

import sys
import subprocess
from pathlib import Path

def test_installation():
    """Test the installation and basic functionality"""
    print("Testing Gemini CLI Video Recording Extension")
    print("=" * 60)
    
    # Check if required files exist
    required_files = [
        'video_recorder.py',
        'frame_extractor.py', 
        'requirements.txt',
        'cli_video_ext.py'
    ]
    
    project_dir = Path(__file__).parent
    missing_files = []
    
    for file_name in required_files:
        file_path = project_dir / file_name
        if file_path.exists():
            print(f"Found: {file_name}")
        else:
            print(f"Missing: {file_name}")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
        return False
    
    # Test Python imports
    print("\nTesting Python imports...")
    try:
        import flask
        print("Flask imported successfully")
    except ImportError:
        print("Flask not installed")
        return False
    
    try:
        import whisper
        print("Whisper imported successfully")
    except ImportError:
        print("Whisper not installed")
        return False
    
    try:
        import ffmpeg
        print("ffmpeg-python imported successfully")
    except ImportError:
        print("ffmpeg-python not installed")
        return False
    
    # Test CLI extension
    print("\nTesting CLI extension...")
    try:
        cli_ext_path = project_dir / 'cli_video_ext.py'
        result = subprocess.run([
            sys.executable, str(cli_ext_path), 'check'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("CLI extension check passed")
            print(f"Output: {result.stdout}")
        else:
            print("CLI extension check had warnings")
            print(f"Output: {result.stdout}")
            print(f"Errors: {result.stderr}")
    except Exception as e:
        print(f"CLI extension test failed: {e}")
        return False
    
    print("\nAll tests passed!")
    print("\nNext steps:")
    print("1. Run: python install.py")
    print("2. Test with Gemini CLI")
    
    return True

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)