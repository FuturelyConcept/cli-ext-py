#!/usr/bin/env python3
"""
Create direct integration methods for Gemini CLI
"""

import os
import sys
from pathlib import Path


def create_batch_file():
    """Create a Windows batch file for video recording"""
    
    batch_content = f"""@echo off
echo Starting video recording for Gemini CLI...
python "{Path.home() / '.gemini' / 'extensions' / 'video-recording' / 'gemini_video_handler.py'}" record
pause
"""
    
    batch_file = Path.home() / '.gemini' / 'video_record.bat'
    
    try:
        with open(batch_file, 'w') as f:
            f.write(batch_content)
        print(f"Created batch file: {batch_file}")
        print("Usage: Double-click the batch file or run from command line")
        return True
    except Exception as e:
        print(f"Error creating batch file: {e}")
        return False


def create_powershell_script():
    """Create a PowerShell script for video recording"""
    
    ps_content = f"""# Video Recording Script for Gemini CLI
Write-Host "Starting video recording for Gemini CLI..." -ForegroundColor Green

$videoHandler = "{Path.home() / '.gemini' / 'extensions' / 'video-recording' / 'gemini_video_handler.py'}"
$result = python $videoHandler record

Write-Host "Video recording complete!" -ForegroundColor Green
Write-Host "Copy the output above and paste into Gemini CLI" -ForegroundColor Yellow

# Keep window open
Read-Host "Press Enter to exit"
"""
    
    ps_file = Path.home() / '.gemini' / 'video_record.ps1'
    
    try:
        with open(ps_file, 'w') as f:
            f.write(ps_content)
        print(f"Created PowerShell script: {ps_file}")
        print("Usage: Right-click and 'Run with PowerShell' or run: powershell -ExecutionPolicy Bypass -File video_record.ps1")
        return True
    except Exception as e:
        print(f"Error creating PowerShell script: {e}")
        return False


def create_direct_command_helper():
    """Create a helper script that provides the exact command to run"""
    
    helper_content = f"""#!/usr/bin/env python3
\"\"\"
Direct command helper for Gemini CLI video recording
\"\"\"

import sys
from pathlib import Path

def main():
    video_handler = Path.home() / '.gemini' / 'extensions' / 'video-recording' / 'gemini_video_handler.py'
    
    print("="*60)
    print("GEMINI CLI VIDEO RECORDING - DIRECT COMMAND")
    print("="*60)
    print()
    print("Since Gemini CLI doesn't recognize the extension automatically,")
    print("use this direct command:")
    print()
    print("COMMAND TO RUN:")
    print(f"python \\"{video_handler}\\" record")
    print()
    print("STEPS:")
    print("1. Copy the command above")
    print("2. Run it in your terminal")
    print("3. Follow the video recording instructions")
    print("4. Copy the output")
    print("5. Paste into Gemini CLI with: 'Please analyze this video context:'")
    print()
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--run':
        print("Running video recording now...")
        import subprocess
        try:
            result = subprocess.run([sys.executable, str(video_handler), 'record'])
            return result.returncode
        except Exception as e:
            print(f"Error running video recording: {{e}}")
            return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
"""
    
    helper_file = Path.home() / '.gemini' / 'video_helper.py'
    
    try:
        with open(helper_file, 'w') as f:
            f.write(helper_content)
        print(f"Created helper script: {helper_file}")
        print("Usage: python video_helper.py (shows command) or python video_helper.py --run (runs recording)")
        return True
    except Exception as e:
        print(f"Error creating helper script: {e}")
        return False


def main():
    """Main function"""
    print("Creating direct integration methods for Gemini CLI...\n")
    
    methods = [
        ("Windows Batch File", create_batch_file),
        ("PowerShell Script", create_powershell_script),
        ("Direct Command Helper", create_direct_command_helper)
    ]
    
    results = []
    for method_name, method_func in methods:
        print(f"Creating {method_name}...")
        result = method_func()
        results.append((method_name, result))
        print(f"Result: {'SUCCESS' if result else 'FAILED'}")
        print()
    
    print("="*60)
    print("SUMMARY")
    print("="*60)
    
    success_count = 0
    for method_name, result in results:
        status = "SUCCESS" if result else "FAILED"
        print(f"{method_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\\nCreated {success_count}/{len(methods)} integration methods")
    
    if success_count > 0:
        print("\\nYou can now use video recording with Gemini CLI using these methods!")
        print("\\nRECOMMENDED WORKFLOW:")
        print("1. Run the video recording command")
        print("2. Copy the generated context")
        print("3. In Gemini CLI, say: 'Please analyze this video context:' and paste the context")
    
    return 0 if success_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())