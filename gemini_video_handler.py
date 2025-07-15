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

        print("Starting video recording. Please look for a new browser window to open shortly.")
        print("Instructions:")
        print("1. In the browser window that opens, click 'Start Recording'.")
        print("2. Select your screen/window to record")
        print("3. Demonstrate the problem you want solved")
        print("4. SPEAK CLEARLY about what you want fixed")
        print("5. Recording will auto-stop after 30 seconds")
        print("")
        print("The video will be processed with AI-guided frame extraction...")
        print("")
        
        print(f"[DEBUG] sys.executable in gemini_video_handler: {sys.executable}", file=sys.stderr, flush=True)
        print(f"[DEBUG] video_recorder_path: {video_recorder_path}", file=sys.stderr, flush=True)
        command = [sys.executable, str(video_recorder_path)]
        print(f"[DEBUG] Executing command: {command}", file=sys.stderr, flush=True)

        try:
            # Start the video recorder as a separate process
            # Use Popen to run it detached, so it doesn't block the current process
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )
            print(f"[DEBUG] Subprocess started with PID: {process.pid}", file=sys.stderr, flush=True)

            stdout, stderr = process.communicate(timeout=300) # 5 minutes timeout

            print(f"[DEBUG] Subprocess stdout:\n{stdout}", file=sys.stderr, flush=True)
            print(f"[DEBUG] Subprocess stderr:\n{stderr}", file=sys.stderr, flush=True)

            if process.returncode == 0:
                session_dir_line = next((line for line in stderr.splitlines() if line.startswith("SESSION_DIR:")), None)
                if session_dir_line:
                    session_dir_path = session_dir_line.replace("SESSION_DIR:", "").strip()
                    context_file_path = Path(session_dir_path) / "context.md"
                    if context_file_path.exists():
                        with open(context_file_path, "r", encoding="utf-8") as f:
                            context_content = f.read()
                        return context_content
                    else:
                        error_message = f"Video recording process completed, but context file not found: {context_file_path}"
                        print(error_message, file=sys.stderr, flush=True)
                        return error_message
                else:
                    error_message = f"Video recording process completed, but session directory path not found in stderr."
                    print(error_message, file=sys.stderr, flush=True)
                    return error_message
            else:
                error_message = f"Video recording process failed with exit code {process.returncode}.\nStdout: {stdout.strip()}\nStderr: {stderr.strip()}"

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            error_message = f"Video recording timed out after 5 minutes.\nStdout: {stdout.strip()}\nStderr: {stderr.strip()}"
            print(error_message, file=sys.stderr, flush=True)
            return error_message
        except Exception as e:
            error_message = f"Error during video recording: {str(e)}"
            print(error_message, file=sys.stderr, flush=True)
            return error_message
    
    def process_video_context(self, context):
        """Process the video context and prepare it for Gemini"""
        if not context or "failed" in context.lower():
            return context
        
        # Add instructions for Gemini on how to use the video context
        processed_context = f"""
# Video Recording Analysis Complete

The video has been processed with AI-guided intelligent frame extraction. Here's what I found:

{context}

## Next Steps for Implementation:

Based on the video analysis above, I should now:
1. Analyze each frame in the context of the spoken requirements
2. Identify the specific problems or features mentioned
3. Implement the requested changes or fixes
4. Provide code solutions based on the visual and audio context

Please let me analyze the frames and transcript to understand exactly what you want me to implement.
"""
        
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
        print("[DEBUG] Running start_recording() for test...", file=sys.stderr, flush=True)
        result = handler.start_recording()
        print("[DEBUG] start_recording() returned:", file=sys.stderr, flush=True)
        print(result, file=sys.stderr, flush=True)
        print(result)
            
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())