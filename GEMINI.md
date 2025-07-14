# Gemini CLI Video Extension (Python) Development Context

This `cli-ext-py` subdirectory was created to develop a Python-based video recording and transcription extension for the Gemini CLI. This decision was made to address the limitations and billing requirements of the Google Cloud Speech-to-Text API when used with the Node.js extension, and to leverage the local, free, and high-quality transcription capabilities of OpenAI's Whisper.

## Key Decisions & Implementation:

*   **Language:** Python was chosen for its robust libraries for audio/video processing (`ffmpeg-python`) and local speech-to-text (`openai-whisper`).
*   **Transcription:** OpenAI's Whisper is the chosen transcription engine, running locally to avoid cloud billing and usage limits.
*   **Video/Audio Capture:** Relies on `ffmpeg` as an external dependency, which users will need to install.
*   **Project Structure:**
    *   `requirements.txt`: Lists Python dependencies (`openai-whisper`, `ffmpeg-python`).
    *   `main.py`: Contains the core logic for recording, audio/frame extraction, transcription, and context generation.
    *   `README.md`: Provides setup and usage instructions for the Python extension.
*   **Authentication:** This Python extension will *not* require `GEMINI_API_KEY` export or `gcloud auth application-default login` for transcription, as Whisper runs entirely locally.

## Next Steps:

The `main.py` currently has a Windows-centric `record_video` function. Further development will involve making this cross-platform and integrating it with the Gemini CLI's extension mechanism.
