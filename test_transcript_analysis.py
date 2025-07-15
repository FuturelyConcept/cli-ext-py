#!/usr/bin/env python3
"""
Test the transcript analysis with an existing video file
Shows word timeline and speech analysis without running full extension
"""

import os
import sys
from pathlib import Path
import subprocess

def extract_audio_simple(video_path):
    """Extract audio from video for testing"""
    video_file = Path(video_path)
    audio_path = video_file.parent / "test_transcript_audio.wav"
    
    # Find FFmpeg
    ffmpeg_locations = [
        'ffmpeg',
        Path(__file__).parent / 'bin' / 'ffmpeg.exe',
        Path("C:/Users/Deepika_Akshaj/.gemini/extensions/video-recording/bin/ffmpeg.exe")
    ]
    
    ffmpeg_exe = None
    for location in ffmpeg_locations:
        try:
            if location == 'ffmpeg':
                result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    ffmpeg_exe = 'ffmpeg'
                    break
            elif Path(location).exists():
                result = subprocess.run([str(location), '-version'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    ffmpeg_exe = str(location)
                    break
        except:
            continue
    
    if not ffmpeg_exe:
        print("❌ No working FFmpeg found")
        return None
    
    try:
        cmd = [
            ffmpeg_exe, '-i', str(video_path),
            '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1',
            '-y', str(audio_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and audio_path.exists() and audio_path.stat().st_size > 1000:
            return str(audio_path)
        
    except Exception as e:
        print(f"❌ Audio extraction failed: {e}")
    
    return None

def transcribe_with_whisper(audio_path):
    """Transcribe audio using Whisper"""
    try:
        import whisper
        print("📝 Loading Whisper model...")
        
        import warnings
        import os
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            os.environ['CUDA_VISIBLE_DEVICES'] = ''
            model = whisper.load_model('base')
            result = model.transcribe(audio_path, word_timestamps=True, verbose=False)
        
        return result
    except Exception as e:
        print(f"❌ Whisper transcription failed: {e}")
        return None

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
                'score': score,
                'keywords': found_keywords
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
            'context': seg['text'],
            'score': seg['score'],
            'keywords': seg['keywords']
        })
    
    return suggested_frames

def test_transcript_analysis(video_path):
    """Test transcript analysis on the video"""
    print("🎬 Testing Transcript Analysis")
    print("=" * 60)
    print(f"Video: {video_path}")
    
    if not os.path.exists(video_path):
        print("❌ Video file not found")
        return
    
    # Step 1: Extract audio
    print("\n🔊 Extracting audio...")
    audio_path = extract_audio_simple(video_path)
    if not audio_path:
        print("❌ Failed to extract audio")
        return
    
    print(f"✅ Audio extracted: {audio_path}")
    
    # Step 2: Transcribe
    print("\n📝 Transcribing with Whisper...")
    transcript_result = transcribe_with_whisper(audio_path)
    if not transcript_result:
        print("❌ Failed to transcribe")
        return
    
    print("✅ Transcription completed")
    
    # Get video duration (approximate from transcript)
    duration = 20  # Default
    if transcript_result.get('segments'):
        max_end = max(seg['end'] for seg in transcript_result['segments'])
        duration = max_end
    
    print(f"📊 Video duration: {duration:.1f}s")
    
    # Step 3: Create word timeline
    print("\n" + "=" * 60)
    print("📋 WORD TIMELINE")
    print("=" * 60)
    
    word_timeline = create_word_timeline_table(transcript_result)
    if word_timeline:
        print("| Time | Word |")
        print("|------|------|")
        
        for i, entry in enumerate(word_timeline):
            time_str = f"{entry['time']:.1f}s"
            print(f"| {time_str:>6} | {entry['word']} |")
            
            # Limit output for readability
            if i >= 40:
                print("| ... | (more words) |")
                break
    else:
        print("No word timeline available")
    
    # Step 4: Speech analysis
    print("\n" + "=" * 60)
    print("🎯 SPEECH ANALYSIS")
    print("=" * 60)
    
    speech_analysis = analyze_speech_for_frame_requests(transcript_result, duration)
    if speech_analysis:
        print("Key moments identified:")
        print()
        
        for i, moment in enumerate(speech_analysis):
            time_str = f"{moment['timestamp']:.1f}s"
            print(f"🎯 Frame {i+1} - {time_str}")
            print(f"   Score: {moment['score']}")
            print(f"   Keywords: {', '.join(moment['keywords'])}")
            print(f"   Text: {moment['context']}")
            print()
    else:
        print("No key moments identified")
    
    # Step 5: Complete transcript
    print("\n" + "=" * 60)
    print("📄 COMPLETE TRANSCRIPT")
    print("=" * 60)
    
    if transcript_result.get('segments'):
        for segment in transcript_result['segments']:
            start_time = segment['start']
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            text = segment['text'].strip()
            print(f"{timestamp} {text}")
    else:
        print("No transcript segments available")
    
    # Cleanup
    try:
        os.remove(audio_path)
        print(f"\n🧹 Cleaned up: {audio_path}")
    except:
        pass

def main():
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = r"C:\Users\Deepika_Akshaj\manoj\play\.gemini\video_ext\video_session_20250715_210000\uploads\recording.webm"
    
    test_transcript_analysis(video_path)

if __name__ == "__main__":
    main()