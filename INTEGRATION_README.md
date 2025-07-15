# Gemini CLI Video Recording Integration

This integration allows you to use AI-guided video recording directly within Gemini CLI conversations. When you say "start a video recording and i will tell you the problem i want you to solve", Gemini will launch the video recorder, process your demonstration with AI-guided frame extraction, and then implement the requested changes.

## 🚀 Quick Setup

1. **Install Dependencies**:
   ```bash
   python3 cli_video_ext.py install
   ```

2. **Find Gemini CLI** (if needed):
   ```bash
   python3 find_gemini.py
   ```

3. **Set Up Integration**:
   ```bash
   # Auto-detect Gemini CLI (most common)
   python3 setup_gemini_integration.py
   
   # Or specify custom paths
   python3 setup_gemini_integration.py --gemini-path /path/to/gemini
   python3 setup_gemini_integration.py --gemini-dir ~/.config/gemini
   ```

4. **Test Integration**:
   ```bash
   python3 test_integration.py
   ```

## 🎬 How to Use

### In Gemini CLI:

1. **Start Recording**: Say any of these phrases:
   - "start a video recording and i will tell you the problem i want you to solve"
   - "record a video to show you the bug"  
   - "let me record my screen to demonstrate the issue"

2. **Record Your Problem**: 
   - Browser window opens automatically
   - Click "Start Recording"
   - Select screen/window to record
   - **SPEAK CLEARLY** about what you want fixed
   - Demonstrate the problem visually
   - Recording auto-stops after 30 seconds

3. **AI Analysis**: 
   - Video processed with AI-guided frame extraction
   - Frames extracted at moments when you mention specific problems
   - Timeline visualization created
   - Transcript generated with word-level timestamps

4. **Implementation**: 
   - Gemini receives context with frames and transcript
   - Analyzes your demonstration
   - Implements the requested changes
   - Provides code solutions

## 🔧 Technical Architecture

### Workflow Process:
```
User Request → Gemini CLI → Video Handler → Video Recorder → AI Analysis → Context → Implementation
```

### Key Components:
- **`gemini_video_handler.py`**: Main integration handler
- **`video_recorder.py`**: Core video processing with AI-guided extraction
- **`cli_video_ext.py`**: Command-line interface
- **`setup_gemini_integration.py`**: Installation and setup

### AI-Guided Frame Extraction:
1. **Word-Level Transcription**: Uses OpenAI Whisper with word timestamps
2. **Timeline Visualization**: Creates visual timeline of speech
3. **AI Analysis**: Calls Gemini to analyze transcript and suggest optimal frame timestamps
4. **Intelligent Extraction**: Extracts frames at moments when you mention specific problems
5. **Context Generation**: Creates rich markdown with frame reasoning and timeline

## 📋 Example Interaction

```
User: "start a video recording and i will tell you the problem i want you to solve"

Gemini: "I'll start a video recording for you. Please demonstrate the problem clearly and speak about what you want me to fix."

[Video recording process starts]

User: [Records screen showing a bug, saying "There's a login error on this page, the submit button doesn't work when I click it"]

[AI processing completes]

Gemini: "I've analyzed your video recording. I can see the login form issue you demonstrated. Based on the frame at 00:08 where you clicked the submit button, I can see the problem. Let me fix the button handler..."

[Implements the fix]
```

## 🎯 AI-Guided Features

### Smart Frame Selection:
- ❌ **Old**: Frames at 2s, 7s, 12s (often irrelevant)
- ✅ **New**: Frames when you say "login error", "submit button", "doesn't work"

### Timeline Intelligence:
```
Time axis - 0s--------1s--------2s--------3s--------4s--------5s--------6s--------7s--------8s
Text axis  - I have a login error on this page, the submit button doesn't work when I click it
```

### Context Quality:
- **Frame 1**: Shows login form (when you said "login error")
- **Frame 2**: Shows submit button click (when you said "doesn't work")
- **Frame 3**: Shows error state (when you said "button doesn't work")

## 🛠️ Configuration

### Video Settings:
```python
CONFIG = {
    'MAX_RECORDING_DURATION': 30,  # seconds
    'MAX_FRAMES': 6,               # AI-guided frames
    'MIN_FRAMES': 2,               # minimum frames
    'AI_ANALYSIS_TIMEOUT': 30,     # seconds
    'SILENT_VIDEO_INTERVALS': [2, 7, 12, 17, 22]  # for silent videos
}
```

### Fallback Modes:
1. **AI-Guided**: Uses Gemini to analyze transcript and suggest frame timestamps
2. **Speech Segments**: Extracts frames at speech segment midpoints
3. **Silent Video**: Uses fixed intervals [2, 7, 12, 17, 22] seconds

## 🔍 Troubleshooting

### Common Issues:

1. **"Gemini CLI not found"**:
   - Run: `python3 find_gemini.py` to locate Gemini CLI
   - Use `--gemini-path` option to specify custom path
   - Install Gemini CLI if not found
   - Common locations:
     - Linux: `/usr/local/bin/gemini`, `~/.local/bin/gemini`
     - Windows: `%APPDATA%\Local\gemini\`, `C:\Program Files\gemini\`
     - macOS: `/Applications/Gemini.app/Contents/MacOS/gemini`

2. **"Video extension dependencies missing"**:
   - Run: `python3 cli_video_ext.py install`

3. **"AI analysis timeout"**:
   - Check Gemini CLI is responding
   - Verify network connectivity

4. **"No frames extracted"**:
   - Check FFmpeg is installed
   - Verify video file was created

5. **"Silent video fallback"**:
   - Check microphone permissions
   - Ensure audio is being recorded

### Debug Mode:
```bash
python3 gemini_video_handler.py record
```

## 📊 Performance

- **Recording**: 30 seconds max
- **Processing**: ~30-60 seconds
- **AI Analysis**: ~10-30 seconds  
- **Total Time**: ~1-2 minutes

## 🔒 Privacy & Security

- All processing happens locally
- No cloud uploads for video/audio
- Temporary files auto-deleted after processing
- Only Gemini CLI calls are made for AI analysis

## 🚀 Future Enhancements

- [ ] Support for longer recordings
- [ ] Multiple language support
- [ ] Visual change detection
- [ ] Custom frame extraction rules
- [ ] Integration with other CLI agents

## 📞 Support

If you encounter issues:
1. Run: `python3 test_integration.py`
2. Check the output for specific error messages
3. Verify all dependencies are installed
4. Ensure Gemini CLI is working properly

---

**Ready to test?** Run `python3 setup_gemini_integration.py` and start using AI-guided video recording in Gemini CLI! 🎉