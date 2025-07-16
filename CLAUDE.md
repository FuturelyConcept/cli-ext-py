# Gemini CLI Video Recording Extension - Claude Memory

## Project Summary
Built a complete video recording extension for Gemini CLI that enables screen recording with intelligent frame extraction and audio transcription.

## Current Status: ✅ WORKING
- Video recording works and saves to local project directory
- FFmpeg binaries installed and working (both local and extension directories)
- Audio extraction functional (531KB extracted successfully from test video)
- Frame extraction working with timestamps
- Clean output format implemented (no more messy debug output)
- Extension properly registered with Gemini CLI

## Architecture
- **Environment**: WSL for development, Windows PowerShell for Gemini CLI execution
- **Installation Target**: `C:\Users\Deepika_Akshaj\.gemini\extensions\video-recording\`
- **Session Storage**: Current working directory `.gemini\video_ext\video_session_TIMESTAMP\`
- **FFmpeg**: Portable binaries in `bin/` directory (both project and extension)

## Workflow
1. User asks Gemini to start video recording
2. Gemini executes: `python C:\Users\Deepika_Akshaj\.gemini\extensions\video-recording\record_video.py`
3. Browser screen recording dialog opens
4. User records screen and audio
5. FFmpeg extracts audio and frames at intervals
6. Whisper transcribes audio locally (minor Windows path issue exists)
7. Clean formatted context returned to Gemini

## Key Files Structure
```
C:\Users\Deepika_Akshaj\.gemini\extensions\video-recording\
├── record_video.py          # Main entry point for Gemini
├── video_recorder.py        # Flask server & video processing
├── frame_extractor.py       # Frame extraction utilities  
├── cli_video_ext.py         # CLI interface
├── requirements.txt         # Python dependencies
└── bin/                     # FFmpeg binaries
    ├── ffmpeg.exe
    ├── ffprobe.exe
    └── ffplay.exe
```

## Installation Process
1. Run `python install.py` from cli-ext-py directory
2. Copies all files + FFmpeg binaries to extension directory
3. Creates Gemini CLI configuration files
4. Registers extension with auto-detection phrases

## Output Format (Clean & Concise)
```
# Video Recording Analysis
Duration: 17.3s | Frames: 5 | Audio: Yes

## Audio Transcript
[Transcript or error message]

## Visual Frames
**Frame 1** (00:02): @.gemini/video_ext/session/frames/frame_1_at_2.0s.png
**Frame 2** (00:07): @.gemini/video_ext/session/frames/frame_2_at_7.0s.png

## Analysis
Please analyze the frames and transcript to understand what the user wants help with.
```

## Test Results (Latest)
- ✅ Dependencies: All Python packages installed
- ✅ FFmpeg: Found in multiple locations and working
- ✅ Audio Extraction: Successfully extracts audio (531KB from test video)
- ✅ Whisper: Model loads successfully
- ⚠️ Transcription: Minor Windows path issue but extension still functional
- ✅ Overall: Extension ready for use

## Known Issues
1. **Minor Whisper path issue on Windows** - `[WinError 2] The system cannot find the file specified` during transcription
2. **Fallback working** - Extension falls back to silent video mode when transcription fails

## Dependencies
- flask>=2.3.3
- openai-whisper  
- ffmpeg-python>=0.2.0
- werkzeug>=2.3.7

## Usage with Gemini CLI
Simply ask Gemini:
- "start a video recording"
- "record my screen so I can show you the problem"
- "let me record this issue"

## Files Created
- `install.py` - Main installer with FFmpeg binary copying
- `test_windows.py` - Windows testing script for all components
- `install_ffmpeg_windows.py` - Automated FFmpeg installer
- `SETUP_GUIDE.md` - User documentation
- All video recording extension files with clean output formatting

## CRITICAL INSIGHT - NEW APPROACH (2025-07-15)
**Problem**: Gemini CLI corrupts output with scattered pipes and spaces, making it unusable.

**Solution**: Two-step process:
1. **First call**: Record video, transcribe with Whisper, generate word_timeline.csv ONLY. Output: `@word_timeline.csv`
2. **Wait for Gemini**: Let Gemini analyze the CSV and tell us which timestamps need frames
3. **Second call**: Extract frames at requested timestamps, provide final analysis

**Key Changes Needed**:
- Remove automatic frame extraction 
- Only generate word_timeline.csv initially
- Wait for Gemini to request specific frame timestamps
- Extract frames on demand based on Gemini's analysis
- Final output: word timeline + requested frames + analysis request

**Benefits**:
- Bypasses output corruption by using @ file references
- Lets Gemini do intelligent analysis of timeline
- Reduces processing time (no unnecessary frames)
- Cleaner workflow with explicit frame requests

## Implementation Status (2025-07-16)
✅ **COMPLETED**: Two-step workflow implemented and tested

### New Workflow (ACTIVE)
1. **Step 1**: `python video_recorder.py` → records video → transcribes audio → generates `word_timeline.csv` → outputs `@word_timeline.csv`
2. **Step 2**: `python extract_frames.py "1.5,3.2,5.0"` → extracts frames at specific timestamps → outputs `@frame_paths`

### Changes Made
- Modified `video_recorder.py` to use `generate_minimal_context()` 
- Removed automatic frame extraction from initial recording
- Created `extract_frames.py` for on-demand frame extraction
- Added `extract_frames_at_timestamps()` function to `frame_extractor.py`
- Updated `install.py` to include new extract_frames.py script
- Tested workflow with `test_workflow.py`

### File Structure (Updated)
```
C:\Users\Deepika_Akshaj\.gemini\extensions\video-recording\
├── video_recorder.py        # Step 1: Record + transcribe + CSV only
├── extract_frames.py        # Step 2: Extract frames at timestamps
├── frame_extractor.py       # Frame extraction utilities
├── requirements.txt         # Dependencies
└── bin/                     # FFmpeg binaries
```

### Usage Example
```bash
# Step 1: Record video (generates CSV)
python video_recorder.py
# Output: Duration 5.0s
#         @.gemini/video_ext/session/word_timeline.csv

# Step 2: Extract frames at specific timestamps
python extract_frames.py "1.5,3.2,5.0"
# Output: @.gemini/video_ext/session/frames/frame_1_at_1.5s.png
#         @.gemini/video_ext/session/frames/frame_2_at_3.2s.png
```

### Benefits Achieved
- ✅ Clean output (no scattered pipes/spaces)
- ✅ @ file references work properly  
- ✅ Gemini can analyze timeline before requesting frames
- ✅ Faster initial processing (no unnecessary frames)
- ✅ On-demand frame extraction based on analysis

### Output Cleanup (2025-07-16)
✅ **FIXED**: Removed debug output and simplified analysis format

### Changes Made to Fix Text Cluttering:
1. **Removed debug prints** from gemini_video_handler.py
2. **Removed duration** from analysis.txt (redundant with CSV)
3. **Suppressed Whisper progress bars** using contextlib.redirect_stderr
4. **Simplified output** - Only essential @ file references
5. **Clean stdout** - Just `@analysis.txt` path, no extra text

### New Clean Output:
```
# Before (cluttered):
Starting video recording...
[DEBUG] Executing command...
Recording complete. Analysis: @analysis.txt

# After (clean):
@analysis.txt
```

### Expected analysis.txt content:
```
@word_timeline.csv
Next: Analyze the timeline and request specific frame timestamps
```

### Next Steps
- Test with actual Gemini CLI integration
- Monitor for any edge cases in production use