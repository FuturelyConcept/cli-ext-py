#!/usr/bin/env python3
"""
Windows Test Script for Video Recording Extension
Run this on Windows to test audio extraction and whisper transcription
"""

import os
import sys
from pathlib import Path
import subprocess

def test_ffmpeg():
    """Test if FFmpeg is available and working"""
    print("=" * 60)
    print("TESTING FFMPEG")
    print("=" * 60)
    
    # Check multiple locations for FFmpeg
    ffmpeg_paths = []
    
    # 1. System PATH
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            ffmpeg_paths.append(('System PATH', 'ffmpeg'))
    except:
        pass
    
    # 2. Local bin directory (project)
    script_dir = Path(__file__).parent
    local_ffmpeg = script_dir / 'bin' / 'ffmpeg.exe'
    if local_ffmpeg.exists():
        try:
            result = subprocess.run([str(local_ffmpeg), '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ffmpeg_paths.append(('Local bin (project)', str(local_ffmpeg)))
        except:
            pass
    
    # 3. Extension bin directory
    extension_ffmpeg = Path("C:/Users/Deepika_Akshaj/.gemini/extensions/video-recording/bin/ffmpeg.exe")
    if extension_ffmpeg.exists():
        try:
            result = subprocess.run([str(extension_ffmpeg), '-version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ffmpeg_paths.append(('Extension bin', str(extension_ffmpeg)))
        except:
            pass
    
    if ffmpeg_paths:
        print("✓ FFmpeg found in multiple locations:")
        for location, path in ffmpeg_paths:
            print(f"  - {location}: {path}")
        
        # Get version from the first working one
        try:
            if ffmpeg_paths[0][1] == 'ffmpeg':
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run([ffmpeg_paths[0][1], '-version'], capture_output=True, text=True, timeout=5)
            version_line = result.stdout.split('\n')[0]
            print(f"Version: {version_line}")
        except:
            print("Version: Could not determine")
        
        return True
    else:
        print("✗ FFmpeg not found in any location")
        print("Checked:")
        print("  - System PATH")
        print(f"  - Local bin: {local_ffmpeg}")
        print(f"  - Extension bin: {extension_ffmpeg}")
        return False

def test_whisper():
    """Test if Whisper is available and working"""
    print("\n" + "=" * 60)
    print("TESTING WHISPER")
    print("=" * 60)
    
    try:
        import whisper
        print("✓ Whisper module imported successfully")
        
        # Test loading a model
        print("Loading Whisper model...")
        model = whisper.load_model('base')
        print("✓ Whisper model loaded successfully")
        return True
        
    except ImportError:
        print("✗ Whisper not installed")
        print("Install with: pip install openai-whisper")
        return False
    except Exception as e:
        print(f"✗ Whisper error: {e}")
        return False

def test_audio_extraction(video_path):
    """Test audio extraction from video"""
    print("\n" + "=" * 60)
    print("TESTING AUDIO EXTRACTION")
    print("=" * 60)
    
    if not os.path.exists(video_path):
        print(f"✗ Video file not found: {video_path}")
        return False
    
    video_file = Path(video_path)
    print(f"Video file: {video_file}")
    print(f"Video size: {video_file.stat().st_size:,} bytes")
    
    # Find FFmpeg executable
    ffmpeg_exe = None
    
    # Check multiple locations
    locations = [
        'ffmpeg',  # System PATH
        Path(__file__).parent / 'bin' / 'ffmpeg.exe',  # Local bin
        Path("C:/Users/Deepika_Akshaj/.gemini/extensions/video-recording/bin/ffmpeg.exe")  # Extension bin
    ]
    
    for location in locations:
        try:
            if location == 'ffmpeg':
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    ffmpeg_exe = 'ffmpeg'
                    print(f"Using FFmpeg from: System PATH")
                    break
            elif Path(location).exists():
                result = subprocess.run([str(location), '-version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    ffmpeg_exe = str(location)
                    print(f"Using FFmpeg from: {location}")
                    break
        except:
            continue
    
    if not ffmpeg_exe:
        print("✗ No working FFmpeg found for audio extraction")
        return False
    
    # Test audio extraction
    audio_path = video_file.parent / "test_audio.wav"
    
    try:
        cmd = [
            ffmpeg_exe, '-i', str(video_path),
            '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
            '-y', str(audio_path)
        ]
        
        print("Running audio extraction...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and audio_path.exists():
            audio_size = audio_path.stat().st_size
            print(f"✓ Audio extracted successfully")
            print(f"Audio file: {audio_path}")
            print(f"Audio size: {audio_size:,} bytes")
            
            if audio_size > 1000:
                return str(audio_path)
            else:
                print("✗ Audio file too small, likely no audio track")
                return False
        else:
            print("✗ Audio extraction failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Audio extraction error: {e}")
        return False

def test_whisper_transcription(audio_path):
    """Test Whisper transcription"""
    print("\n" + "=" * 60)
    print("TESTING WHISPER TRANSCRIPTION")
    print("=" * 60)
    
    if not audio_path or not os.path.exists(audio_path):
        print("✗ No audio file to test")
        return False
    
    try:
        import whisper
        print("Loading Whisper model...")
        model = whisper.load_model('base')
        
        print("Transcribing audio...")
        result = model.transcribe(audio_path, word_timestamps=True, verbose=False)
        
        print(f"✓ Transcription completed")
        print(f"Text: {result.get('text', 'No text')}")
        print(f"Segments: {len(result.get('segments', []))}")
        
        if result.get('segments'):
            print("\nSegments:")
            for i, segment in enumerate(result['segments'][:3]):  # Show first 3
                start = segment['start']
                end = segment['end']
                text = segment['text'].strip()
                print(f"  {i+1}. [{start:.1f}s - {end:.1f}s]: {text}")
        
        return True
        
    except Exception as e:
        print(f"✗ Whisper transcription error: {e}")
        return False

def test_dependencies():
    """Test all Python dependencies"""
    print("\n" + "=" * 60)
    print("TESTING PYTHON DEPENDENCIES")
    print("=" * 60)
    
    deps = ['flask', 'whisper', 'ffmpeg', 'werkzeug']
    missing = []
    
    for dep in deps:
        try:
            if dep == 'whisper':
                import whisper
            elif dep == 'ffmpeg':
                import ffmpeg
            elif dep == 'flask':
                import flask
            elif dep == 'werkzeug':
                import werkzeug
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep}")
            missing.append(dep)
    
    if missing:
        print(f"\nMissing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing.replace('whisper', 'openai-whisper') for dep in missing))
        return False
    
    return True

def main():
    """Main test function"""
    print("Windows Video Recording Extension Test")
    print("Run this script on Windows to test the extension components")
    print()
    
    # Test 1: Dependencies
    deps_ok = test_dependencies()
    
    # Test 2: FFmpeg
    ffmpeg_ok = test_ffmpeg()
    
    # Test 3: Whisper
    whisper_ok = test_whisper()
    
    # Test 4: Audio extraction (if video file provided)
    video_path = None
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # Try to find the most recent video
        possible_paths = [
            Path.cwd() / ".gemini" / "video_ext",
            Path("C:/Users/Deepika_Akshaj/manoj/play/.gemini/video_ext")
        ]
        
        for base_path in possible_paths:
            if base_path.exists():
                # Find most recent session
                sessions = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith('video_session_')]
                if sessions:
                    latest_session = max(sessions, key=lambda x: x.stat().st_mtime)
                    video_file = latest_session / "uploads" / "recording.webm"
                    if video_file.exists():
                        video_path = str(video_file)
                        break
    
    audio_path = None
    if video_path:
        audio_path = test_audio_extraction(video_path)
    else:
        print("\n" + "=" * 60)
        print("SKIPPING AUDIO EXTRACTION - NO VIDEO FILE")
        print("=" * 60)
        print("Usage: python test_windows.py [path_to_video_file]")
    
    # Test 5: Whisper transcription
    if audio_path and whisper_ok:
        test_whisper_transcription(audio_path)
    else:
        print("\n" + "=" * 60)
        print("SKIPPING WHISPER TRANSCRIPTION")
        print("=" * 60)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Dependencies: {'✓' if deps_ok else '✗'}")
    print(f"FFmpeg: {'✓' if ffmpeg_ok else '✗'}")
    print(f"Whisper: {'✓' if whisper_ok else '✗'}")
    print(f"Audio Extraction: {'✓' if audio_path else '✗'}")
    print(f"Transcription: {'✓' if audio_path and whisper_ok else '✗'}")
    
    if all([deps_ok, ffmpeg_ok, whisper_ok]):
        print("\n🎉 All components working! Extension should work properly.")
    else:
        print("\n⚠️  Some components failed. Fix the issues above.")

if __name__ == "__main__":
    main()