#!/usr/bin/env python3
"""
CLI Video Extension Integration
This script provides a command-line interface for the video recording extension
that can be integrated with Gemini CLI or Claude Code CLI.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []
    
    try:
        import flask
    except ImportError:
        missing_deps.append('flask')
    
    try:
        import whisper
    except ImportError:
        missing_deps.append('openai-whisper')
    
    try:
        import ffmpeg
    except ImportError:
        missing_deps.append('ffmpeg-python')
    
    # Check for ffmpeg (system or local bin)
    ffmpeg_found = False
    
    # First check local bin directory
    script_dir = Path(__file__).parent
    local_ffmpeg = script_dir / 'bin' / 'ffmpeg.exe'
    
    if local_ffmpeg.exists():
        try:
            subprocess.run([str(local_ffmpeg), '-version'], capture_output=True, check=True)
            ffmpeg_found = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # Then check system PATH
    if not ffmpeg_found:
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            ffmpeg_found = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    if not ffmpeg_found:
        missing_deps.append('ffmpeg (system)')
    
    return missing_deps


def install_dependencies():
    """Install missing Python dependencies"""
    print("Installing required dependencies...")
    
    requirements_file = Path(__file__).parent / 'requirements.txt'
    
    try:
        if requirements_file.exists():
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file), '--user'], check=True)
        else:
            # Install individually with better compatibility
            deps = ['flask', 'openai-whisper', 'ffmpeg-python', 'werkzeug']
            for dep in deps:
                print(f"Installing {dep}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep, '--user'], check=True)
        
        print("Dependencies installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("Trying alternative installation method...")
        
        # Try individual installation with more flexibility
        deps = ['flask', 'openai-whisper', 'ffmpeg-python', 'werkzeug']
        success_count = 0
        
        for dep in deps:
            try:
                print(f"Installing {dep}...")
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep, '--user'], check=True)
                success_count += 1
                print(f"✅ {dep} installed successfully")
            except subprocess.CalledProcessError:
                print(f"⚠️ {dep} had installation issues, trying without user flag...")
                try:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', dep], check=True)
                    success_count += 1
                    print(f"✅ {dep} installed successfully")
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to install {dep}")
        
        if success_count >= 3:  # If most dependencies installed
            print(f"✅ {success_count}/{len(deps)} dependencies installed successfully!")
        else:
            print(f"❌ Only {success_count}/{len(deps)} dependencies installed")
            raise e


def record_video():
    """Start video recording process"""
    try:
        # Import and run the video recorder
        video_recorder_path = Path(__file__).parent / 'video_recorder.py'
        
        if not video_recorder_path.exists():
            print("Error: video_recorder.py not found!")
            return 1
        
        # Run the video recorder - output goes directly to stdout
        result = subprocess.run([sys.executable, str(video_recorder_path)], 
                              capture_output=False, text=True)
        
        return result.returncode
        
    except KeyboardInterrupt:
        return 1  # Silent exit on Ctrl+C
    except Exception:
        print("Error in recording, please try again later")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='CLI Video Extension for Code Agents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s record          # Start video recording
  %(prog)s check           # Check dependencies
  %(prog)s install         # Install dependencies
  
Integration with CLI agents:
  # Add to your CLI agent's command registry
  /video                   # Record screen and generate context
        """
    )
    
    parser.add_argument('command', nargs='?', default='record',
                       choices=['record', 'check', 'install'],
                       help='Command to execute')
    
    parser.add_argument('--version', action='version', version='CLI Video Extension 1.0.0')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        missing = check_dependencies()
        if missing:
            print("Missing dependencies:")
            for dep in missing:
                print(f"  - {dep}")
            print("\nRun 'python cli_video_ext.py install' to install missing dependencies.")
            return 1
        else:
            print("All dependencies are installed!")
            return 0
    
    elif args.command == 'install':
        try:
            missing = check_dependencies()
            if 'ffmpeg (system)' in missing:
                print("System ffmpeg not found!")
                print("Please install ffmpeg:")
                print("  - Windows: Download from https://ffmpeg.org/download.html")
                print("  - macOS: brew install ffmpeg")
                print("  - Linux: sudo apt-get install ffmpeg")
                print("")
            
            # Install Python dependencies
            install_dependencies()
            
            # Check again
            missing = check_dependencies()
            if missing:
                print("Some dependencies are still missing:")
                for dep in missing:
                    print(f"  - {dep}")
                return 1
            else:
                print("All Python dependencies installed successfully!")
                return 0
                
        except Exception as e:
            print(f"Installation failed: {e}")
            return 1
    
    elif args.command == 'record':
        # Check dependencies first
        missing = check_dependencies()
        if missing:
            print("Missing dependencies. Please install them first:")
            for dep in missing:
                print(f"  - {dep}")
            print("\nRun 'python cli_video_ext.py install' to install missing dependencies.")
            return 1
        
        # Start recording
        return record_video()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())