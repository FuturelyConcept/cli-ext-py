#!/usr/bin/env python3
"""
Frame Extractor Command for Gemini CLI
Extracts frames at specified timestamps and provides final context
"""

import os
import sys
import re
import glob
from pathlib import Path
from frame_extractor import extract_frames_at_timestamps


def parse_frame_arguments(args):
    """Parse frame arguments from command line"""
    frame_timestamps = []
    
    # Parse arguments like frame1=1.5 frame2=3.2 frame3=5.0
    for arg in args:
        match = re.match(r'frame\d+=(\d+\.?\d*)', arg)
        if match:
            timestamp = float(match.group(1))
            frame_timestamps.append(timestamp)
    
    return sorted(frame_timestamps)


def find_latest_session_dir():
    """Find the most recent video session directory"""
    current_dir = Path.cwd()
    session_pattern = current_dir / ".gemini" / "video_ext" / "video_session_*"
    
    session_dirs = glob.glob(str(session_pattern))
    if not session_dirs:
        return None
    
    # Return the most recent session directory
    return Path(max(session_dirs, key=os.path.getmtime))


def find_video_file(session_dir):
    """Find the video file in the session directory"""
    if not session_dir or not session_dir.exists():
        return None
    
    video_extensions = ['*.mp4', '*.webm', '*.mov', '*.avi']
    for ext in video_extensions:
        video_files = list(session_dir.glob(ext))
        if video_files:
            return video_files[0]
    
    return None


def extract_frames_and_generate_context(timestamps):
    """Extract frames at timestamps and generate final context"""
    # Find the latest session directory
    session_dir = find_latest_session_dir()
    if not session_dir:
        return "Error: No video session found"
    
    # Find the video file
    video_file = find_video_file(session_dir)
    if not video_file:
        return "Error: No video file found in session"
    
    # Create frames directory
    frames_dir = session_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    # Extract frames
    try:
        frame_paths = extract_frames_at_timestamps(str(video_file), timestamps, str(frames_dir))
        if not frame_paths:
            return "Error: Failed to extract frames"
        
        # Find CSV file
        csv_files = list(session_dir.glob("word_timeline.csv"))
        if not csv_files:
            return "Error: No word_timeline.csv found"
        
        csv_file = csv_files[0]
        csv_path = os.path.relpath(csv_file, os.getcwd()).replace('\\', '/')
        
        # Generate final context
        context = f"""Here is the word_timeline.csv:
@{csv_path}

Based on your analysis, I extracted these {len(frame_paths)} frames:"""
        
        for i, frame_path in enumerate(frame_paths, 1):
            rel_path = os.path.relpath(frame_path, os.getcwd()).replace('\\', '/')
            context += f"\n@{rel_path}"
        
        context += "\n\nPlease analyze the frames and problem explained in word_timeline.csv and help resolve user's query."
        
        return context
        
    except Exception as e:
        return f"Error extracting frames: {str(e)}"


def main():
    """Main function for frame extraction command"""
    if len(sys.argv) < 2:
        print("Usage: python gemini_frame_extractor.py frame1=X.X frame2=Y.Y frame3=Z.Z")
        return 1
    
    # Parse frame timestamps from arguments
    timestamps = parse_frame_arguments(sys.argv[1:])
    
    if not timestamps:
        print("No valid frame timestamps provided")
        return 1
    
    # Extract frames and generate context
    context = extract_frames_and_generate_context(timestamps)
    
    # Output final context
    print(context)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())