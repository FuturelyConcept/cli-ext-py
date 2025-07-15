#!/usr/bin/env python3
"""
Gemini CLI Video Extension Integration
This script integrates the video recording functionality with Gemini CLI
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path


def create_gemini_command():
    """Create a Gemini CLI command for video recording"""
    
    # Get the current directory where our video recorder is located
    current_dir = Path(__file__).parent
    video_ext_script = current_dir / 'cli_video_ext.py'
    
    # Create the command definition
    command_def = {
        "name": "video",
        "description": "Record screen video with intelligent frame extraction and transcription",
        "type": "tool",
        "command": f"python3 {video_ext_script} record",
        "working_directory": str(current_dir),
        "timeout": 300,  # 5 minutes timeout
        "examples": [
            {
                "input": "start a video recording and i will tell you the problem i want you to solve",
                "description": "Initiates video recording with AI-guided frame extraction"
            },
            {
                "input": "record a video to show you the bug",
                "description": "Records screen activity with intelligent analysis"
            }
        ]
    }
    
    return command_def


def setup_gemini_integration():
    """Set up the integration with Gemini CLI"""
    
    # Check if we're in a Gemini CLI environment
    gemini_dir = Path.home() / '.gemini'
    if not gemini_dir.exists():
        print("Gemini CLI not found. Please install Gemini CLI first.")
        return False
    
    # Create commands directory if it doesn't exist
    commands_dir = gemini_dir / 'commands'
    commands_dir.mkdir(exist_ok=True)
    
    # Create the video command file
    video_command_file = commands_dir / 'video.json'
    command_def = create_gemini_command()
    
    with open(video_command_file, 'w') as f:
        json.dump(command_def, f, indent=2)
    
    print(f"✅ Video command registered with Gemini CLI")
    print(f"📁 Command file: {video_command_file}")
    print(f"🎬 You can now use: 'start a video recording' in Gemini CLI")
    
    return True


def create_video_workflow_prompt():
    """Create a workflow prompt for Gemini to handle video recording requests"""
    
    workflow_prompt = """
# Video Recording Workflow for Gemini CLI

When a user asks to "start a video recording" or mentions recording/showing a problem:

1. **Initiate Recording**: Execute the video recording command
2. **Guide User**: Tell them to:
   - Demonstrate the problem clearly
   - Speak about what they want fixed
   - Show the specific UI elements or code sections
3. **Process Results**: After recording completes, you'll receive:
   - Transcript with timeline
   - Intelligently extracted frames
   - AI analysis of the issues
4. **Take Action**: Use the context to implement fixes or provide solutions

## Example Interaction:

User: "start a video recording and i will tell you the problem i want you to solve"

Response: "I'll start a video recording for you. Please demonstrate the problem you'd like me to solve and speak clearly about what you want fixed."

[Execute video recording command]

[After recording completes, analyze the generated context and implement the requested changes]
"""
    
    return workflow_prompt


def main():
    """Main function to set up Gemini integration"""
    
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        print("Setting up Gemini CLI integration...")
        if setup_gemini_integration():
            print("\n🎉 Integration setup complete!")
            print("\nNext steps:")
            print("1. Open Gemini CLI")
            print("2. Say: 'start a video recording and i will tell you the problem i want you to solve'")
            print("3. Gemini will launch the video recorder")
            print("4. Record your problem demonstration")
            print("5. Gemini will analyze the results and take action")
        else:
            print("❌ Integration setup failed")
            return 1
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--workflow':
        print("Video Recording Workflow:")
        print(create_video_workflow_prompt())
    
    else:
        print("Gemini CLI Video Extension Integration")
        print("Usage:")
        print("  python3 gemini_integration.py --setup     # Set up integration")
        print("  python3 gemini_integration.py --workflow  # Show workflow guide")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())