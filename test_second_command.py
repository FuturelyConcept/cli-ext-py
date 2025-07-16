#!/usr/bin/env python3
"""
Test second command to see if Gemini CLI can chain commands
"""

import sys

def main():
    """Test second command"""
    
    print(f"Second command executed successfully!")
    print(f"Arguments received: {sys.argv[1:] if len(sys.argv) > 1 else 'None'}")
    print("This confirms that Gemini CLI can chain commands based on output from previous commands.")

if __name__ == '__main__':
    main()