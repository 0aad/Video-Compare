import cv2
import numpy as np
import os
import json


def detect_keyframes(frames_folder, threshold=0.6):
    keyframes = []
    last_hist = None

    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.png')])
    print(f"Starting keyframe detection in {frames_folder}. Total frames: {len(frame_files)}")

    for frame_index, frame_file in enumerate(frame_files):
        frame_path = os.path.join(frames_folder, frame_file)
        frame = cv2.imread(frame_path)

        hist = cv2.calcHist([frame], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()

        if last_hist is not None:
            score = cv2.compareHist(hist, last_hist, cv2.HISTCMP_CORREL)
            print(f"Frame {frame_index}: Similarity score = {score:.4f}")
            if score < threshold:
                keyframes.append(frame_file)
                print(f"Keyframe detected at frame {frame_index} with score {score:.4f}")

        last_hist = hist

    print(f"Keyframe detection completed in {frames_folder}. Total keyframes detected: {len(keyframes)}")
    return keyframes


if __name__ == "__main__":
    original_frames_dir = 'frames/original_frames'
    recorded_frames_dir = 'frames/recorded_frames'

    original_keyframes = detect_keyframes(original_frames_dir)
    recorded_keyframes = detect_keyframes(recorded_frames_dir)

    print("Original video keyframes:", original_keyframes)
    print("Recorded video keyframes:", recorded_keyframes)

    # 统计关键帧数量
    original_keyframe_count = len(original_keyframes)
    recorded_keyframe_count = len(recorded_keyframes)

    print(f"Original video keyframe count: {original_keyframe_count}")
    print(f"Recorded video keyframe count: {recorded_keyframe_count}")

    # 将两个视频的关键帧信息保存在同一个文件中
    keyframes_info = {
        "original_keyframes": original_keyframes,
        "recorded_keyframes": recorded_keyframes,
        "original_keyframe_count": original_keyframe_count,
        "recorded_keyframe_count": recorded_keyframe_count
    }

    with open('keyframes.json', 'w') as f:
        json.dump(keyframes_info, f, indent=4)
