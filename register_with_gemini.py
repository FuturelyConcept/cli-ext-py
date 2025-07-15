#!/usr/bin/env python3
"""
Register the video recording extension with Gemini CLI
This script helps configure Gemini to recognize the video recording command
"""

import json
import sys
from pathlib import Path

def register_video_extension():
    """Register the video recording extension with Gemini CLI"""
    print("Registering Video Recording Extension with Gemini CLI")
    print("=" * 60)
    
    # Path to the installed extension
    gemini_dir = Path("C:/Users/Deepika_Akshaj/.gemini")
    extension_dir = gemini_dir / "video-recording"
    
    if not extension_dir.exists():
        print("Error: Video recording extension not found!")
        print("Please run 'python install.py' first.")
        return False
    
    # Create extension registration
    extension_config = {
        "video_recording": {
            "command": f"python {extension_dir / 'record_video.py'}",
            "description": "Record screen video with AI-guided frame extraction",
            "category": "media",
            "keywords": ["video", "record", "screen", "capture", "frames"],
            "auto_detect_phrases": [
                "start video recording",
                "record my screen",
                "video capture",
                "screen recording",
                "show you what I mean",
                "let me record this"
            ]
        }
    }
    
    # Save the registration
    config_file = gemini_dir / "video-extension-config.json"
    with open(config_file, 'w') as f:
        json.dump(extension_config, f, indent=2)
    
    print(f"Extension registered at: {config_file}")
    
    # Create a simple command map
    command_map = {
        "commands": {
            "record_video": f"python {extension_dir / 'record_video.py'}",
            "start_video_recording": f"python {extension_dir / 'record_video.py'}",
            "screen_record": f"python {extension_dir / 'record_video.py'}"
        }
    }
    
    command_file = gemini_dir / "commands.json"
    with open(command_file, 'w') as f:
        json.dump(command_map, f, indent=2)
    
    print(f"Command mappings created at: {command_file}")
    
    # Create user instructions
    instructions = f"""
# Video Recording Extension - User Instructions

## Installation Complete!

Your video recording extension has been installed and configured.

## How to Use:

Simply ask Gemini to start video recording using natural language:

### Examples:
- "start a video recording"
- "record my screen so I can show you the problem"
- "let me record this issue"
- "use video recording to explain what I need"

### What happens:
1. Browser opens with screen recording dialog
2. You select screen/window to record
3. Record your screen and speak about the issue
4. Extension extracts frames and transcribes audio
5. Gemini receives video context with frames and transcript

### Manual Command:
If needed, you can run directly:
```
python {extension_dir / 'record_video.py'}
```

### Configuration Files Created:
- {config_file}
- {command_file}

## Troubleshooting:
If Gemini doesn't recognize the video recording command:
1. Restart Gemini CLI
2. Try the manual command above
3. Check that all files exist in {extension_dir}
"""
    
    instructions_file = gemini_dir / "video-recording-instructions.md"
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"User instructions created at: {instructions_file}")
    
    print("\nSUCCESS!")
    print("The video recording extension has been registered with Gemini CLI.")
    print("\nNext steps:")
    print("1. Restart Gemini CLI")
    print("2. Ask Gemini to 'start a video recording'")
    print("3. Gemini should automatically use your video recording tool")
    
    return True

if __name__ == "__main__":
    success = register_video_extension()
    sys.exit(0 if success else 1)