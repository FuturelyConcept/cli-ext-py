#!/usr/bin/env python3
"""
Video Recording Extension for Gemini CLI
Python equivalent of the Node.js extension integration pattern
"""

import json
import sys
import asyncio
from pathlib import Path
from gemini_video_handler import GeminiVideoHandler

class VideoExtension:
    """Main extension class for Gemini CLI integration"""
    
    def __init__(self):
        self.video_handler = GeminiVideoHandler()
        
        # Extension metadata (equivalent to Node.js module.exports)
        self.name = 'video-recording'
        self.version = '1.0.0'
        self.description = 'AI-guided video recording with intelligent frame extraction'
        
        # Command definitions (equivalent to Node.js commands object)
        self.commands = {
            'video': {
                'description': 'Record screen video with AI-guided intelligent frame extraction',
                'action': self.start_video_capture
            }
        }
        
        # Extension configuration
        self.config = {
            'privacy': {
                'dataRetention': 'session-only',
                'cloudSync': False,
                'analytics': False
            },
            'permissions': [
                'screen-capture',
                'audio-recording',
                'local-file-system'
            ]
        }
    
    def start_video_capture(self):
        """Main entry point for video command - equivalent to Node.js startVideoCapture"""
        try:
            print("Starting AI-guided video recording...", file=sys.stderr)
            
            # Start recording process
            context = self.video_handler.start_recording()
            
            if context:
                # Process the video context
                processed_context = self.video_handler.process_video_context(context)
                return processed_context
            else:
                return "Video recording completed but no context was generated."
                
        except Exception as e:
            error_msg = f"Error during video capture: {str(e)}"
            print(error_msg, file=sys.stderr)
            return error_msg

# Create global extension instance
extension = VideoExtension()

def get_extension_info():
    """Return extension metadata for CLI discovery"""
    return {
        'name': extension.name,
        'version': extension.version,
        'description': extension.description,
        'commands': extension.commands,
        'config': extension.config
    }

def handle_command(command_name, *args):
    """Handle command execution"""
    if command_name in extension.commands:
        command = extension.commands[command_name]
        action = command['action']
        return action(*args)
    else:
        raise ValueError(f"Unknown command: {command_name}")

def main():
    """Main entry point for CLI integration"""
    if len(sys.argv) < 2:
        print("Usage: python index.py <command> [args...]", file=sys.stderr)
        print("Available commands:", file=sys.stderr)
        for cmd_name, cmd_info in extension.commands.items():
            print(f"  {cmd_name}: {cmd_info['description']}", file=sys.stderr)
        return 1
    
    command_name = sys.argv[1]
    args = sys.argv[2:]
    
    try:
        result = handle_command(command_name, *args)
        if result:
            print(result)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

# For compatibility with different CLI integration methods
if __name__ == "__main__":
    sys.exit(main())