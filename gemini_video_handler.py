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
        command = [sys.executable, str(self.video_ext_script), "record"]

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate(timeout=300)

            if process.returncode == 0:
                # Print the raw output from cli_video_ext.py directly
                if stdout:
                    print(stdout.strip())
                if stderr:
                    print(stderr.strip(), file=sys.stderr)
                return ""
            else:
                return f"Recording failed with exit code {process.returncode}. Stderr: {stderr.strip()}"

        except subprocess.TimeoutExpired:
            process.kill()
            return "Recording timed out"
        except Exception as e:
            return f"Recording error: {str(e)}"
    
    


def main():
    """Main function for command-line usage"""
    
    handler = GeminiVideoHandler()
    handler.start_recording()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())