#!/usr/bin/env python3
"""
Helper script to find Gemini CLI installation
"""

import os
import sys
import subprocess
from pathlib import Path


def find_gemini_executable():
    """Find Gemini CLI executable"""
    print("🔍 Searching for Gemini CLI executable...")
    
    # Check common executable names
    possible_names = ['gemini', 'gemini.exe', 'gemini-cli', 'gemini-cli.exe']
    
    # Check system PATH
    for name in possible_names:
        try:
            result = subprocess.run(['which', name], capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                print(f"✅ Found in PATH: {path}")
                return path
        except FileNotFoundError:
            # 'which' not available, try direct execution
            try:
                result = subprocess.run([name, '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Found in PATH: {name}")
                    return name
            except FileNotFoundError:
                continue
    
    # Check common installation directories
    common_dirs = [
        Path('/usr/local/bin'),
        Path('/usr/bin'),
        Path('/opt/gemini/bin'),
        Path.home() / '.local' / 'bin',
        Path.home() / 'bin',
    ]
    
    # Windows-specific paths
    if sys.platform == 'win32':
        common_dirs.extend([
            Path.home() / 'AppData' / 'Local' / 'gemini',
            Path('C:') / 'Program Files' / 'gemini',
            Path('C:') / 'Program Files (x86)' / 'gemini',
        ])
    
    # macOS-specific paths
    elif sys.platform == 'darwin':
        common_dirs.extend([
            Path('/Applications/Gemini.app/Contents/MacOS'),
            Path.home() / 'Applications' / 'Gemini.app' / 'Contents' / 'MacOS',
        ])
    
    for directory in common_dirs:
        if directory.exists():
            for name in possible_names:
                executable = directory / name
                if executable.exists() and executable.is_file():
                    try:
                        result = subprocess.run([str(executable), '--version'], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            print(f"✅ Found executable: {executable}")
                            return str(executable)
                    except:
                        continue
    
    print("❌ Gemini CLI executable not found")
    return None


def find_gemini_directory():
    """Find Gemini CLI data directory"""
    print("🔍 Searching for Gemini CLI data directory...")
    
    possible_locations = [
        Path.home() / '.gemini',
        Path.home() / '.config' / 'gemini',
        Path.home() / 'AppData' / 'Local' / 'gemini',  # Windows
        Path.home() / 'AppData' / 'Roaming' / 'gemini',  # Windows
        Path.home() / 'Library' / 'Application Support' / 'gemini',  # macOS
        Path('/usr/local/share/gemini'),
        Path('/opt/gemini'),
        Path('/var/lib/gemini'),
    ]
    
    for location in possible_locations:
        if location.exists():
            print(f"✅ Found directory: {location}")
            return str(location)
    
    print("❌ Gemini CLI data directory not found")
    return None


def test_gemini_access(executable_path):
    """Test if Gemini CLI is accessible and working"""
    print(f"🧪 Testing Gemini CLI access: {executable_path}")
    
    try:
        result = subprocess.run([executable_path, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Gemini CLI is working")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Gemini CLI returned error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Gemini CLI command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing Gemini CLI: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Gemini CLI Detection Tool\n")
    
    # Find executable
    executable = find_gemini_executable()
    if not executable:
        print("\n❌ Could not find Gemini CLI executable")
        print("Please install Gemini CLI or specify the path manually")
        return 1
    
    # Find data directory
    data_dir = find_gemini_directory()
    if not data_dir:
        print("\n⚠️ Could not find Gemini CLI data directory")
        print("This might be normal for first-time installations")
    
    # Test access
    if not test_gemini_access(executable):
        print("\n❌ Gemini CLI is not working properly")
        return 1
    
    print("\n" + "="*50)
    print("📋 GEMINI CLI DETECTION RESULTS")
    print("="*50)
    print(f"Executable: {executable}")
    print(f"Data Directory: {data_dir or 'Not found (will be created)'}")
    print("\n✅ Ready for integration setup!")
    
    print("\n📝 Next steps:")
    if executable != 'gemini':
        print(f"python3 setup_gemini_integration.py --gemini-path '{executable}'")
    else:
        print("python3 setup_gemini_integration.py")
    
    if data_dir and data_dir != str(Path.home() / '.gemini'):
        print(f"python3 setup_gemini_integration.py --gemini-dir '{data_dir}'")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())