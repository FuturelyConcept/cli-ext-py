# CLI Video Extension for Code Agents (Python)

🎥 **Privacy-first video recording extension for CLI code agents (Gemini CLI, Claude Code, etc.)**

This Python-based extension allows you to record your screen and audio, transcribe the audio using OpenAI's Whisper locally, and extract key frames to provide rich visual and auditory context for AI-powered debugging and development assistance.

## ✨ Features

- **🔒 Privacy-First**: All processing happens locally - no data leaves your machine
- **📹 Browser-Based Recording**: User-friendly web interface for screen recording
- **🤖 Local AI Transcription**: Uses OpenAI Whisper for high-quality speech-to-text
- **⚡ Smart Frame Extraction**: Captures frames at strategic intervals (2, 7, 12, 17, 22 seconds)
- **🎯 Developer-Focused**: Perfect for bug reports and enhancement requests
- **🌐 Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/)
2. **pip**: Python's package installer (usually comes with Python)
3. **FFmpeg**: Required for video processing
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt-get install ffmpeg`

### Installation

1. **Clone or download** this repository
2. **Navigate** to the `cli-ext-py` directory:
   ```bash
   cd cli-ext-py
   ```
3. **Install dependencies**:
   ```bash
   python cli_video_ext.py install
   ```
   Or manually:
   ```bash
   pip install -r requirements.txt
   ```

### Usage

#### Basic Recording
```bash
python cli_video_ext.py record
```

#### Check Dependencies
```bash
python cli_video_ext.py check
```

#### Install Dependencies
```bash
python cli_video_ext.py install
```

### Integration with CLI Agents

Add this to your CLI agent's command registry:

```bash
# For Gemini CLI or Claude Code
/video    # This would trigger: python cli_video_ext.py record
```

## 🎬 How It Works

1. **Start Recording**: Run the CLI command to open a browser window
2. **Record Screen**: Select screen/window/tab to record (up to 30 seconds)
3. **Capture Audio**: Speak about the issue or feature you want addressed
4. **Auto-Processing**: 
   - Extracts frames at 2, 7, 12, 17, 22 second intervals
   - Transcribes audio using Whisper
   - Generates markdown context for the AI agent
5. **Context Generation**: Returns formatted context with images and transcript

## 📋 Example Output

```markdown
# Video Recording Context

**Recording Duration**: 25.3 seconds
**Frames Extracted**: 5

## Visual Context

### Frame 1 - Time: 00:02
**Image**: `temp_session_20240714_143052/frames/frame-02s.png`

### Frame 2 - Time: 00:07
**Image**: `temp_session_20240714_143052/frames/frame-07s.png`

## Audio Transcript

```
[00:03] This login button is broken when I click it
[00:08] The search feature isn't working properly
[00:15] Can you add a dark mode option please
```

## Instructions

Please analyze the provided frame images and transcript to understand the developer's request.
The frames show the application state at different time intervals during the recording.
Use this visual and audio context to implement the requested changes or fixes.
```

## 🛠️ Technical Architecture

### Core Components

1. **`cli_video_ext.py`**: Main CLI interface and dependency management
2. **`video_recorder.py`**: Flask server with HTML interface for recording
3. **`main.py`**: Original direct FFmpeg implementation (deprecated)

### Technology Stack

- **Flask**: Web server for recording interface
- **OpenAI Whisper**: Local speech-to-text transcription
- **FFmpeg-Python**: Video processing and frame extraction
- **HTML5 MediaRecorder**: Browser-based screen recording

### Recording Process

```
User Command → Browser Opens → Screen Recording → Video Upload → 
Frame Extraction → Audio Transcription → Context Generation → CLI Output
```

## 🔒 Privacy Guarantees

**ZERO DATA TRANSFER:**
- ✅ All video and audio processing happens locally
- ✅ No cloud storage or API calls for transcription
- ✅ Original video and audio files are automatically deleted after processing
- ✅ No user tracking or data collection
- ✅ No API keys required for transcription

## 🚨 Troubleshooting

### Common Issues

1. **"FFmpeg not found"**
   - Ensure FFmpeg is installed and in your PATH
   - Test with: `ffmpeg -version`

2. **"Permission denied" errors**
   - Grant microphone/screen recording permissions to your terminal
   - On macOS: System Preferences → Security & Privacy → Privacy

3. **"Module not found" errors**
   - Run: `python cli_video_ext.py install`
   - Or: `pip install -r requirements.txt`

4. **Browser doesn't open**
   - Manually navigate to `http://localhost:8765?autostart=true`
   - Check firewall settings

5. **No audio in recording**
   - Ensure "Share system audio" is selected in browser prompt
   - Check microphone permissions

### Performance Tips

- Use `tiny` or `base` Whisper model for faster processing
- Ensure sufficient disk space for temporary files
- Close unnecessary applications during recording

## 📝 Configuration

Edit `CONFIG` in `video_recorder.py` to customize:

```python
CONFIG = {
    'MAX_RECORDING_DURATION': 30,  # seconds
    'FRAME_TIMESTAMPS': [2, 7, 12, 17, 22, 27],  # seconds
    'PORT': 8765,
    'WHISPER_MODEL': 'base'  # tiny, base, small, medium, large
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🔗 Related Projects

- [Gemini CLI](https://github.com/google/gemini-cli) - Google's CLI for Gemini
- [Claude Code](https://claude.ai/code) - Anthropic's coding assistant
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition

---

**Built with ❤️ for developers by developers**