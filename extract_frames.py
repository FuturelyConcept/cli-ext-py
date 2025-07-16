#!/usr/bin/env python3
"""
On-demand frame extraction script for Gemini CLI Video Recording Extension
Step 2 of two-step workflow: Extract frames at specific timestamps
"""

import os
import sys
import json
import argparse
from pathlib import Path
from frame_extractor import extract_frames_at_timestamps, get_ffmpeg_path


def find_latest_video_session():
    """Find the latest video session directory"""
    current_dir = Path.cwd()
    video_ext_dir = current_dir / '.gemini' / 'video_ext'
    
    if not video_ext_dir.exists():
        return None
    
    # Find all session directories
    session_dirs = [d for d in video_ext_dir.iterdir() if d.is_dir() and d.name.startswith('video_session_')]
    
    if not session_dirs:
        return None
    
    # Sort by name (which includes timestamp) and return the latest
    session_dirs.sort(key=lambda x: x.name)
    return session_dirs[-1]


def extract_frames_from_timestamps(timestamps_str, session_dir=None):
    """Extract frames from video at specified timestamps"""
    
    # Find session directory
    if not session_dir:
        session_dir = find_latest_video_session()
    
    if not session_dir or not session_dir.exists():
        return "Error: No video session found"
    
    # Find the video file
    uploads_dir = session_dir / 'uploads'
    video_files = list(uploads_dir.glob('*.webm'))
    
    if not video_files:
        return "Error: No video file found in session"
    
    video_path = video_files[0]
    
    # Parse timestamps
    try:
        if timestamps_str.startswith('[') and timestamps_str.endswith(']'):
            # JSON format
            timestamps = json.loads(timestamps_str)
        else:
            # Comma-separated format
            timestamps = [float(t.strip()) for t in timestamps_str.split(',')]
    except (json.JSONDecodeError, ValueError) as e:
        return f"Error parsing timestamps: {e}"
    
    # Create frames directory
    frames_dir = session_dir / 'frames'
    frames_dir.mkdir(exist_ok=True)
    
    # Extract frames
    try:
        extracted_frames = extract_frames_at_timestamps(
            str(video_path), 
            str(frames_dir), 
            timestamps
        )
        
        if not extracted_frames:
            return "Error: No frames could be extracted"
        
        # Generate output
        output = f"Extracted {len(extracted_frames)} frames:\n"
        for frame in extracted_frames:
            frame_path = os.path.relpath(frame['path'], os.getcwd()).replace('\\', '/')
            output += f"@{frame_path}\n"
        
        return output
        
    except Exception as e:
        return f"Error extracting frames: {e}"


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Extract frames at specific timestamps')
    parser.add_argument('timestamps', help='Comma-separated timestamps or JSON array')
    parser.add_argument('--session', help='Session directory path (optional)')
    
    args = parser.parse_args()
    
    session_dir = None
    if args.session:
        session_dir = Path(args.session)
    
    result = extract_frames_from_timestamps(args.timestamps, session_dir)
    print(result)


if __name__ == '__main__':
    main()