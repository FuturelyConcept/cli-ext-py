#!/usr/bin/env python3
"""
Windows-specific installer for Gemini CLI Video Recording Extension
Detects correct Python executable and configures accordingly
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def detect_python_executable():
    """Detect the correct Python executable name"""
    possible_names = ['python.exe', 'python3.exe', 'python', 'python3']
    
    for name in possible_names:
        try:
            result = subprocess.run([name, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"[SUCCESS] Found Python: {name}")
                return name
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    print("[ERROR] No Python executable found")
    return None

def find_gemini_directory():
    """Find Gemini CLI installation directory"""
    # Windows-specific paths
    possible_paths = [
        Path.home() / ".gemini",
        Path("C:/Users") / os.getenv('USERNAME', '') / ".gemini",
        Path(os.path.expanduser("~/.gemini")),
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "extensions").exists():
            return path
    
    return None

def install_extension():
    """Install the video recording extension"""
    print("Windows Installer for Gemini CLI Video Recording Extension")
    print("=" * 65)
    
    # Step 1: Detect Python
    python_exe = detect_python_executable()
    if not python_exe:
        print("[ERROR] Python not found. Please install Python and try again.")
        return False
    
    # Step 2: Find Gemini directory
    gemini_dir = find_gemini_directory()
    if not gemini_dir:
        print("[ERROR] Gemini CLI installation not found")
        print("Please ensure Gemini CLI is installed at ~/.gemini")
        return False
    
    print(f"[SUCCESS] Found Gemini CLI at: {gemini_dir}")
    
    # Step 3: Setup extension directory
    extension_dir = gemini_dir / "extensions" / "video-recording"
    extension_dir.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    for subdir in ['uploads', 'frames', 'context']:
        (extension_dir / subdir).mkdir(exist_ok=True)
    
    print(f"[SUCCESS] Created extension directory: {extension_dir}")
    
    # Step 4: Copy files
    script_dir = Path(__file__).parent
    essential_files = [
        'index.py',
        'gemini_video_handler.py',
        'video_recorder.py',
        'cli_video_ext.py'
    ]
    
    copied_files = []
    for file in essential_files:
        source = script_dir / file
        if source.exists():
            shutil.copy2(source, extension_dir / file)
            copied_files.append(file)
            print(f"[SUCCESS] Copied: {file}")
        else:
            print(f"[ERROR] Missing: {file}")
    
    if len(copied_files) < len(essential_files):
        print("[ERROR] Some essential files are missing")
        return False

    # Create a main.py that points to index.py for Gemini's internal lookup
    main_py_path = extension_dir / "main.py"
    with open(main_py_path, 'w') as f:
        f.write("import sys\nfrom index import main\nif __name__ == \"__main__\":\n    sys.exit(main())")
    print(f"[SUCCESS] Created {main_py_path.name} as a pointer to index.py")
    
    # Step 5: Create Windows-specific configuration
    config = {
        "name": "video-recording",
        "version": "1.0.0",
        "main": "index.py",
        "description": "AI-guided video recording with intelligent frame extraction for development assistance",
        
        "contextFileName": "workflow_instructions.md",
        "excludeTools": [],
        "config": {
            "privacy": {
                "dataRetention": "session-only",
                "cloudSync": False,
                "analytics": False
            },
            "permissions": [
                "screen-capture",
                "audio-recording",
                "local-file-system"
            ]
        }
    }
    
    config_path = extension_dir / "gemini-extension.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"[SUCCESS] Created configuration with Python executable: {python_exe}")
    
    # Step 6: Create workflow instructions
    workflow_content = f"""# Video Recording Extension

## Quick Start
1. Restart Gemini CLI
2. Say: "start a video recording and i will tell you the problem i want you to solve"
3. Record your screen and explain the issue
4. Get AI-assisted help based on visual context

## Configuration
- Python executable: {python_exe}
- Extension directory: {extension_dir}

## Dependencies Required
Install these Python packages:
```cmd
pip install opencv-python openai-whisper flask requests
```

## Troubleshooting
If the extension doesn't work:
1. Make sure Python dependencies are installed
2. Restart Gemini CLI
3. Check that {python_exe} is in your PATH
"""
    
    with open(extension_dir / "workflow_instructions.md", 'w') as f:
        f.write(workflow_content)
    
    print("[SUCCESS] Created workflow instructions")
    
    # Step 7: Test the command
    print("\n[INFO] Testing extension...")
    try:
        result = subprocess.run([
            python_exe, str(extension_dir / "index.py")
        ], capture_output=True, text=True, timeout=10, cwd=str(extension_dir))
        
        if "Available commands" in result.stderr:
            print("[SUCCESS] Extension command works correctly")
        else:
            print("[WARNING]  Extension test completed with warnings")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
    except Exception as e:
        print(f"[WARNING]  Extension test failed: {e}")
    
    # Success message
    print("\n" + "=" * 65)
    print("[INFO] INSTALLATION COMPLETE!")
    print("=" * 65)
    print(f"Extension installed at: {extension_dir}")
    print(f"Using Python executable: {python_exe}")
    print("\n[INFO] DEPENDENCIES:")
    print("Install these Python packages:")
    print("  pip install opencv-python openai-whisper flask requests")
    print("\n[INFO] NEXT STEPS:")
    print("1. Install the dependencies above")
    print("2. Restart Gemini CLI")
    print("3. Try: 'start a video recording and i will tell you the problem i want you to solve'")
    
    return True

if __name__ == "__main__":
    success = install_extension()
    sys.exit(0 if success else 1)