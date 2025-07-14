@echo off
echo Installing CLI Video Extension dependencies for Windows...
echo.

echo Step 1: Installing Python dependencies...
python -m pip install flask==2.3.3 werkzeug==2.3.7 openai-whisper==20231117 ffmpeg-python==0.2.0

echo.
echo Step 2: Checking installation...
python cli_video_ext.py check

echo.
echo Installation complete!
echo.
echo To test the video recorder, run:
echo   python cli_video_ext.py record
echo.
pause