#!/usr/bin/env python3
"""
Parse Gemini's response and extract frames at specified timestamps
"""

import sys
import re
import subprocess
from pathlib import Path


def parse_timestamps(response_text):
    """Parse timestamps from Gemini's response"""
    timestamps = []
    
    # Look for patterns like "frame1: X.X seconds" or "Around X.X seconds"
    patterns = [
        r'frame\d+:\s*(\d+\.?\d*)\s*seconds?',
        r'around\s+(\d+\.?\d*)\s*seconds?',
        r'(\d+\.?\d*)\s*seconds?'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response_text, re.IGNORECASE)
        for match in matches:
            try:
                timestamp = float(match)
                if timestamp not in timestamps:
                    timestamps.append(timestamp)
            except ValueError:
                continue
    
    return sorted(timestamps)


def extract_frames_at_timestamps(timestamps):
    """Extract frames at specified timestamps"""
    if not timestamps:
        return "No valid timestamps found in response"
    
    # Convert timestamps to comma-separated string
    timestamp_str = ','.join(map(str, timestamps))
    
    # Call extract_frames.py script
    current_dir = Path(__file__).parent
    extract_frames_script = current_dir / 'extract_frames.py'
    
    try:
        command = [sys.executable, str(extract_frames_script), timestamp_str]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = process.communicate(timeout=60)
        
        if process.returncode == 0:
            return stdout.strip()
        else:
            return f"Frame extraction failed: {stderr}"
            
    except subprocess.TimeoutExpired:
        process.kill()
        return "Frame extraction timed out"
    except Exception as e:
        return f"Frame extraction error: {str(e)}"


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python parse_gemini_response.py '<gemini_response_text>'", file=sys.stderr)
        return 1
    
    response_text = sys.argv[1]
    
    # Parse timestamps from response
    timestamps = parse_timestamps(response_text)
    
    if not timestamps:
        print("No timestamps found in the response")
        return 1
    
    # Extract frames at those timestamps
    result = extract_frames_at_timestamps(timestamps)
    print(result)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())