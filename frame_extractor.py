import os
from pathlib import Path
import subprocess
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

def extract_frames(video_path, frames_dir, duration, ai_analysis=None, transcript_result=None, has_audio=True, config=None):
    """Extract frames using AI analysis or fallback methods"""
    extracted_frames = []
    frames_path = Path(frames_dir)
    
    # Use a default config if none is provided
    if config is None:
        config = {
            'MAX_FRAMES': 6,
            'MIN_FRAMES': 2,
            'SILENT_VIDEO_INTERVALS': [2, 7, 12, 17, 22]  # For videos without audio
        }

    # Method 1: AI-guided extraction (only if we have audio and transcript)
    if has_audio and ai_analysis and ai_analysis.get('suggested_frames'):
        for i, frame_suggestion in enumerate(ai_analysis['suggested_frames']):
            timestamp = float(frame_suggestion['timestamp'])
            reason = frame_suggestion.get('reason', 'AI suggested frame')
            
            # Ensure timestamp is within video bounds
            if timestamp >= duration:
                timestamp = max(0.0, duration - 1.0)
            
            frame_filename = f"frame_{i+1}_at_{timestamp:.1f}s.png"
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
                        'reason': reason,
                        'method': 'ai_guided'
                    })
            except:
                pass  # Silent failure
        
        if extracted_frames:
            return extracted_frames
    
    # Method 2: Segment-based extraction (only if we have audio and transcript)
    if has_audio and transcript_result and transcript_result.get('segments'):
        segments = transcript_result['segments']
        for i, segment in enumerate(segments):
            segment_start = float(segment['start'])
            segment_end = float(segment['end'])
            timestamp = (segment_start + segment_end) / 2.0
            
            if timestamp >= duration:
                timestamp = max(0.0, duration - 1.0)
            
            frame_filename = f"frame_{i+1}_at_{timestamp:.1f}s.png"
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
                        'reason': f"Speech segment: {segment['text'].strip()}",
                        'method': 'segment_based'
                    })
            except:
                pass  # Silent failure
        
        if extracted_frames:
            return extracted_frames
    
    # Method 3: Fixed intervals for silent videos or fallback
    if not has_audio:
        # Use fixed intervals for silent videos
        intervals = [ts for ts in config['SILENT_VIDEO_INTERVALS'] if ts < duration]
        method = 'silent_video'
        reason_prefix = 'Silent video'
    else:
        # Fallback for videos with audio but no transcript/AI analysis
        intervals = [duration * 0.2, duration * 0.5, duration * 0.8]
        method = 'fallback'
        reason_prefix = 'Fallback'
    
    if not intervals:
        intervals = [duration / 2] if duration > 1 else [0.5]
    
    for i, timestamp in enumerate(intervals):
        frame_filename = f"frame_{i+1}_at_{timestamp:.1f}s.png"
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
                    'reason': f'{reason_prefix} interval',
                    'method': method
                })
        except:
            pass  # Silent failure
    
    return extracted_frames


def extract_frames_at_timestamps(video_path, frames_dir, timestamps):
    """Extract frames at specific timestamps - Step 2 of two-step workflow"""
    extracted_frames = []
    frames_path = Path(frames_dir)
    frames_path.mkdir(exist_ok=True)
    
    for i, timestamp in enumerate(timestamps):
        timestamp = float(timestamp)
        frame_filename = f"frame_{i+1}_at_{timestamp:.1f}s.png"
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
                    'reason': f'Requested timestamp {timestamp:.1f}s',
                    'method': 'on_demand'
                })
        except Exception as e:
            # Log error but continue with other frames
            pass
    
    return extracted_frames
