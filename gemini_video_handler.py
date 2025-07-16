#!/usr/bin/env python3
"""
Gemini CLI Video Recording Handler
This script handles video recording requests and processes the results for Gemini CLI
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path


class GeminiVideoHandler:
    """Handles video recording workflow for Gemini CLI"""
    
    def __init__(self):
        self.current_dir = Path(__file__).parent
        self.video_ext_script = self.current_dir / 'cli_video_ext.py'
        
    def start_recording(self):
        """Start the video recording process"""
        video_recorder_path = self.current_dir / 'video_recorder.py'

        command = [sys.executable, str(video_recorder_path)]

        try:
            # Start the video recorder as a separate process
            # Use Popen to run it detached, so it doesn't block the current process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )
            stdout, stderr = process.communicate(timeout=300) # 5 minutes timeout

            if process.returncode == 0:
                session_dir_line = next((line for line in stderr.splitlines() if line.startswith("SESSION_DIR:")), None)
                if session_dir_line:
                    session_dir_path = session_dir_line.replace("SESSION_DIR:", "").strip()
                    context_file_path = Path(session_dir_path) / "analysis.txt"
                    if context_file_path.exists():
                        with open(context_file_path, "r", encoding="utf-8") as f:
                            context_content = f.read()
                        return context_content
                    else:
                        return "Recording failed: context file not found"
                else:
                    return "Recording failed: session directory not found"
            else:
                error_message = f"Video recording process failed with exit code {process.returncode}.\nStdout: {stdout.strip()}\nStderr: {stderr.strip()}"

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return "Recording timed out"
        except Exception as e:
            return f"Recording error: {str(e)}"
    
    def process_video_context(self, context):
        """Process the video context and prepare it for Gemini"""
        if not context or "failed" in context.lower():
            return context
        
        # Just return the file reference if it looks like a file path message
        if context and "Analysis: @" in context:
            return context
        processed_context = context
        
        return processed_context
    
    def handle_video_request(self, user_message):
        """Handle user's video recording request"""
        
        # Check if this is a video recording request
        video_keywords = [
            'start a video recording',
            'record a video',
            'video recording',
            'show you the problem',
            'demonstrate the issue',
            'record my screen'
        ]
        
        if any(keyword in user_message.lower() for keyword in video_keywords):
            # Start video recording
            context = self.start_recording()
            
            # Process and return the context
            return self.process_video_context(context)
        
        return None


def main():
    """Main function for command-line usage"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_video_handler.py <command>")
        print("Commands:")
        print("  record    - Start video recording")
        print("  test      - Test the integration")
        return 1
    
    handler = GeminiVideoHandler()
    command = sys.argv[1]
    
    if command == 'record':
        context = handler.start_recording()
        processed = handler.process_video_context(context)
        print(processed)
        
    elif command == 'test':
        result = handler.start_recording()
        print(result)
            
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())