#!/usr/bin/env python3
"""
Installer for Gemini CLI Video Recording Extension
Copies files from project directory to C:/Users/Deepika_Akshaj/.gemini/
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

class VideoExtensionInstaller:
    def __init__(self):
        self.project_dir = Path(__file__).parent.absolute()
        self.gemini_dir = Path("C:/Users/Deepika_Akshaj/.gemini")
        self.extension_dir = self.gemini_dir / "extensions" / "video-recording"
        
    def detect_python_executable(self):
        """Detect the correct Python executable name"""
        possible_names = ['python.exe', 'python3.exe', 'python', 'python3']
        
        for name in possible_names:
            try:
                result = subprocess.run([name, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"Found Python: {name}")
                    return name
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        print("No Python executable found")
        return 'python'  # Default fallback
    
    def ensure_gemini_directory(self):
        """Ensure Gemini CLI installation directory exists"""
        if not self.gemini_dir.exists():
            self.gemini_dir.mkdir(parents=True, exist_ok=True)
            print(f"Created Gemini directory: {self.gemini_dir}")
        else:
            print(f"Found Gemini directory: {self.gemini_dir}")
        
        return True
    
    def copy_project_files(self):
        """Copy all necessary files from project to extension directory"""
        print("Copying project files to extension directory...")
        
        # Files to copy from project directory
        files_to_copy = [
            'video_recorder.py', 
            'frame_extractor.py',
            'extract_frames.py',
            'gemini_video_handler.py',
            'requirements.txt',
            'cli_video_ext.py'
        ]
        
        # Create extension directory
        self.extension_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        for subdir in ['uploads', 'frames', 'context', 'temp']:
            (self.extension_dir / subdir).mkdir(exist_ok=True)
        
        # Copy files
        copied_files = []
        for file_name in files_to_copy:
            source = self.project_dir / file_name
            target = self.extension_dir / file_name
            
            if source.exists():
                shutil.copy2(source, target)
                copied_files.append(file_name)
                print(f"Copied: {file_name}")
            else:
                print(f"Missing: {file_name}")
        
        # Copy bin directory if it exists (for FFmpeg binaries)
        bin_source = self.project_dir / 'bin'
        if bin_source.exists():
            bin_target = self.extension_dir / 'bin'
            if bin_target.exists():
                shutil.rmtree(bin_target)
            shutil.copytree(bin_source, bin_target)
            print(f"Copied: bin directory with FFmpeg binaries")
            copied_files.append('bin')
        
        print(f"Copied {len(copied_files)} items to extension directory")
        return len(copied_files) > 0
    
    def create_main_entry_point(self, python_exe):
        """Create the main entry point for Gemini CLI"""
        print("Creating main entry point...")
        
        entry_point_code = f'''#!/usr/bin/env python3
"""
Video Recording Extension for Gemini CLI
Entry point that executes from {self.extension_dir}
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for video recording"""
    extension_dir = Path(__file__).parent.absolute()
    video_recorder_path = extension_dir / "video_recorder.py"
    
    if not video_recorder_path.exists():
        print("Error: video_recorder.py not found!")
        return 1
    
    # Run video recorder and capture output
    try:
        result = subprocess.run([
            "{python_exe}", str(video_recorder_path)
        ], cwd=str(extension_dir), capture_output=True, text=True)
        
        # Print the actual video context output
        if result.stdout:
            print(result.stdout)
        
        # Handle session directory info from stderr
        if result.stderr:
            for line in result.stderr.split("\\n"):
                if line.startswith("SESSION_DIR:"):
                    session_dir = line.split(":", 1)[1].strip()
                    context_file = Path(session_dir) / "context.md"
                    if context_file.exists():
                        with open(context_file, "r", encoding="utf-8") as f:
                            print(f.read())
        
        return result.returncode
    except Exception as e:
        print(f"Error running video recorder: {{e}}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        
        entry_point_path = self.extension_dir / "record_video.py"
        with open(entry_point_path, 'w') as f:
            f.write(entry_point_code)
        
        print(f"Created main entry point: {entry_point_path}")
        return True
    
    def create_gemini_extension_config(self, python_exe):
        """Create Gemini CLI extension configuration"""
        print("Creating Gemini CLI extension configuration...")
        
        # Create the extension config that Gemini CLI will recognize
        config = {
            "name": "video-recording",
            "version": "1.0.0", 
            "description": "Record screen video with AI-guided frame extraction",
            "commands": {
                "record_video": {
                    "command": f"{python_exe} {str(self.extension_dir / 'record_video.py')}",
                    "description": "Start video recording with intelligent frame extraction",
                    "working_directory": str(self.extension_dir)
                }
            }
        }
        
        # Save to the main gemini directory so it gets auto-loaded
        config_file = self.gemini_dir / "video-recording-extension.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"Created extension config: {config_file}")
        
        # Also create a tools.json file for tool integration
        tools_config = {
            "tools": [
                {
                    "name": "video_recorder",
                    "description": "Record screen video and extract frames with transcription",
                    "command": f"{python_exe} {str(self.extension_dir / 'record_video.py')}",
                    "parameters": [],
                    "working_directory": str(self.extension_dir)
                }
            ]
        }
        
        tools_file = self.gemini_dir / "tools.json"
        with open(tools_file, 'w') as f:
            json.dump(tools_config, f, indent=2)
        
        print(f"Created tools config: {tools_file}")
        return True
    
    def install_dependencies(self):
        """Install required Python dependencies"""
        print("Installing Python dependencies...")
        
        requirements_file = self.extension_dir / 'requirements.txt'
        
        if requirements_file.exists():
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)], 
                             check=True, cwd=str(self.extension_dir))
                print("Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error installing dependencies: {e}")
                return False
        else:
            print("Requirements file not found")
            return False
    
    def test_installation(self):
        """Test the installation"""
        print("Testing installation...")
        
        # Check if video_recorder.py exists and is executable
        video_recorder_path = self.extension_dir / "video_recorder.py"
        if not video_recorder_path.exists():
            print("video_recorder.py not found in extension directory")
            return False
        
        # Check if record_video.py exists
        entry_point_path = self.extension_dir / "record_video.py"
        if not entry_point_path.exists():
            print("record_video.py not found in extension directory")
            return False
        
        print("All required files are in place")
        return True
    
    def register_with_gemini_cli(self, python_exe):
        """Register the extension with Gemini CLI for automatic recognition"""
        print("Registering extension with Gemini CLI...")
        
        # Create extension registration with auto-detection phrases
        extension_config = {
            "video_recording": {
                "command": f"python {self.extension_dir / 'record_video.py'}",
                "description": "Record screen video with AI-guided frame extraction",
                "category": "media",
                "keywords": ["video", "record", "screen", "capture", "frames"],
                "auto_detect_phrases": [
                    "start video recording",
                    "record my screen", 
                    "video capture",
                    "screen recording",
                    "show you what I mean",
                    "let me record this",
                    "record this problem",
                    "video of the issue"
                ]
            }
        }
        
        # Save the registration
        config_file = self.gemini_dir / "video-extension-config.json"
        with open(config_file, 'w') as f:
            json.dump(extension_config, f, indent=2)
        
        # Create command mappings
        command_map = {
            "commands": {
                "record_video": f"python {self.extension_dir / 'record_video.py'}",
                "start_video_recording": f"python {self.extension_dir / 'record_video.py'}",
                "screen_record": f"python {self.extension_dir / 'record_video.py'}"
            }
        }
        
        command_file = self.gemini_dir / "commands.json"
        with open(command_file, 'w') as f:
            json.dump(command_map, f, indent=2)
        
        print(f"Extension registered at: {config_file}")
        print(f"Command mappings created at: {command_file}")
        return True
    
    def run_installation(self):
        """Run the complete installation process"""
        print("Gemini CLI Video Recording Extension Installer")
        print("=" * 60)
        print(f"Project directory: {self.project_dir}")
        print(f"Target directory: {self.extension_dir}")
        print()
        
        # Step 1: Detect Python
        python_exe = self.detect_python_executable()
        
        # Step 2: Ensure Gemini directory exists
        if not self.ensure_gemini_directory():
            print("Failed to create Gemini directory")
            return False
        
        # Step 3: Copy project files
        if not self.copy_project_files():
            print("Failed to copy project files")
            return False
        
        # Step 4: Create main entry point
        if not self.create_main_entry_point(python_exe):
            print("Failed to create main entry point")
            return False
        
        # Step 5: Create Gemini extension configuration
        if not self.create_gemini_extension_config(python_exe):
            print("Failed to create Gemini extension configuration")
            return False
        
        # Step 6: Install dependencies
        if not self.install_dependencies():
            print("Failed to install dependencies - install manually")
        
        # Step 7: Test installation
        if not self.test_installation():
            print("Installation completed but tests failed")
        
        # Step 8: Register with Gemini CLI
        self.register_with_gemini_cli(python_exe)
        
        # Success message
        print("\n" + "=" * 60)
        print("INSTALLATION COMPLETE!")
        print("=" * 60)
        print(f"Project directory: {self.project_dir}")
        print(f"Extension installed at: {self.extension_dir}")
        print(f"Using Python executable: {python_exe}")
        
        print("\nUSAGE:")
        print("The extension has been automatically configured for Gemini CLI.")
        print("Simply ask Gemini to start video recording:")
        print("")
        print("Examples:")
        print('  "start a video recording"')
        print('  "record my screen so I can explain the problem"')
        print('  "use video recording to show you what I need help with"')
        print("")
        print("Gemini will automatically use the video recording tool.")
        print("")
        print("Manual command (if needed):")
        print(f"python {self.extension_dir / 'record_video.py'}")
        print("")
        print("Process:")
        print("1. Opens browser screen recording dialog")
        print("2. Records screen and audio")
        print("3. Extracts frames and transcribes audio")
        print("4. Returns video context to Gemini")
        
        return True

def main():
    """Main installation function"""
    installer = VideoExtensionInstaller()
    
    try:
        success = installer.run_installation()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nInstallation failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())