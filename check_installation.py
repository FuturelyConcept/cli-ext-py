#!/usr/bin/env python3
"""
Check Gemini CLI integration installation
"""

import os
import sys
import json
from pathlib import Path


def check_gemini_installation():
    """Check if Gemini CLI integration is properly installed"""
    
    print("Checking Gemini CLI integration installation...\n")
    
    # Check .gemini directory
    gemini_dir = Path.home() / '.gemini'
    print(f"Gemini directory: {gemini_dir}")
    print(f"Exists: {'YES' if gemini_dir.exists() else 'NO'}")
    
    if not gemini_dir.exists():
        print("ERROR: .gemini directory not found!")
        return False
    
    # Check extensions directory
    extensions_dir = gemini_dir / 'extensions'
    print(f"\nExtensions directory: {extensions_dir}")
    print(f"Exists: {'YES' if extensions_dir.exists() else 'NO'}")
    
    if extensions_dir.exists():
        print("Extensions found:")
        for item in extensions_dir.iterdir():
            print(f"  - {item.name}")
    
    # Check video-recording extension
    video_ext_dir = extensions_dir / 'video-recording'
    print(f"\nVideo extension directory: {video_ext_dir}")
    print(f"Exists: {'YES' if video_ext_dir.exists() else 'NO'}")
    
    if video_ext_dir.exists():
        print("Video extension files:")
        for item in video_ext_dir.iterdir():
            print(f"  - {item.name}")
    
    # Check commands directory
    commands_dir = gemini_dir / 'commands'
    print(f"\nCommands directory: {commands_dir}")
    print(f"Exists: {'YES' if commands_dir.exists() else 'NO'}")
    
    if commands_dir.exists():
        print("Command files:")
        for item in commands_dir.iterdir():
            print(f"  - {item.name}")
        
        # Check video recording command
        video_cmd_file = commands_dir / 'video_recording.json'
        print(f"\nVideo recording command: {video_cmd_file}")
        print(f"Exists: {'YES' if video_cmd_file.exists() else 'NO'}")
        
        if video_cmd_file.exists():
            try:
                with open(video_cmd_file, 'r') as f:
                    cmd_config = json.load(f)
                print("Command configuration:")
                print(json.dumps(cmd_config, indent=2))
            except Exception as e:
                print(f"Error reading command file: {e}")
    
    # Check if Gemini CLI supports extensions
    print(f"\n" + "="*50)
    print("CHECKING GEMINI CLI EXTENSION SUPPORT")
    print("="*50)
    
    # Try to get Gemini CLI help to see if it mentions extensions
    import subprocess
    try:
        result = subprocess.run(['gemini', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            help_text = result.stdout.lower()
            print("Gemini CLI Help Analysis:")
            print(f"  - Mentions 'extension': {'YES' if 'extension' in help_text else 'NO'}")
            print(f"  - Mentions 'command': {'YES' if 'command' in help_text else 'NO'}")
            print(f"  - Mentions 'tool': {'YES' if 'tool' in help_text else 'NO'}")
            
            if 'extension' not in help_text and 'command' not in help_text:
                print("\nWARNING: This version of Gemini CLI might not support extensions!")
                print("You may need to use a different integration method.")
        else:
            print("Could not get Gemini CLI help")
    except FileNotFoundError:
        print("Gemini CLI not found in PATH")
    except Exception as e:
        print(f"Error checking Gemini CLI: {e}")
    
    return True


def suggest_alternative_integration():
    """Suggest alternative integration methods"""
    
    print(f"\n" + "="*50)
    print("ALTERNATIVE INTEGRATION METHODS")
    print("="*50)
    
    print("""
Since Gemini CLI might not support our extension format, here are alternatives:

1. DIRECT COMMAND METHOD:
   Instead of 'start a video recording', try:
   - Run: python C:\\Users\\Deepika_Akshaj\\.gemini\\extensions\\video-recording\\gemini_video_handler.py record
   - Then paste the output into Gemini CLI

2. ALIAS METHOD (Windows PowerShell):
   Add this to your PowerShell profile:
   function Start-VideoRecording {
       python "C:\\Users\\Deepika_Akshaj\\.gemini\\extensions\\video-recording\\gemini_video_handler.py" record
   }

3. BATCH FILE METHOD:
   Create a video_record.bat file:
   @echo off
   python "C:\\Users\\Deepika_Akshaj\\.gemini\\extensions\\video-recording\\gemini_video_handler.py" record

4. MANUAL WORKFLOW:
   - Run: python cli_video_ext.py record
   - Copy the output
   - Paste into Gemini CLI with: "Please analyze this video context:"

Would you like me to create any of these alternative methods?
""")


def main():
    """Main function"""
    check_gemini_installation()
    suggest_alternative_integration()
    
    print(f"\n" + "="*50)
    print("NEXT STEPS")
    print("="*50)
    print("1. Check if files are installed correctly (shown above)")
    print("2. Verify Gemini CLI version supports extensions")
    print("3. Try alternative integration methods if needed")
    print("4. Test direct command execution")


if __name__ == '__main__':
    main()