# Gemini CLI Video Recording Extension - Setup Guide

## Overview
This extension allows you to record your screen and audio from within Gemini CLI, with intelligent frame extraction and transcription.

## Architecture
- **WSL Environment**: Development and source code
- **Windows PowerShell**: Gemini CLI execution
- **Installation Target**: `C:\Users\Deepika_Akshaj\.gemini\video-recording\`

## Workflow
1. User asks Gemini to start video recording
2. Gemini executes: `python C:\Users\Deepika_Akshaj\.gemini\video-recording\record_video.py`
3. Browser screen recording dialog opens
4. User records screen and audio
5. FFmpeg extracts audio and frames
6. Whisper transcribes audio with timeline
7. Frames are selected based on transcript
8. Context is returned to Gemini

## Installation Steps

### 1. Install Dependencies
```bash
# In WSL (cli-ext-py directory)
pip install -r requirements.txt
```

### 2. Run Installation Script
```bash
# In WSL (cli-ext-py directory)
python install.py
```

This will:
- Copy all necessary files to `C:\Users\Deepika_Akshaj\.gemini\video-recording\`
- Create main entry point (`record_video.py`)
- Install Python dependencies
- Test the installation

### 3. Test Installation
```bash
# In WSL (cli-ext-py directory)
python test_installation.py
```

### 4. Usage in Gemini CLI
From Windows PowerShell, in Gemini CLI:
```
Ask Gemini: "start a video recording and I will tell you the problem I want you to solve"
```

Gemini will execute:
```
python C:\Users\Deepika_Akshaj\.gemini\video-recording\record_video.py
```

## Key Files

### Source Files (cli-ext-py/)
- `install.py` - Installation script
- `video_recorder.py` - Main video recording logic
- `frame_extractor.py` - Frame extraction utilities
- `cli_video_ext.py` - CLI interface
- `requirements.txt` - Python dependencies

### Installed Files (C:\Users\Deepika_Akshaj\.gemini\video-recording\)
- `record_video.py` - Main entry point for Gemini
- `video_recorder.py` - Video recording server
- `frame_extractor.py` - Frame extraction
- `cli_video_ext.py` - CLI utilities
- `requirements.txt` - Dependencies

## Features
- Browser-based screen recording
- Audio extraction with FFmpeg
- Whisper transcription (local, no API keys)
- Intelligent frame extraction based on transcript
- Timeline visualization
- Privacy-first (all processing local)
- Cross-platform support

## Troubleshooting

### Common Issues
1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **FFmpeg Not Found**: Install FFmpeg and add to PATH
3. **Browser Won't Open**: Check firewall settings
4. **No Audio**: Ensure "Share system audio" is selected

### Testing
```bash
# Test basic functionality
python test_installation.py

# Test CLI extension
python cli_video_ext.py check

# Test dependencies
python cli_video_ext.py install
```

## Directory Structure
```
C:\Users\Deepika_Akshaj\.gemini\video-recording\
├── record_video.py          # Main entry point
├── video_recorder.py        # Flask server & processing
├── frame_extractor.py       # Frame extraction utilities
├── cli_video_ext.py         # CLI interface
├── requirements.txt         # Python dependencies
├── uploads/                 # Video uploads (temp)
├── frames/                  # Extracted frames (temp)
├── context/                 # Generated context (temp)
└── temp/                    # Temporary files
```

## Next Steps
1. Run the installation: `python install.py`
2. Test the setup: `python test_installation.py`
3. Use with Gemini CLI from Windows PowerShell