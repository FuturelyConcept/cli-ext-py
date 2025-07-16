#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

def main():
    # Just run the main recorder and capture its output
    current_dir = Path(__file__).parent
    recorder_path = current_dir / 'video_recorder.py'
    
    try:
        result = subprocess.run([sys.executable, str(recorder_path)], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            # Just print the essential info, nothing else
            print("Recording completed successfully")
            print("Check the session directory for files")
        else:
            print("Recording failed")
            
    except Exception as e:
        print("Error occurred")

if __name__ == '__main__':
    main()