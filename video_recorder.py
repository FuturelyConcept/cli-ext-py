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

from frame_extractor import extract_frames, get_ffmpeg_path, get_ffprobe_path

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
    'MAX_RECORDING_DURATION': 30,
    'PORT': 8765,
    'UPLOAD_FOLDER': 'uploads',
    'FRAMES_FOLDER': 'frames',
    'WHISPER_MODEL': 'base',
    'MAX_FRAMES': 6,
    'MIN_FRAMES': 2,
    'AI_ANALYSIS_TIMEOUT': 30,
    'SILENT_VIDEO_INTERVALS': [2, 7, 12, 17, 22]  # For videos without audio
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
    
    # Create the session directory in current working directory
    current_dir = Path.cwd()
    session_path = current_dir / '.gemini' / 'video_ext' / session_id
    
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


# Frame extraction function is now imported from frame_extractor.py


def extract_audio(video_path, audio_path):
    """Extract audio from video for transcription"""
    try:
        # First check if video file exists and has content
        video_file = Path(video_path)
        if not video_file.exists() or video_file.stat().st_size < 1000:
            return False
        
        # Use ffmpeg-python to extract audio
        (
            ffmpeg
            .input(str(video_path))
            .output(str(audio_path), acodec='pcm_s16le', ar=16000, ac=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True, cmd=ffmpeg_path)
        )
        
        # Verify the audio file was created and has content
        audio_file = Path(audio_path)
        if audio_file.exists() and audio_file.stat().st_size > 1000:
            return True
        else:
            return False
            
    except Exception as e:
        # Try fallback method with direct subprocess
        try:
            import subprocess
            cmd = [
                ffmpeg_path, '-i', str(video_path),
                '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
                '-y', str(audio_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Check if output file exists and has content
            audio_file = Path(audio_path)
            return audio_file.exists() and audio_file.stat().st_size > 1000
            
        except Exception:
            return False


def create_word_timeline_table(transcript_result):
    """Create a clean word-level timeline table"""
    if not transcript_result or not transcript_result.get('segments'):
        return None
    
    timeline_entries = []
    
    for segment in transcript_result['segments']:
        words = segment.get('words', [])
        if words:
            # Use word-level timestamps
            for word_data in words:
                start_time = word_data.get('start', segment['start'])
                word = word_data.get('word', '').strip()
                if word:
                    timeline_entries.append({
                        'time': start_time,
                        'word': word
                    })
        else:
            # Fallback to segment level
            timeline_entries.append({
                'time': segment['start'],
                'word': segment['text'].strip()
            })
    
    # Sort by time
    timeline_entries.sort(key=lambda x: x['time'])
    
    return timeline_entries

def analyze_speech_for_frame_requests(transcript_result, duration):
    """Analyze speech to identify key moments for frame extraction"""
    if not transcript_result or not transcript_result.get('segments'):
        return []
    
    # Keywords that indicate important moments
    important_keywords = [
        'problem', 'issue', 'error', 'bug', 'broken', 'wrong', 'fix', 'help',
        'first', 'second', 'third', 'next', 'then', 'also', 'here', 'this',
        'show', 'see', 'look', 'example', 'case', 'situation'
    ]
    
    # Phrases that indicate transitions or new topics
    transition_phrases = [
        'now this', 'this one', 'and this', 'here is', 'look at this',
        'the next', 'another', 'also this', 'finally', 'lastly'
    ]
    
    suggested_frames = []
    processed_segments = []
    
    for segment in transcript_result['segments']:
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].lower().strip()
        
        # Calculate score based on keywords
        score = 0
        found_keywords = []
        
        for keyword in important_keywords:
            if keyword in text:
                score += 2
                found_keywords.append(keyword)
        
        for phrase in transition_phrases:
            if phrase in text:
                score += 3
                found_keywords.append(phrase)
        
        # Also look for numbered items (first, second, third, etc.)
        if any(num in text for num in ['first', 'second', 'third', 'fourth', 'fifth']):
            score += 4
        
        if score > 0:
            # Use middle of segment for frame extraction
            frame_time = (start_time + end_time) / 2
            
            # Ensure we don't go beyond video duration
            if frame_time >= duration:
                frame_time = max(0, duration - 1)
            
            processed_segments.append({
                'timestamp': frame_time,
                'reason': f"Speech analysis: {', '.join(found_keywords[:3])}",
                'text': segment['text'].strip(),
                'score': score
            })
    
    # Sort by score (highest first) and take top segments
    processed_segments.sort(key=lambda x: x['score'], reverse=True)
    
    # Take top 5 segments or all if less than 5
    top_segments = processed_segments[:5]
    
    # If we have segments, create frame requests
    for i, seg in enumerate(top_segments):
        suggested_frames.append({
            'timestamp': seg['timestamp'],
            'reason': f"Key moment {i+1}: {seg['text'][:50]}...",
            'context': seg['text']
        })
    
    return suggested_frames


def transcribe_audio_whisper_with_segments(audio_path):
    """Transcribe audio using OpenAI Whisper with word-level timestamps"""
    try:
        audio_file = Path(audio_path)
        if not audio_file.exists() or audio_file.stat().st_size == 0:
            return "[No audio detected]", None
        
        # Check if audio file has content
        if audio_file.stat().st_size < 1000:  # Less than 1KB likely means no audio
            return "[No audio detected]", None
        
        # Load and transcribe with word timestamps (suppress warnings and progress)
        import warnings
        import os
        import contextlib
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Suppress CUDA warnings
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            # Suppress progress bars and other output
            with contextlib.redirect_stderr(open(os.devnull, 'w')):
                model = whisper.load_model(CONFIG['WHISPER_MODEL'])
                result = model.transcribe(str(audio_path), word_timestamps=True, verbose=False)
        
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
    
    except Exception as e:
        return f"[Transcription error: {str(e)}]", None


def detect_available_cli_agents():
    """Detect available CLI agents (Gemini, Claude, etc.)"""
    agents = {}
    
    # Check for Gemini CLI
    try:
        result = subprocess.run(['gemini', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            agents['gemini'] = {
                'command': 'gemini',
                'available': True,
                'version': result.stdout.strip()
            }
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        agents['gemini'] = {'available': False}
    
    # Check for Claude CLI
    try:
        result = subprocess.run(['claude', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            agents['claude'] = {
                'command': 'claude',
                'available': True,
                'version': result.stdout.strip()
            }
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        agents['claude'] = {'available': False}
    
    return agents


def create_ai_analysis_prompt(transcript_data, timeline_viz, duration):
    """Create AI analysis prompt for intelligent frame extraction"""
    if not transcript_data or not transcript_data.get('segments'):
        return None
    
    # Build detailed segments breakdown
    segments_breakdown = []
    for i, segment in enumerate(transcript_data['segments']):
        start_time = segment['start']
        end_time = segment['end']
        text = segment['text'].strip()
        segments_breakdown.append(f"Segment {i+1}: {start_time:.1f}s - {end_time:.1f}s: \"{text}\"")
    
    prompt = f"""# Intelligent Frame Extraction Analysis

I have a {duration:.1f}-second screen recording with the following transcript and timeline:

## Visual Timeline
```
{timeline_viz['full_timeline'] if timeline_viz else 'Timeline visualization not available'}
```

## Detailed Segments
{chr(10).join(segments_breakdown)}

**Task**: Analyze this transcript to identify optimal frame extraction points that would best represent the distinct issues, features, or topics the user is discussing.

**Guidelines**:
1. Identify distinct problems/topics/segments in the user's speech
2. For each segment, suggest a timestamp (in seconds) that would capture the most relevant visual context
3. Aim for 3-6 frames total, focusing on moments when the user is:
   - Pointing out specific issues
   - Demonstrating features or problems  
   - Showing different screens/sections
   - Beginning to discuss new topics

**Response Format**:
Please respond with ONLY a JSON object in this exact format:
```json
{{
  "reasoning": "Brief explanation of your analysis",
  "suggested_frames": [
    {{"timestamp": 1.5, "reason": "User pointing out specific issue"}},
    {{"timestamp": 8.5, "reason": "Demonstrating feature problem"}},
    {{"timestamp": 15.0, "reason": "Showing different section"}}
  ],
  "total_issues_identified": 3
}}
```"""
    
    return prompt


def call_ai_for_frame_analysis(transcript_data, timeline_viz, duration, cli_agents):
    """Call available CLI agent for frame analysis"""
    
    prompt = create_ai_analysis_prompt(transcript_data, timeline_viz, duration)
    if not prompt:
        return None
    
    # Try Claude first, then Gemini
    for agent_name in ['claude', 'gemini']:
        if agent_name in cli_agents and cli_agents[agent_name].get('available'):
            try:
                # Create temporary prompt file
                temp_dir = session_dir / 'temp'
                temp_dir.mkdir(exist_ok=True)
                
                prompt_file = temp_dir / 'frame_analysis_prompt.md'
                with open(prompt_file, 'w', encoding='utf-8') as f:
                    f.write(prompt)
                
                # Call the CLI agent
                if agent_name == 'claude':
                    cmd = ['claude', 'code', f'@{prompt_file}']
                else:  # gemini
                    cmd = ['gemini', f'@{prompt_file}']
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=CONFIG['AI_ANALYSIS_TIMEOUT'])
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse JSON response
                    try:
                        response_text = result.stdout.strip()
                        
                        # Extract JSON from response
                        json_start = response_text.find('{')
                        json_end = response_text.rfind('}') + 1
                        
                        if json_start != -1 and json_end != -1:
                            json_str = response_text[json_start:json_end]
                            analysis_result = json.loads(json_str)
                            
                            # Validate and limit frame count
                            if 'suggested_frames' in analysis_result and isinstance(analysis_result['suggested_frames'], list):
                                frames = analysis_result['suggested_frames']
                                
                                # Limit frame count
                                if len(frames) > CONFIG['MAX_FRAMES']:
                                    frames = frames[:CONFIG['MAX_FRAMES']]
                                    analysis_result['suggested_frames'] = frames
                                
                                # Ensure minimum frames
                                if len(frames) >= CONFIG['MIN_FRAMES']:
                                    return analysis_result
                    
                    except json.JSONDecodeError:
                        pass  # Try next agent
                
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                pass  # Try next agent
    
    return None


def process_video(video_path):
    """Process uploaded video: transcribe audio, generate word timeline CSV only"""
    global context_result, processing_complete, server_process
    
    try:
        # Get video duration
        duration = get_video_duration(video_path)
        
        # Extract and transcribe audio
        audio_path = session_dir / 'audio.wav'
        transcript_result = None
        transcript_text = "[No audio detected]"
        has_audio = False
        
        if extract_audio(video_path, audio_path):
            if audio_path.exists() and audio_path.stat().st_size > 0:
                # We have audio, try to transcribe it
                has_audio = True
                transcript_text, transcript_result = transcribe_audio_whisper_with_segments(audio_path)
            else:
                transcript_text = "[Audio extraction failed]"
        else:
            transcript_text = "[No audio track in video]"
        
        # Generate word timeline CSV (Step 1 of two-step workflow)
        csv_file = None
        if has_audio and transcript_result:
            word_timeline = create_word_timeline_table(transcript_result)
            if word_timeline:
                csv_content = "timestamp,word\n"  # Add header
                for entry in word_timeline:
                    csv_content += f"{entry['time']:.1f},{entry['word']}\n"
                
                csv_file = session_dir / "word_timeline.csv"
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
        
        # Generate minimal context with only CSV reference
        context = generate_minimal_context(duration, transcript_text, csv_file, has_audio)
        
        context_result = context
        processing_complete = True
        
        # Shutdown server after processing
        if server_process:
            server_process.shutdown()
        
        return context
        
    except Exception as e:
        error_msg = "Error in recording, please try again"
        context_result = error_msg
        processing_complete = True
        
        # Shutdown server even on error
        if server_process:
            server_process.shutdown()
        
        return error_msg





def generate_minimal_context(duration, transcript, csv_file, has_audio):
    """Generate minimal context for CLI agent - Step 1 of two-step workflow"""
    
    # Build simple output with only CSV reference
    output = ""
    
    if csv_file and csv_file.exists():
        csv_path = os.path.relpath(csv_file, os.getcwd()).replace('\\', '/')
        output = f"@{csv_path}"
    
    return output


def generate_context(duration, transcript, frame_data, timeline_viz=None, ai_analysis=None, has_audio=True, transcript_result=None):
    """Generate full context for CLI agent - Step 2 of two-step workflow"""
    
    # Save word timeline as simple CSV file
    csv_file = None
    if has_audio and transcript_result:
        word_timeline = create_word_timeline_table(transcript_result)
        if word_timeline:
            csv_content = "timestamp,word\n"  # Add header
            for entry in word_timeline:
                csv_content += f"{entry['time']:.1f},{entry['word']}\n"
            
            global session_dir
            if session_dir:
                csv_file = session_dir / "word_timeline.csv"
                with open(csv_file, 'w', encoding='utf-8') as f:
                    f.write(csv_content)
    
    # Build simple output
    output = f"Duration {duration:.1f}s\n"
    
    if csv_file:
        csv_path = os.path.relpath(csv_file, os.getcwd()).replace('\\', '/')
        output += f"Timeline @{csv_path}\n"
    
    if transcript and transcript != "[No audio detected]" and transcript != "[No speech detected]":
        output += f"Transcript\n{transcript}\n"
    
    output += "Frames\n"
    for frame in frame_data:
        frame_path = os.path.relpath(frame['path'], os.getcwd()).replace('\\', '/')
        output += f"@{frame_path}\n"
    
    return output


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
        return jsonify({'error': 'Upload failed'}), 500


@app.route('/status')
def get_status():
    return jsonify({
        'processing_complete': processing_complete,
        'context': context_result
    })


def cleanup_session():
    """Clean up session directory"""
    global session_dir
    if session_dir and session_dir.exists():
        try:
            shutil.rmtree(session_dir)
        except Exception:
            pass  # Silent cleanup


def signal_handler(signum, frame):
    """Handle termination signals"""
    cleanup_session()
    sys.exit(0)


def start_server():
    """Start the Flask server"""
    global session_dir, server_process
    
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
    """Open browser to recording interface with retry mechanism"""
    import requests
    url = f"http://localhost:{CONFIG['PORT']}?autostart=true"
    max_retries = 10
    retry_delay = 1  # seconds

    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                webbrowser.open(url)
                return
        except requests.exceptions.ConnectionError:
            pass  # Server not ready yet
        except Exception:
            pass  # Other error, continue trying
        time.sleep(retry_delay)


def main():
    """Main function to start video recording"""
    global processing_complete, context_result
    
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Check if required modules are available
        import whisper
        import ffmpeg
        from flask import Flask
        
        # Start browser opener in background
        Thread(target=open_browser, daemon=True).start()
        
        # Start server in a separate thread
        server_thread = Thread(target=start_server, daemon=True)
        server_thread.start()

        # Wait for processing to complete
        while not processing_complete:
            time.sleep(0.1)
        
        # Output the CSV path directly
        if context_result and context_result != "Error in recording, please try again":
            print(context_result)
        else:
            print("Recording failed")
        
        # Don't cleanup immediately - let user see the files
        # cleanup_session()
            
    except ImportError as e:
        print("Missing dependency. Please install required packages.")
        sys.exit(1)
    except Exception as e:
        print("Video recording failed. Please try again.")
        sys.exit(1)
    finally:
        if server_process:
            server_process.shutdown()


if __name__ == '__main__':
    main()