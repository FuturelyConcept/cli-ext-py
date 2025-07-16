#!/usr/bin/env python3
"""
Test the new two-step workflow
"""

import os
import sys
from pathlib import Path

def test_csv_generation():
    """Test CSV generation"""
    # Simulate word timeline data
    word_timeline = [
        {'time': 0.5, 'word': 'Hello'},
        {'time': 1.0, 'word': 'this'},
        {'time': 1.5, 'word': 'is'},
        {'time': 2.0, 'word': 'a'},
        {'time': 2.5, 'word': 'test'}
    ]
    
    # Create CSV content
    csv_content = "timestamp,word\n"
    for entry in word_timeline:
        csv_content += f"{entry['time']:.1f},{entry['word']}\n"
    
    # Test CSV content
    print("Generated CSV content:")
    print(csv_content)
    
    # Save to test file
    test_dir = Path('.gemini/video_ext/test_session')
    test_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = test_dir / "word_timeline.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_content)
    
    print(f"CSV saved to: {csv_file}")
    
    # Test minimal context generation
    duration = 5.0
    csv_path = os.path.relpath(csv_file, os.getcwd()).replace('\\', '/')
    
    output = f"Duration {duration:.1f}s\n"
    output += f"@{csv_path}\n"
    output += "Next: Ask Gemini to analyze the timeline and request specific frame timestamps\n"
    
    print("\nMinimal context output:")
    print(output)
    
    return csv_file

def test_timestamp_parsing():
    """Test timestamp parsing for frame extraction"""
    test_timestamps = [
        "1.5,3.2,5.0",
        "[1.5, 3.2, 5.0]",
        "2.0, 4.5"
    ]
    
    for timestamps_str in test_timestamps:
        try:
            if timestamps_str.startswith('[') and timestamps_str.endswith(']'):
                # JSON format
                import json
                timestamps = json.loads(timestamps_str)
            else:
                # Comma-separated format
                timestamps = [float(t.strip()) for t in timestamps_str.split(',')]
            
            print(f"Parsed '{timestamps_str}' -> {timestamps}")
            
        except Exception as e:
            print(f"Failed to parse '{timestamps_str}': {e}")

if __name__ == "__main__":
    print("Testing two-step workflow...")
    print("=" * 50)
    
    print("1. Testing CSV generation:")
    csv_file = test_csv_generation()
    
    print("\n2. Testing timestamp parsing:")
    test_timestamp_parsing()
    
    print("\n3. Example usage:")
    print("Step 1: Record video -> generates word_timeline.csv")
    print("Step 2: python3 extract_frames.py '1.5,3.2,5.0' -> extracts frames")
    
    print("\nWorkflow test completed!")