#!/usr/bin/env python3
"""
Video Recording Workflow - Step 1
Records video and asks Gemini to analyze timeline for frame extraction
"""

import os
import sys
import subprocess
from pathlib import Path


def record_video():
    """Step 1-5: Record video and generate word_timeline.csv"""
    current_dir = Path(__file__).parent
    video_recorder_path = current_dir / 'video_recorder.py'
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(video_recorder_path)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate(timeout=300)
        
        if process.returncode == 0:
            # Extract CSV path from output
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.startswith('@') and 'word_timeline.csv' in line:
                    return line.strip()
        
        return None
        
    except Exception as e:
        print(f"Recording failed: {e}")
        return None


def generate_gemini_prompt(csv_path):
    """Step 6: Generate prompt for Gemini to analyze timeline"""
    if not csv_path:
        return "Recording failed - no timeline generated"
    
    prompt = f"""Video recording complete. Please analyze the transcript timeline and extract frames.

Load this CSV file: {csv_path}

This file contains transcribed audio with timestamps. Analyze the content and identify 3-5 specific timestamps where frames should be extracted to accurately capture what the user is demonstrating.

After you analyze the timeline, immediately call the extract_frames command with your selected timestamps:

\\extract_frames frame1=X1.Y1 frame2=X2.Y2 frame3=X3.Y3

Replace X1.Y1, X2.Y2, X3.Y3 with the actual timestamp values you select."""
    
    return prompt


def main():
    """Main workflow function - Steps 1-6"""
    
    # Steps 1-5: Record video
    csv_path = record_video()
    if not csv_path:
        print("Video recording failed")
        return 1
    
    # Step 6: Generate prompt for Gemini
    gemini_prompt = generate_gemini_prompt(csv_path)
    
    # Output prompt for Gemini
    print(gemini_prompt)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())