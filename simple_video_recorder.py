#!/usr/bin/env python3
"""
Simple Video Recorder for Gemini CLI
Just records video, transcribes audio, and outputs clean results
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime


def create_session_dir():
    """Create session directory in current working directory"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_dir = Path.cwd() / '.gemini' / 'video_ext' / f'video_session_{timestamp}'
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def start_recording(session_dir):
    """Start video recording using browser"""
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Video Recording</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
        button { padding: 15px 30px; font-size: 18px; margin: 10px; cursor: pointer; }
        #startBtn { background: #4CAF50; color: white; border: none; }
        #stopBtn { background: #f44336; color: white; border: none; display: none; }
        #status { margin: 20px 0; font-size: 16px; }
    </style>
</head>
<body>
    <h1>Video Recording for Gemini CLI</h1>
    <div id="status">Click Start to begin recording</div>
    <button id="startBtn" onclick="startRecording()">Start Recording</button>
    <button id="stopBtn" onclick="stopRecording()">Stop Recording</button>
    
    <script>
        let mediaRecorder;
        let recordedChunks = [];
        
        async function startRecording() {
            try {
                const stream = await navigator.mediaDevices.getDisplayMedia({
                    video: true,
                    audio: true
                });
                
                mediaRecorder = new MediaRecorder(stream);
                recordedChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = async () => {
                    const blob = new Blob(recordedChunks, { type: 'video/webm' });
                    const formData = new FormData();
                    formData.append('video', blob, 'recording.webm');
                    
                    try {
                        const response = await fetch('/upload', {
                            method: 'POST',
                            body: formData
                        });
                        
                        if (response.ok) {
                            document.getElementById('status').textContent = 'Recording saved! Processing...';
                            setTimeout(() => window.close(), 2000);
                        } else {
                            document.getElementById('status').textContent = 'Error saving recording';
                        }
                    } catch (error) {
                        document.getElementById('status').textContent = 'Error: ' + error.message;
                    }
                };
                
                mediaRecorder.start();
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
                document.getElementById('status').textContent = 'Recording... Click Stop when finished';
                
            } catch (error) {
                document.getElementById('status').textContent = 'Error: ' + error.message;
            }
        }
        
        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
                document.getElementById('stopBtn').style.display = 'none';
                document.getElementById('status').textContent = 'Stopping recording...';
            }
        }
    </script>
</body>
</html>
'''
    
    # Save HTML file
    html_file = session_dir / 'recorder.html'
    with open(html_file, 'w') as f:
        f.write(html_content)
    
    # Start simple HTTP server
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import cgi
    import threading
    import webbrowser
    
    video_file = None
    server_running = True
    
    class RecorderHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode())
            else:
                self.send_error(404)
        
        def do_POST(self):
            nonlocal video_file, server_running
            if self.path == '/upload':
                try:
                    content_type = self.headers['Content-Type']
                    if 'multipart/form-data' in content_type:
                        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
                        video_data = form['video'].file.read()
                        
                        video_file = session_dir / 'recording.webm'
                        with open(video_file, 'wb') as f:
                            f.write(video_data)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        self.wfile.write(b'OK')
                        
                        # Stop server
                        server_running = False
                        threading.Timer(1.0, lambda: os._exit(0)).start()
                        
                except Exception as e:
                    self.send_error(500, str(e))
            else:
                self.send_error(404)
    
    # Start server
    server = HTTPServer(('localhost', 8000), RecorderHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Open browser
    webbrowser.open('http://localhost:8000')
    
    # Wait for recording to complete
    print("Recording in progress... Please record your screen and click Stop when finished.")
    while server_running:
        time.sleep(1)
    
    server.shutdown()
    return video_file


def extract_audio(video_file, session_dir):
    """Extract audio from video"""
    if not video_file or not video_file.exists():
        return None
    
    audio_file = session_dir / 'audio.wav'
    
    # Find FFmpeg
    current_dir = Path(__file__).parent
    ffmpeg_path = current_dir / 'bin' / 'ffmpeg.exe'
    
    if not ffmpeg_path.exists():
        # Try system FFmpeg
        ffmpeg_path = 'ffmpeg'
    
    try:
        cmd = [str(ffmpeg_path), '-i', str(video_file), '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', str(audio_file), '-y']
        subprocess.run(cmd, check=True, capture_output=True)
        return audio_file
    except:
        return None


def transcribe_audio(audio_file, session_dir):
    """Transcribe audio using Whisper"""
    if not audio_file or not audio_file.exists():
        return None
    
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(str(audio_file), word_timestamps=True)
        
        # Create word timeline CSV
        csv_file = session_dir / 'word_timeline.csv'
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('word,start_time,end_time\n')
            for segment in result.get('segments', []):
                for word_info in segment.get('words', []):
                    word = word_info.get('word', '').strip()
                    start = word_info.get('start', 0)
                    end = word_info.get('end', 0)
                    f.write(f'"{word}",{start},{end}\n')
        
        return csv_file
    except:
        return None


def main():
    try:
        # Create session directory
        session_dir = create_session_dir()
        
        # Start recording
        video_file = start_recording(session_dir)
        
        if not video_file:
            print("No video recorded")
            return
        
        # Extract audio
        audio_file = extract_audio(video_file, session_dir)
        
        # Transcribe audio
        csv_file = transcribe_audio(audio_file, session_dir)
        
        # Output result
        if csv_file and csv_file.exists():
            relative_path = os.path.relpath(csv_file, Path.cwd()).replace('\\', '/')
            print(f"Video recorded and transcribed. Please analyze this timeline and tell me which timestamps to extract frames from:")
            print(f"@{relative_path}")
        else:
            print("Video recorded but transcription failed. Please describe what you want help with.")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()