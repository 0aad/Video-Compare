# Video-Compare
## 📁 Code Structure

The project is structured into modular Python scripts, each responsible for a core function in the video comparison pipeline. Here's a breakdown of the main components:

```
Video-Compare/
├── extract_frames.py              # Extracts frames from original and recorded videos at a fixed frame rate
├── detect_keyframes.py           # Identifies keyframes based on histogram differences across sequential frames
├── match_features.py             # Performs keyframe matching between original and recorded video frames
├── manual_calibration.py         # Allows manual trimming of frames to align starting and ending points
├── process_frames.py             # Conducts segment-based comparison between matched frame intervals
├── FrameComparisonVisualizer.py  # Generates visual reports (plots and HTML tables) for similarity analysis
├── frames/                       # Directory to hold extracted frames from both video sources
│   ├── original_frames/          # Extracted frames from the original video
│   └── recorded_frames/          # Extracted frames from the recorded playback
├── output/                       # Stores CSV results, HTML reports, plots, and editable match files
└── keyframes.json                # Contains metadata for detected keyframes in both videos
```


