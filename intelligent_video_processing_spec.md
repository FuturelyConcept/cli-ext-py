# Intelligent Video Processing Enhancement Specification

## Overview

This document outlines the enhancement of the CLI Video Extension to implement AI-guided intelligent frame extraction. The current system uses static timing intervals for frame extraction, which often results in frames that don't correspond to the actual content being discussed. This enhancement will use AI analysis to determine optimal frame extraction points based on transcript content.

## Problem Statement

### Current Issues
- **Misaligned Context**: Frames extracted at arbitrary intervals (2s, 7s, 12s, etc.) often don't match what the user is discussing
- **Poor Visual Context**: Code agents receive frames that may not show the actual problems being described
- **Inaccurate Problem Solving**: Agents make incorrect assumptions due to irrelevant visual context
- **Missed Key Moments**: Important visual states might be skipped entirely with static timing

### Example Scenario
```
User Recording: "I have three problems. First, there's a typo on the landing page [2s]. 
Second, when I click this feature button [8s], it gives a JSON error [9s]. 
Third, the logout button in the top right doesn't work [15s]."

Current System: Extracts frames at 2s, 7s, 12s, 17s
- Frame at 7s: Shows nothing relevant (between problems)
- Frame at 12s: Shows nothing relevant (between problems)  
- Misses the actual JSON error at 9s and logout button at 15s
```

## Proposed Solution

### Core Concept
Use the CLI agent itself to analyze the transcript and intelligently determine optimal frame extraction points that correspond to the actual issues being discussed.

### Key Innovation
Instead of arbitrary timing, extract frames at moments when the user is:
1. Demonstrating specific problems
2. Pointing to UI elements
3. Showing error states
4. Transitioning between different issues/topics

## Technical Requirements

### Dependencies
- **Existing**: `openai-whisper`, `ffmpeg-python`, `flask`
- **New**: Enhanced Whisper configuration for word-level timestamps
- **CLI Integration**: Ability to call Gemini CLI or Claude Code CLI from Python

### System Requirements
- Python 3.8+
- FFmpeg (for video/audio processing)
- Active CLI agent (Gemini CLI or Claude Code)
- Sufficient disk space for temporary transcript files

## Detailed Implementation Plan

### Phase 1: Enhanced Transcript Generation

#### 1.1 Upgrade Whisper Transcription
**Objective**: Generate detailed transcript with precise word-level timing

**Implementation**:
- Modify `transcribe_audio_whisper_with_segments()` function
- Enable `word_timestamps=True` in Whisper configuration
- Generate timeline visualization format as requested

**Timeline Format Output**:
```
Time axis - 0s--------1s--------2s--------3s--------4s--------5s--------6s--------7s--------8s--------9s--------10s-------11s-------12s-------13s-------14s-------15s-------16s
Text axis  - I need your help in solving three problems, [pause] I have this typo in landing page, we can fix it easily. Another one for it let me click feature button here, it gives json error, something to do with data parsing here. also here when i click on logout which you see on right top corner, it just doesnt work here.... when i click i should be logged out.
```

**Code Changes Required**:
- Update `video_recorder.py` function `transcribe_audio_whisper_with_segments()`
- Add new function `generate_timeline_visualization()`
- Create structured data output with both visual timeline and programmatic segments

#### 1.2 Enhanced Data Structure
**Create comprehensive transcript data**:
```python
transcript_data = {
    'duration': 25.3,
    'timeline_visual': "Time axis - 0s--------1s...",
    'segments': [
        {'start': 0.5, 'end': 3.2, 'text': 'I need your help in solving three problems'},
        {'start': 4.1, 'end': 7.8, 'text': 'I have this typo in landing page'},
        # ... more segments
    ],
    'word_timestamps': [...],  # Word-level timing
    'full_text': 'Complete transcript text'
}
```

### Phase 2: AI Analysis Integration

#### 2.1 CLI Agent Detection
**Objective**: Automatically detect available CLI agents and choose the appropriate one

**Implementation**:
- Check for `gemini` command availability
- Check for `claude` command availability  
- Implement fallback logic if no CLI agent available

**Code Changes**:
- Add function `detect_available_cli_agents()`
- Add configuration for CLI command formats
- Handle different response formats from different agents

#### 2.2 AI Analysis Prompt Creation
**Objective**: Create intelligent prompts for frame extraction analysis

**Prompt Template**:
```markdown
# Intelligent Frame Extraction Analysis

I have a {duration}-second screen recording with the following transcript and timeline:

## Visual Timeline
```
{timeline_visualization}
```

## Detailed Segments
{segment_breakdown}

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
{
  "reasoning": "Brief explanation of your analysis",
  "suggested_frames": [
    {"timestamp": 1.5, "reason": "User pointing out typo on landing page"},
    {"timestamp": 8.5, "reason": "Demonstrating feature button JSON error"},
    {"timestamp": 15.0, "reason": "Showing logout button that doesn't work"}
  ],
  "total_issues_identified": 3
}
```
```

#### 2.3 CLI Agent Communication
**Implementation Details**:
- Save transcript to temporary file in `.gemini/video_ext/temp/`
- Call appropriate CLI agent with transcript file
- Parse JSON response to extract frame timing suggestions
- Handle errors and timeouts gracefully

**Code Structure**:
```python
def call_ai_for_frame_analysis(transcript_file, cli_type='auto'):
    # Auto-detect CLI type if not specified
    # Create prompt file
    # Execute CLI command
    # Parse response
    # Return frame suggestions or None
```

### Phase 3: Intelligent Frame Extraction

#### 3.1 AI-Guided Frame Extraction
**Objective**: Extract frames based on AI analysis rather than static timing

**Process Flow**:
1. Receive AI suggestions with timestamps and reasons
2. Validate timestamps against video duration
3. Extract frames using FFmpeg at suggested times
4. Generate enhanced metadata for each frame

**Frame Metadata Structure**:
```python
frame_data = {
    'path': 'path/to/frame.png',
    'timestamp': 8.5,
    'type': 'ai_intelligent',
    'reason': 'User demonstrating JSON error on feature button',
    'issue_index': 2,
    'confidence': 'high'  # Based on AI analysis
}
```

#### 3.2 Fallback Logic
**Multiple Fallback Levels**:
1. **Primary**: AI-guided intelligent extraction
2. **Secondary**: Segment-based extraction (use transcript segments without AI)
3. **Tertiary**: Default static timing (2s, 7s, 12s, 17s, 22s)
4. **Final**: Single frame at video midpoint

### Phase 4: Enhanced Context Generation

#### 4.1 Rich Context Output
**Generate comprehensive markdown context including**:
- AI analysis summary
- Timeline visualization
- Frame context with reasoning
- Issue mapping

**Context Template**:
```markdown
# Enhanced Video Recording Context

**Duration**: 25.3 seconds
**Analysis Method**: AI-Guided Intelligence  
**Issues Identified**: 3

## AI Analysis Summary
**Issue 1**: Typo on landing page (Frame 1 at 00:01)
**Issue 2**: JSON error on feature button (Frame 2 at 00:08) 
**Issue 3**: Logout button not working (Frame 3 at 00:15)

## Timeline Transcript
```
Time axis - 0s--------1s--------2s...
Text axis  - I need your help in solving three problems...
```

## Visual Context

### Frame 1 - Time: 00:01
**Context**: User pointing out typo on landing page
**Issue**: Landing page content error
@.gemini/video_ext/session_123/frames/intelligent_1_at_1.5s.png

### Frame 2 - Time: 00:08  
**Context**: Demonstrating feature button JSON error
**Issue**: Feature button functionality
@.gemini/video_ext/session_123/frames/intelligent_2_at_8.5s.png

### Frame 3 - Time: 00:15
**Context**: Showing logout button that doesn't work  
**Issue**: Authentication/logout functionality
@.gemini/video_ext/session_123/frames/intelligent_3_at_15.0s.png

## Instructions

This video context was generated using AI-guided intelligent frame extraction.
Each frame corresponds to a specific issue the user identified:

1. **Landing Page Typo**: Visual context shows the exact location of the text error
2. **Feature Button Error**: Frame captures the moment before/during the JSON error  
3. **Logout Issue**: Shows the logout button location and state

Please analyze each frame in the context of its corresponding issue and provide comprehensive solutions.
```

## File Structure Changes

### New Files
```
cli-ext-py/
├── intelligent_processor.py      # New: AI-guided processing logic
├── transcript_analyzer.py        # New: Timeline generation and analysis
├── cli_integration.py            # New: CLI agent communication
├── enhanced_context.py           # New: Rich context generation
└── config/
    └── prompts/
        └── frame_analysis.md      # New: AI analysis prompt templates
```

### Modified Files
```
cli-ext-py/
├── video_recorder.py            # Modified: Integrate intelligent processing
├── cli_video_ext.py             # Modified: Add intelligent mode option
└── README.md                    # Modified: Document new features
```

## Configuration Options

### New Configuration Parameters
```python
INTELLIGENT_CONFIG = {
    'enable_ai_analysis': True,          # Toggle intelligent mode
    'cli_agent_preference': 'auto',      # 'gemini', 'claude', 'auto'
    'max_frames': 6,                     # Maximum frames to extract
    'min_frames': 2,                     # Minimum frames to extract
    'analysis_timeout': 30,              # Seconds to wait for AI analysis
    'fallback_on_failure': True,        # Use default timing if AI fails
    'word_timestamps': True,             # Enable word-level timing
    'timeline_visualization': True,      # Generate visual timeline
    'enhanced_context': True            # Generate rich markdown context
}
```

## Testing Strategy

### Test Cases

#### 1. Single Issue Recording
- **Input**: 10-second video with one problem
- **Expected**: 1-2 frames focused on the specific issue
- **Validation**: Frame timing aligns with problem description

#### 2. Multiple Issues Recording  
- **Input**: 30-second video with 3 distinct problems
- **Expected**: 3-4 frames, one per issue plus overview
- **Validation**: Each frame corresponds to different issue mentioned

#### 3. No Audio Recording
- **Input**: Video without audio track
- **Expected**: Fallback to default static timing
- **Validation**: Standard frames at 2s, 7s, 12s intervals

#### 4. CLI Agent Unavailable
- **Input**: System without Gemini/Claude CLI
- **Expected**: Graceful fallback to segment-based extraction
- **Validation**: Functional frame extraction without AI analysis

#### 5. Complex Workflow Recording
- **Input**: Long recording with multiple screens/applications
- **Expected**: Frames at transition points and key moments
- **Validation**: Visual context matches spoken workflow steps

### Performance Benchmarks
- **AI Analysis Time**: < 30 seconds for 30-second video
- **Total Processing Time**: < 2 minutes for 30-second video  
- **Frame Accuracy**: > 80% relevance to spoken content
- **Fallback Reliability**: 100% success rate when AI unavailable

## Implementation Timeline

### Week 1: Core Infrastructure
- [ ] Implement enhanced Whisper transcription with word timestamps
- [ ] Create timeline visualization generator
- [ ] Build transcript data structures

### Week 2: AI Integration
- [ ] Implement CLI agent detection and communication
- [ ] Create AI analysis prompt system
- [ ] Build response parsing and validation

### Week 3: Intelligent Processing
- [ ] Implement AI-guided frame extraction
- [ ] Create comprehensive fallback logic
- [ ] Build enhanced context generation

### Week 4: Testing and Refinement
- [ ] Comprehensive testing across all scenarios
- [ ] Performance optimization
- [ ] Documentation and user guide updates

## Success Metrics

### Primary Metrics
- **Frame Relevance**: 80%+ of frames show content related to spoken issues
- **Issue Coverage**: 95%+ of mentioned problems have corresponding visual context
- **Processing Reliability**: 98%+ successful completion rate

### Secondary Metrics  
- **User Satisfaction**: Improved debugging accuracy reported by users
- **Agent Effectiveness**: Better problem resolution from CLI agents
- **Performance**: Processing time under 2 minutes for typical recordings

## Risk Mitigation

### Potential Risks and Solutions

#### 1. AI Analysis Failure
- **Risk**: CLI agent unavailable or returns invalid response
- **Mitigation**: Multiple fallback levels, robust error handling

#### 2. Performance Issues
- **Risk**: AI analysis adds significant processing time
- **Mitigation**: Timeout controls, parallel processing where possible

#### 3. Accuracy Problems
- **Risk**: AI suggests irrelevant frame timings
- **Mitigation**: Validation logic, user feedback mechanism

#### 4. Compatibility Issues
- **Risk**: Different CLI agents return different response formats
- **Mitigation**: Standardized parsing, agent-specific handlers

## Future Enhancements

### Phase 2 Features (Post-Implementation)
- **Visual Change Detection**: Combine AI analysis with frame diff analysis
- **Multi-Language Support**: Enhanced support for non-English recordings
- **Custom Prompt Templates**: User-configurable analysis prompts
- **Learning System**: Improve frame selection based on user feedback
- **Integration APIs**: Direct integration with popular development tools

## Conclusion

This enhancement transforms the CLI Video Extension from a basic screen recorder with arbitrary frame extraction into an intelligent system that provides contextually relevant visual information to AI agents. By leveraging the AI agent's own analytical capabilities, we create a feedback loop that significantly improves the quality of context provided for debugging and development assistance.

The implementation maintains backward compatibility while providing substantial improvements in accuracy and usefulness, making it a valuable tool for developers working with AI-powered CLI agents.

---

**Next Steps**: Use this specification with Claude Code CLI to implement the intelligent video processing enhancement:

```bash
claude code @intelligent_video_processing_spec.md "Implement the intelligent video processing enhancement as specified in this document. Start with Phase 1 and integrate the changes into the existing video_recorder.py codebase."
```