# Video Recording and Frame Extraction Workflow Summary

This document summarizes the proposed workflow for a multi-step video recording and problem-solving process, orchestrated by the Gemini CLI agent. The goal is to initiate the entire process with a single user command.

## Overall Workflow

1.  **User initiates with a single command:** The user runs a command like `\start_video_recording`.
2.  **Command 1 (`\start_video_recording`) executes:** This command handles video recording, audio extraction, and transcription.
3.  **Gemini's Intermediate Processing:** Gemini analyzes the output of Command 1 to identify key moments.
4.  **Command 2 (`\extract_frames`) executes (orchestrated by Gemini):** Gemini triggers a second command to extract frames from the video at the identified key moments.
5.  **Gemini's Final Problem Solving:** Gemini combines the textual and visual context to understand and solve the user's problem.

## Detailed Steps and Responsibilities

### Step 1: User Initiates (`\start_video_recording`)

*   **User Action:** The user types `\start_video_recording` in the Gemini CLI.
*   **`command.json` Definition:**
    ```json
    {
      "start_video_recording": {
        "description": "Starts a video recording session, captures audio, and generates a word timeline.",
        "shell_command": "python your_video_recording_script.py"
      }
    }
    ```
*   **`your_video_recording_script.py` Responsibilities:**
    *   Initiate screen recording and audio capture.
    *   Save the raw video (e.g., `recording.webm`) and audio (e.g., `audio.wav`) files.
    *   Process the audio (e.g., using Whisper) to generate `word_timeline.csv` (containing `timestamp,word` data).
    *   **Crucially, print the absolute paths of `word_timeline.csv` and `recording.webm` to standard output in a parsable format (e.g., `WORD_TIMELINE_PATH=/path/to/word_timeline.csv VIDEO_PATH=/path/to/recording.webm`). This allows Gemini to read these paths.**

### Step 2: Gemini's Intermediate Processing

*   **Gemini Action:** After `your_video_recording_script.py` completes, Gemini will:
    1.  Parse the standard output of the script to extract the absolute paths for `word_timeline.csv` and `recording.webm`.
    2.  Use the `read_file` tool to read the content of `word_timeline.csv`.
    3.  Perform "AI analysis" on `word_timeline.csv` (and potentially the full transcript) to identify critical timestamps where the user is likely pointing out problems (e.g., based on specific phrases, pauses, or changes in speech patterns).
    4.  Formulate the arguments for the next command (`\extract_frames`) using the identified timestamps and the video file path.

### Step 3: Gemini Orchestrates Command 2 (`\extract_frames`)

*   **Gemini Action:** Gemini will *automatically* execute `\extract_frames` with the determined arguments.
*   **`command.json` Definition:**
    ```json
    {
      "extract_frames": {
        "description": "Extracts frames from a video at specified timestamps.",
        "shell_command": "python your_frame_extraction_script.py {video_path} {timestamps}"
      }
    }
    ```
    (Note: `{video_path}` and `{timestamps}` are placeholders for arguments Gemini will pass.)
*   **`your_frame_extraction_script.py` Responsibilities:**
    *   Accept the video file path and a list of timestamps as command-line arguments.
    *   Use `ffmpeg` (or similar) to extract frames from the video at each specified timestamp.
    *   Save these frames as image files (e.g., `frame_3.png`, `frame_7.9.png`) in a designated location (e.g., a `frames` subdirectory).
    *   **Print the absolute paths of the generated frame image files to standard output for Gemini to read.**

### Step 4: Gemini's Final Problem Solving

*   **Gemini Action:** After `your_frame_extraction_script.py` completes, Gemini will:
    1.  Parse the standard output of the script to get the absolute paths of the extracted frame images.
    2.  Use the `read_file` tool to read the content of each extracted frame image.
    3.  Combine the textual context from `word_timeline.csv` (and full transcript) with the visual information from the extracted frames.
    4.  Utilize its multimodal capabilities to gain a comprehensive understanding of the user's problem, leveraging both spoken cues and visual context.
    5.  Proceed to analyze and implement solutions to the identified problems using its available tools (e.g., `replace`, `write_file`, `run_shell_command` for code modifications).

## Key Considerations

*   **Script Output:** It is critical that your Python scripts print the absolute paths of generated files to standard output in a consistent, parsable format for Gemini to consume.
*   **Error Handling:** Scripts should include robust error handling.
*   **File Paths:** Ensure all paths used within scripts and `command.json` are absolute or correctly handled relative to the script's execution context.

This summary should help you set up the project in the correct directory and allow me to pick up the context in a new session.
