#!/usr/bin/env python3
"""
Python Video Recording Extension for CLI Code Agents
Uses Flask for web interface and OpenAI Whisper for local transcription
"""

import os
import sys
import json
import time
import shutil
import tempfile
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
from threading import Thread
import signal

from flask import Flask, render_template_string, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import whisper
import ffmpeg


# FFmpeg configuration - use local binaries if available
def get_ffmpeg_path():
    """Get FFmpeg executable path, prefer local bin directory"""
    script_dir = Path(__file__).parent
    local_ffmpeg = script_dir / 'bin' / 'ffmpeg.exe'
    
    if local_ffmpeg.exists():
        return str(local_ffmpeg)
    
    # Fallback to system PATH
    return 'ffmpeg'


def get_ffprobe_path():
    """Get FFprobe executable path, prefer local bin directory"""
    script_dir = Path(__file__).parent
    local_ffprobe = script_dir / 'bin' / 'ffprobe.exe'
    
    if local_ffprobe.exists():
        return str(local_ffprobe)
    
    # Fallback to system PATH
    return 'ffprobe'


# Set FFmpeg paths for ffmpeg-python
ffmpeg_path = get_ffmpeg_path()
ffprobe_path = get_ffprobe_path()

# Configure ffmpeg-python to use local binaries
os.environ['FFMPEG_BINARY'] = ffmpeg_path
os.environ['FFPROBE_BINARY'] = ffprobe_path

# Add bin directory to PATH so Whisper can find FFmpeg
script_dir = Path(__file__).parent
bin_dir = script_dir / 'bin'
if bin_dir.exists():
    original_path = os.environ.get('PATH', '')
    os.environ['PATH'] = str(bin_dir) + os.pathsep + original_path

# Silent setup - no debug output


# Configuration
CONFIG = {
    'MAX_RECORDING_DURATION': 30,  # seconds
    'FRAME_TIMESTAMPS': [2, 7, 12, 17, 22, 27],  # seconds
    'PORT': 8765,
    'UPLOAD_FOLDER': 'uploads',
    'FRAMES_FOLDER': 'frames',
    'WHISPER_MODEL': 'base'  # Options: tiny, base, small, medium, large
}

# Global variables
app = Flask(__name__)
session_dir = None
processing_complete = False
context_result = None
server_process = None


def create_session_directory():
    """Create a unique session directory for this recording"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    session_id = f"video_session_{timestamp}"
    
    # Use current working directory with .gemini folder for CLI agent compatibility
    current_dir = Path.cwd()
    gemini_dir = current_dir / '.gemini'
    session_path = gemini_dir / 'video_ext' / session_id
    
    # Create directory structure
    session_path.mkdir(parents=True, exist_ok=True)
    (session_path / CONFIG['UPLOAD_FOLDER']).mkdir(exist_ok=True)
    (session_path / CONFIG['FRAMES_FOLDER']).mkdir(exist_ok=True)
    
    return session_path


def get_video_duration(video_path):
    """Get video duration using ffprobe"""
    try:
        # Method 1: Try to get duration from format
        cmd = [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration_str = result.stdout.strip()
        if duration_str and duration_str != "N/A":
            return float(duration_str)
    except:
        pass
    
    try:
        # Method 2: Calculate from frame count and rate  
        cmd_frames = [ffprobe_path, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=nb_read_frames", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
        result_frames = subprocess.run(cmd_frames, capture_output=True, text=True, check=True)
        frame_count = int(result_frames.stdout.strip())
        
        cmd_rate = [ffprobe_path, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)]
        result_rate = subprocess.run(cmd_rate, capture_output=True, text=True, check=True)
        frame_rate_str = result_rate.stdout.strip()
        
        if '/' in frame_rate_str:
            num, den = frame_rate_str.split('/')
            frame_rate = float(num) / float(den)
        else:
            frame_rate = float(frame_rate_str)
        
        return frame_count / frame_rate
    except:
        pass
    
    return 5.0  # Fallback


def extract_frames_intelligent(video_path, frames_dir, duration, transcript_result=None):
    """Extract frames intelligently based on transcript, or use default intervals"""
    extracted_frames = []
    frames_path = Path(frames_dir)
    
    if transcript_result and 'segments' in transcript_result and len(transcript_result['segments']) > 0:
        # INTELLIGENT MODE: Extract frames based on speech segments
        segments = transcript_result['segments']
        
        # Use actual video duration from segments if longer than detected duration
        max_segment_end = max(segment['end'] for segment in segments)
        actual_duration = max(duration, max_segment_end)
        
        for i, segment in enumerate(segments):
            # Use middle of segment for better context
            segment_start = float(segment['start'])
            segment_end = float(segment['end'])
            timestamp = (segment_start + segment_end) / 2.0
            
            # Ensure timestamp is within video bounds
            if timestamp >= actual_duration:
                timestamp = max(0.0, actual_duration - 1.0)
            
            # Use the calculated midpoint timestamp for filename
            frame_filename = f"intelligent_segment_{i+1}_at_{timestamp:.1f}s.png"
            frame_path = frames_path / frame_filename
            
            try:
                (
                    ffmpeg
                    .input(str(video_path), ss=timestamp)
                    .output(str(frame_path), vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, cmd=ffmpeg_path)
                )
                
                if frame_path.exists():
                    extracted_frames.append({
                        'path': str(frame_path),
                        'timestamp': timestamp,
                        'type': 'intelligent',
                        'segment_text': segment['text'].strip(),
                        'segment_index': i,
                        'actual_duration': actual_duration  # Store for context generation
                    })
            except:
                pass  # Silent failure
    
    else:
        # DEFAULT MODE: Use standard intervals when no audio/transcript
        valid_timestamps = [ts for ts in CONFIG['FRAME_TIMESTAMPS'] if ts < duration]
        
        if not valid_timestamps and duration > 0:
            valid_timestamps = [min(2, duration - 0.5)] if duration >= 1 else [duration / 2]
        
        for timestamp in valid_timestamps:
            frame_filename = f"standard_{timestamp:02d}s.png"
            frame_path = frames_path / frame_filename
            
            try:
                (
                    ffmpeg
                    .input(str(video_path), ss=timestamp)
                    .output(str(frame_path), vframes=1)
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, cmd=ffmpeg_path)
                )
                
                if frame_path.exists():
                    extracted_frames.append({
                        'path': str(frame_path),
                        'timestamp': timestamp,
                        'type': 'standard',
                        'segment_text': None,
                        'segment_index': None
                    })
            except:
                pass  # Silent failure
    
    return extracted_frames


def extract_audio(video_path, audio_path):
    """Extract audio from video for transcription"""
    try:
        (
            ffmpeg
            .input(video_path)
            .output(str(audio_path), acodec='pcm_s16le', ar=16000, ac=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True, cmd=ffmpeg_path)
        )
        return True
    except Exception:
        return False


def transcribe_audio_whisper_with_segments(audio_path):
    """Transcribe audio using OpenAI Whisper, return both formatted text and raw result"""
    try:
        audio_file = Path(audio_path)
        if not audio_file.exists() or audio_file.stat().st_size == 0:
            return "[No audio detected]", None
        
        # Load and transcribe (suppress warnings)
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = whisper.load_model(CONFIG['WHISPER_MODEL'])
            result = model.transcribe(str(audio_path))
        
        # Format transcript
        if not result.get('segments') or len(result['segments']) == 0:
            text = result.get('text', '').strip()
            return f"[00:00] {text}" if text else "[No speech detected]", result
        
        formatted_transcript = []
        for segment in result['segments']:
            start_time = segment['start']
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            text = segment['text'].strip()
            if text:
                formatted_transcript.append(f"{timestamp} {text}")
        
        final_transcript = '\n'.join(formatted_transcript) if formatted_transcript else "[No speech detected]"
        return final_transcript, result
    
    except Exception:
        return "[Error in recording, please try again]", None


def process_video(video_path):
    """Process uploaded video: extract frames, transcribe audio, generate context"""
    global context_result, processing_complete, server_process
    
    try:
        # Get video duration
        duration = get_video_duration(video_path)
        
        # Extract and transcribe audio first (to inform intelligent frame extraction)
        audio_path = session_dir / 'audio.wav'
        transcript_result = None
        transcript_text = "[No audio detected]"
        
        if extract_audio(video_path, audio_path):
            if audio_path.exists() and audio_path.stat().st_size > 0:
                # Transcribe audio and get full result for intelligent processing
                transcript_text, transcript_result = transcribe_audio_whisper_with_segments(audio_path)
            else:
                transcript_text = "[Audio extraction failed]"
        else:
            transcript_text = "[No audio track in video]"
        
        # Extract frames intelligently based on transcript (or use defaults)
        frames_dir = session_dir / CONFIG['FRAMES_FOLDER']
        
        # If we have transcript segments, extract frames for ALL segments
        if transcript_result and 'segments' in transcript_result and len(transcript_result['segments']) > 0:
            # Use the actual duration from transcript for better accuracy
            max_segment_end = max(segment['end'] for segment in transcript_result['segments'])
            actual_duration = max(duration, max_segment_end)
            extracted_frames = extract_frames_intelligent(video_path, frames_dir, actual_duration, transcript_result)
        else:
            extracted_frames = extract_frames_intelligent(video_path, frames_dir, duration, transcript_result)
        
        # Generate context with intelligent formatting
        context = generate_context_intelligent(duration, transcript_text, extracted_frames)
        
        context_result = context
        processing_complete = True
        
        # Shutdown server after processing
        if server_process:
            Thread(target=shutdown_server, daemon=True).start()
        
        return context
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in process_video: {str(e)}", file=sys.stderr)
        print(f"Full traceback: {error_details}", file=sys.stderr)
        
        error_msg = f"Error in recording: {str(e)}"
        context_result = error_msg
        processing_complete = True
        
        # Shutdown server even on error
        if server_process:
            Thread(target=shutdown_server, daemon=True).start()
        
        return error_msg


def shutdown_server():
    """Shutdown the Flask server after a brief delay"""
    time.sleep(2)  # Give time for final HTTP response
    if server_process:
        server_process.shutdown()
    # Don't force exit - let main() handle the output


def generate_context_intelligent(duration, transcript, frame_data):
    """Generate markdown context for CLI agent with intelligent or standard frames"""
    
    # Determine extraction mode
    has_intelligent_frames = any(frame.get('type') == 'intelligent' for frame in frame_data)
    
    context_lines = [
        "# Video Recording Context",
        "",
        "## Visual Context",
        ""
    ]
    
    for i, frame in enumerate(frame_data):
        timestamp = frame['timestamp']
        frame_path = frame['path']
        
        # Format timestamp
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        formatted_timestamp = f"{minutes:02d}:{seconds:02d}"
        
        # Get relative path and format for Gemini with @
        relative_path = os.path.relpath(frame_path, os.getcwd()).replace('\\', '/')
        
        context_lines.append(f"### Frame {i+1} - Time: {formatted_timestamp}")
        
        # Add speech context if this is an intelligent frame
        if frame.get('type') == 'intelligent' and frame.get('segment_text'):
            context_lines.append(f"**Speech Context**: \"{frame['segment_text']}\"")
            context_lines.append("")
        
        # Add image reference in Gemini format
        context_lines.append(f"@{relative_path}")
        context_lines.append("")
        context_lines.append("---")
        context_lines.append("")
    
    context_lines.extend([
        "## Audio Transcript",
        "",
        "```",
        transcript,
        "```",
        "",
        "## Instructions",
        "",
        "Please analyze the provided frame images and transcript to understand the developer's request."
    ])
    
    if has_intelligent_frames:
        context_lines.append("Each frame corresponds to a specific speech segment, showing the application state when the user mentioned different issues or requirements.")
    else:
        context_lines.append("The frames show the application state at different time intervals during the recording.")
    
    context_lines.extend([
        "Use this visual and audio context to implement the requested changes or fixes.",
        ""
    ])
    
    return '\n'.join(context_lines)


# HTML Templates
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CLI Video Recorder</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { text-align: center; }
        .timer { font-size: 2em; font-weight: bold; color: #e74c3c; margin: 20px 0; }
        .status { margin: 20px 0; padding: 15px; border-radius: 5px; }
        .status.info { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .status.error { background: #f8d7da; color: #721c24; }
        video { width: 100%; max-width: 600px; border: 2px solid #333; border-radius: 8px; margin: 20px 0; }
        .instructions { text-align: left; background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .hidden { display: none; }
        button { background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #6c757d; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎥 CLI Video Recorder</h1>
        
        <div id="instructions" class="instructions">
            <h3>Instructions:</h3>
            <ol>
                <li>Click "Start Recording" to begin</li>
                <li>Select screen/window to record (choose "Share system audio" if available)</li>
                <li>Demonstrate the issue or feature you want the CLI agent to address</li>
                <li>Speak clearly about what you want changed or fixed</li>
                <li>Recording will stop automatically after 30 seconds</li>
            </ol>
        </div>
        
        <div id="timer" class="timer hidden">00:00</div>
        
        <div id="status" class="status info">
            Ready to record. Click "Start Recording" to begin.
        </div>
        
        <video id="preview" autoplay muted class="hidden"></video>
        
        <div id="controls">
            <button id="startBtn" onclick="startRecording()">Start Recording</button>
            <button id="stopBtn" onclick="stopRecording()" disabled class="hidden">Stop Recording</button>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let recordedChunks = [];
        let stream;
        let startTime;
        let timerInterval;
        let recordingTimeout;

        const statusEl = document.getElementById('status');
        const timerEl = document.getElementById('timer');
        const previewEl = document.getElementById('preview');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const instructionsEl = document.getElementById('instructions');

        function updateStatus(message, type = 'info') {
            statusEl.textContent = message;
            statusEl.className = `status ${type}`;
        }

        function updateTimer() {
            if (startTime) {
                const elapsed = Math.floor((Date.now() - startTime) / 1000);
                const minutes = Math.floor(elapsed / 60);
                const seconds = elapsed % 60;
                timerEl.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            }
        }

        async function startRecording() {
            try {
                updateStatus('Requesting screen access...', 'info');
                
                // Request screen capture
                const displayStream = await navigator.mediaDevices.getDisplayMedia({
                    video: { cursor: 'always' },
                    audio: true  // Try to capture system audio
                });

                // Request microphone access
                let micStream = null;
                try {
                    micStream = await navigator.mediaDevices.getUserMedia({
                        audio: {
                            echoCancellation: true,
                            noiseSuppression: true,
                            autoGainControl: true
                        }
                    });
                } catch (e) {
                    console.log('Microphone access denied, using system audio only');
                }

                // Combine streams
                const videoTrack = displayStream.getVideoTracks()[0];
                const audioTracks = [];
                
                // Add system audio if available
                if (displayStream.getAudioTracks().length > 0) {
                    audioTracks.push(displayStream.getAudioTracks()[0]);
                }
                
                // Add microphone audio if available
                if (micStream && micStream.getAudioTracks().length > 0) {
                    audioTracks.push(micStream.getAudioTracks()[0]);
                }

                stream = new MediaStream([videoTrack, ...audioTracks]);
                previewEl.srcObject = stream;
                previewEl.classList.remove('hidden');

                // Setup MediaRecorder
                mediaRecorder = new MediaRecorder(stream, {
                    mimeType: 'video/webm; codecs=vp9,opus'
                });

                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };

                mediaRecorder.onstop = uploadVideo;

                // Handle user stopping via browser UI
                videoTrack.onended = stopRecording;

                // Start recording
                mediaRecorder.start();
                startTime = Date.now();
                
                // Update UI
                instructionsEl.classList.add('hidden');
                timerEl.classList.remove('hidden');
                startBtn.disabled = true;
                startBtn.classList.add('hidden');
                stopBtn.disabled = false;
                stopBtn.classList.remove('hidden');
                
                updateStatus('Recording in progress... Speak clearly about the issue or feature you want addressed.', 'info');
                
                // Start timer
                timerInterval = setInterval(updateTimer, 1000);
                updateTimer();

                // Auto-stop after 30 seconds
                recordingTimeout = setTimeout(() => {
                    if (mediaRecorder && mediaRecorder.state === 'recording') {
                        stopRecording();
                    }
                }, 30000);

            } catch (error) {
                console.error('Error starting recording:', error);
                updateStatus('Error: Could not access screen or microphone. Please allow permissions.', 'error');
            }
        }

        function stopRecording() {
            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
            
            // Clean up
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
            
            if (timerInterval) {
                clearInterval(timerInterval);
            }
            
            if (recordingTimeout) {
                clearTimeout(recordingTimeout);
            }
            
            // Update UI
            stopBtn.disabled = true;
            updateStatus('Recording stopped. Processing video...', 'info');
        }

        function uploadVideo() {
            const blob = new Blob(recordedChunks, { type: 'video/webm' });
            const formData = new FormData();
            formData.append('video', blob, 'recording.webm');

            updateStatus('Uploading and processing video...', 'info');

            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Upload successful:', data);
                updateStatus('Processing complete! You can close this window.', 'info');
                
                // Close window after a delay
                setTimeout(() => {
                    window.close();
                }, 3000);
            })
            .catch(error => {
                console.error('Upload error:', error);
                updateStatus(`Upload failed: ${error.message}`, 'error');
            });
        }

        // Auto-start if URL parameter is present
        if (new URLSearchParams(window.location.search).get('autostart') === 'true') {
            setTimeout(startRecording, 1000);
        }
    </script>
</body>
</html>
'''


# Flask Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/upload', methods=['POST'])
def upload_video():
    global session_dir
    
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = session_dir / CONFIG['UPLOAD_FOLDER'] / filename
        file.save(str(upload_path))
        
        # Process video in background
        Thread(target=process_video, args=(str(upload_path),), daemon=True).start()
        
        return jsonify({'message': 'Video uploaded successfully, processing started'})
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in upload_video: {str(e)}", file=sys.stderr)
        print(f"Full traceback: {error_details}", file=sys.stderr)
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


@app.route('/status')
def get_status():
    return jsonify({
        'processing_complete': processing_complete,
        'context': context_result
    })


def cleanup_session():
    """Clean up session directory - DISABLED FOR DEBUGGING"""
    global session_dir
    # Keep files for debugging - no cleanup
    pass


def signal_handler(signum, frame):
    """Handle termination signals"""
    print(f"\nReceived signal {signum}, cleaning up...")
    cleanup_session()
    sys.exit(0)


def start_server():
    """Start the Flask server"""
    global session_dir, server_process
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create session directory
    session_dir = create_session_directory()
    
    # Start server silently
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    from werkzeug.serving import make_server
    server_process = make_server('localhost', CONFIG['PORT'], app)
    server_process.serve_forever()


def open_browser():
    """Open browser to recording interface"""
    url = f"http://localhost:{CONFIG['PORT']}?autostart=true"
    time.sleep(1)  # Give server time to start
    webbrowser.open(url)


def main():
    """Main function to start video recording"""
    global processing_complete, context_result
    
    try:
        # Check if required modules are available
        import whisper
        import ffmpeg
        from flask import Flask
        
        # Start browser opener in background
        Thread(target=open_browser, daemon=True).start()
        
        # Start server (this will block) - completely silent
        try:
            start_server()
        except KeyboardInterrupt:
            return  # Silent exit on Ctrl+C
        except Exception as e:
            print(f"Server error: {str(e)}")
            return
        finally:
            # Wait for processing to complete
            while not processing_complete:
                time.sleep(0.1)
            
            # Output ONLY the context - no headers or decorations
            if context_result and not context_result.startswith("Error"):
                print(context_result)
            elif context_result:
                print(context_result)
            
            cleanup_session()
            
    except ImportError as e:
        print(f"Missing dependency: {str(e)}")
        print("Please run: python cli_video_ext.py install")
        return
    except Exception as e:
        print(f"Error in recording: {str(e)}")
        return


if __name__ == '__main__':
    main()