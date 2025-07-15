#!/usr/bin/env python3
"""
Record.py - Entry point for video recording (alias to index.py)
This file exists for backward compatibility with different configuration names
"""

import sys
from pathlib import Path

# Add the current directory to the path so we can import from index.py
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main functionality from index.py
from index import main

if __name__ == "__main__":
    # If called as record.py, assume we want to start video recording
    if len(sys.argv) == 1:
        sys.argv.append("video")
    
    sys.exit(main())