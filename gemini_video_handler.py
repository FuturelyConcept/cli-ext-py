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
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )
            stdout, stderr = process.communicate(timeout=300)

            if process.returncode == 0:
                # Look for the CSV file reference in stdout
                if stdout and "@" in stdout:
                    csv_path = stdout.strip()
                    # Create enhanced prompt for Gemini
                    enhanced_prompt = f"""Please load this word_timeline.csv file on path below.
This file contains transcribed audio text of the video along with timeline in seconds.
Analyze the content and identify 3-5 specific timestamps where frames should be extracted to accurately capture what the user is demonstrating.

Respond ONLY with timestamps in this exact format:
frame1: X.X seconds
frame2: X.X seconds  
frame3: X.X seconds

{csv_path}"""
                    return enhanced_prompt
                else:
                    return "Recording completed but no analysis generated"
            else:
                return "Recording failed"

        except subprocess.TimeoutExpired:
            process.kill()
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
        print("Usage: python3 gemini_video_handler.py <command>", file=sys.stderr)
        print("Commands:", file=sys.stderr)
        print("  record    - Start video recording", file=sys.stderr)
        return 1
    
    handler = GeminiVideoHandler()
    command = sys.argv[1]
    
    if command == 'record':
        context = handler.start_recording()
        processed = handler.process_video_context(context)
        print(processed)
        
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())