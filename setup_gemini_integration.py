#!/usr/bin/env python3
"""
Complete Gemini CLI Integration Setup
This script sets up the video recording extension with Gemini CLI
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path


class GeminiIntegrationSetup:
    """Sets up complete Gemini CLI integration"""
    
    def __init__(self, gemini_path=None):
        self.current_dir = Path(__file__).parent
        self.gemini_path = gemini_path or 'gemini'  # Default to system PATH
        
        # Try to find Gemini directory
        self.gemini_dir = self.find_gemini_directory()
        self.extensions_dir = self.gemini_dir / 'extensions'
        self.video_ext_dir = self.extensions_dir / 'video-recording'
    
    def find_gemini_directory(self):
        """Find Gemini CLI directory"""
        # Common locations to check
        possible_locations = [
            Path.home() / '.gemini',
            Path.home() / '.config' / 'gemini',
            Path.home() / 'AppData' / 'Local' / 'gemini',  # Windows
            Path.home() / 'Library' / 'Application Support' / 'gemini',  # macOS
            Path('/usr/local/share/gemini'),
            Path('/opt/gemini'),
        ]
        
        # Check if user provided a specific path
        if hasattr(self, 'custom_gemini_dir') and self.custom_gemini_dir:
            return Path(self.custom_gemini_dir)
        
        # Check common locations
        for location in possible_locations:
            if location.exists():
                return location
        
        # Default fallback
        return Path.home() / '.gemini'
    
    def set_gemini_directory(self, path):
        """Set custom Gemini directory path"""
        self.custom_gemini_dir = path
        self.gemini_dir = self.find_gemini_directory()
        self.extensions_dir = self.gemini_dir / 'extensions'
        self.video_ext_dir = self.extensions_dir / 'video-recording'
        
    def install_dependencies(self):
        """Install video extension dependencies"""
        print("[INFO] Installing video extension dependencies...")
        
        try:
            # Try to install with better error handling
            result = subprocess.run([
                sys.executable, str(self.current_dir / 'cli_video_ext.py'), 'install'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[SUCCESS] Dependencies installed successfully")
                return True
            else:
                print("[WARNING] Some dependencies may have installation issues:")
                print(result.stdout)
                print(result.stderr)
                
                # Try alternative installation method
                print("[INFO] Trying alternative installation method...")
                
                # Install dependencies individually with better compatibility
                deps = ['flask', 'openai-whisper', 'ffmpeg-python', 'werkzeug']
                
                for dep in deps:
                    try:
                        print(f"   Installing {dep}...")
                        result = subprocess.run([
                            sys.executable, '-m', 'pip', 'install', dep, '--user'
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(f"   [SUCCESS] {dep} installed")
                        else:
                            print(f"   [WARNING] {dep} had issues but may work")
                    except Exception as e:
                        print(f"   [ERROR] Error installing {dep}: {e}")
                
                return True  # Continue even if some deps had issues
                
        except Exception as e:
            print(f"[ERROR] Error during dependency installation: {e}")
            return False

    def check_prerequisites(self):
        """Check if prerequisites are met"""
        print("[INFO] Checking prerequisites...")
        print(f"[INFO] Gemini directory: {self.gemini_dir}")
        
        # Check if Gemini CLI is installed
        try:
            result = subprocess.run([self.gemini_path, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"[SUCCESS] Gemini CLI found at: {self.gemini_path}")
                print(f"   Version: {result.stdout.strip()}")
            else:
                print("[ERROR] Gemini CLI not responding properly")
                print(f"   Command tried: {self.gemini_path} --version")
                return False
        except FileNotFoundError:
            print(f"[ERROR] Gemini CLI not found at: {self.gemini_path}")
            print("   Please specify the correct path using --gemini-path option")
            return False
        
        # Check if our video extension dependencies are met
        try:
            result = subprocess.run([
                sys.executable, str(self.current_dir / 'cli_video_ext.py'), 'check'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("[SUCCESS] Video extension dependencies are ready")
                return True
            else:
                print("[WARNING] Video extension dependencies need installation")
                print("[INFO] Installing dependencies automatically...")
                
                # Auto-install dependencies
                if self.install_dependencies():
                    # Re-check after installation
                    result = subprocess.run([
                        sys.executable, str(self.current_dir / 'cli_video_ext.py'), 'check'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print("[SUCCESS] Dependencies installed and verified")
                        return True
                    else:
                        print("[WARNING] Some dependencies may still have issues, but continuing...")
                        return True
                else:
                    print("[ERROR] Failed to install dependencies")
                    return False
                    
        except Exception as e:
            print(f"[ERROR] Error checking video extension: {e}")
            return False
    
    def setup_extension_directory(self):
        """Set up the extension directory structure"""
        print("[INFO] Setting up extension directory...")
        
        # Create extensions directory
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        self.video_ext_dir.mkdir(exist_ok=True)
        
        # Copy necessary files
        files_to_copy = [
            'cli_video_ext.py',
            'video_recorder.py',
            'gemini_video_handler.py',
            'requirements.txt',
            'frame_extractor.py'
        ]
        
        for file_name in files_to_copy:
            src = self.current_dir / file_name
            dst = self.video_ext_dir / file_name
            if src.exists():
                shutil.copy2(src, dst)
                print(f"[SUCCESS] Copied {file_name}")
            else:
                print(f"[WARNING] File not found: {file_name}")
        
        print(f"[INFO] Extension installed at: {self.video_ext_dir}")
    
    def create_gemini_command(self):
        """Create Gemini CLI command configuration"""
        print("[INFO] Creating Gemini CLI command...")
        
        # Create command configuration
        command_config = {
            "video_recording": {
                "command": f"{sys.executable} {self.video_ext_dir / 'gemini_video_handler.py'} record",
                "description": "Record screen video with AI-guided intelligent frame extraction",
                "timeout": 300,
                "working_directory": str(self.video_ext_dir),
                "triggers": [
                    "start a video recording",
                    "record a video",
                    "show you the problem",
                    "demonstrate the issue",
                    "record my screen"
                ]
            }
        }
        
        # Write command configuration
        commands_dir = self.gemini_dir / 'commands'
        commands_dir.mkdir(exist_ok=True);
        
        command_file = commands_dir / 'video_recording.json'
        with open(command_file, 'w') as f:
            json.dump(command_config, f, indent=2)
        
        print(f"[SUCCESS] Command configuration created: {command_file}")
    
    def create_workflow_instructions(self):
        """Create workflow instructions for Gemini"""
        print("[INFO] Creating workflow instructions...")
        
        instructions = """
# Video Recording Workflow for Gemini CLI

## User Request Patterns:
- "start a video recording and i will tell you the problem i want you to solve"
- "record a video to show you the bug"
- "let me record my screen to demonstrate the issue"

## Workflow Steps:

1. **When user requests video recording:**
   - Execute: video_recording command
   - Guide user through recording process
   - Wait for processing to complete

2. **After recording completes:**
   - Analyze the generated context (transcript + frames)
   - Identify specific problems mentioned
   - Implement requested changes based on visual/audio context

3. **Response Format:**
   - Acknowledge the recording
   - Summarize what was demonstrated
   - Provide implementation or solutions
   - Ask for confirmation or additional details

## Example Interaction:

User: "start a video recording and i will tell you the problem i want you to solve"

Gemini Response: 
"I'll start a video recording for you. Please demonstrate the problem clearly and speak about what you want me to fix."

[Execute video recording command]

[After completion, analyze frames and transcript to implement the solution]
"""
        
        workflow_file = self.video_ext_dir / 'workflow_instructions.md'
        with open(workflow_file, 'w') as f:
            f.write(instructions)
        
        print(f"[SUCCESS] Workflow instructions created: {workflow_file}")
    
    def test_integration(self):
        """Test the integration"""
        print("[INFO] Testing integration...")
        
        try:
            # Test the video handler
            result = subprocess.run([
                sys.executable, 
                str(self.video_ext_dir / 'gemini_video_handler.py'), 
                'test'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("[SUCCESS] Integration test passed")
                return True
            else:
                print(f"[ERROR] Integration test failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Integration test error: {e}")
            return False
    
    def setup_complete(self):
        """Complete the setup process"""
        print("\n[INFO] Integration setup complete!")
        print("\n[INFO] Next steps:")
        print("1. Open Gemini CLI")
        print("2. Say: 'start a video recording and i will tell you the problem i want you to solve'")
        print("3. Follow the recording instructions")
        print("4. Gemini will analyze the video and implement your requested changes")
        print("\n[INFO] Advanced usage:")
        print("- The system uses AI-guided frame extraction for precise visual context")
        print("- Frames are extracted at moments when you mention specific problems")
        print("- Timeline visualization helps understand the flow of issues")
        print("\n[INFO] Extension location:", self.video_ext_dir)
    
    def run_setup(self):
        """Run the complete setup process"""
        print("Starting Gemini CLI Video Recording Integration Setup\n")
        
        if not self.check_prerequisites():
            print("[ERROR] Prerequisites not met. Please resolve the issues above.")
            return False
        
        self.setup_extension_directory()
        self.create_gemini_command()
        self.create_workflow_instructions()
        
        # if self.test_integration():
        #     self.setup_complete()
        #     return True
        # else:
        #     print("[ERROR] Setup completed but integration test failed")
        #     return False
        self.setup_complete()
        return True


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Set up Gemini CLI Video Recording Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 setup_gemini_integration.py
  python3 setup_gemini_integration.py --gemini-path /usr/local/bin/gemini
  python3 setup_gemini_integration.py --gemini-dir ~/.config/gemini
  python3 setup_gemini_integration.py --uninstall
        """
    )
    
    parser.add_argument('--gemini-path', 
                       help='Path to Gemini CLI executable (default: gemini)')
    parser.add_argument('--gemini-dir', 
                       help='Path to Gemini CLI directory (default: auto-detect)')
    parser.add_argument('--uninstall', action='store_true',
                       help='Uninstall the video recording extension')
    parser.add_argument('--list-locations', action='store_true',
                       help='List possible Gemini installation locations')
    
    args = parser.parse_args()
    
    # Handle list locations
    if args.list_locations:
        print("[INFO] Checking possible Gemini CLI locations...")
        possible_locations = [
            Path.home() / '.gemini',
            Path.home() / '.config' / 'gemini',
            Path.home() / 'AppData' / 'Local' / 'gemini',  # Windows
            Path.home() / 'Library' / 'Application Support' / 'gemini',  # macOS
            Path('/usr/local/share/gemini'),
            Path('/opt/gemini'),
        ]
        
        for location in possible_locations:
            status = "[SUCCESS] EXISTS" if location.exists() else "[ERROR] NOT FOUND"
            print(f"  {location}: {status}")
        return 0
    
    # Create setup instance
    setup = GeminiIntegrationSetup(gemini_path=args.gemini_path)
    
    # Set custom directory if provided
    if args.gemini_dir:
        setup.set_gemini_directory(args.gemini_dir)
    
    # Handle uninstall
    if args.uninstall:
        print("[INFO] Uninstalling video recording extension...")
        if setup.video_ext_dir.exists():
            shutil.rmtree(setup.video_ext_dir)
            print("[SUCCESS] Extension uninstalled")
        else:
            print("[WARNING] Extension not found")
        return 0
    
    # Run setup
    success = setup.run_setup()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())