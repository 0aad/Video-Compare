import os
import csv
import cv2
import numpy as np
from concurrent.futures import ProcessPoolExecutor


def calculate_similarity_score(img1, img2):
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    hist1 = cv2.calcHist([img1_gray], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([img2_gray], [0], None, [256], [0, 256])

    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return score


def extract_frame_number(frame_filename):
    return int(frame_filename.split('_')[1].split('.')[0])


def read_editable_matches(filename):
    matches = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row[1]:
                matches.append((row[0], row[1]))
    return matches


def find_frames_to_compare(original_frame, recorded_frame_range, recorded_frame_index, ratio):
    frames_to_compare = []
    range_extent = 3  # 前后3帧范围

    for offset in range(-range_extent, range_extent + 1):
        compare_index = recorded_frame_index + offset
        if 0 <= compare_index < len(recorded_frame_range):
            frames_to_compare.append(recorded_frame_range[compare_index])

    return original_frame, frames_to_compare


def process_frame_group(original_frames_dir, recorded_frames_dir, original_frame, recorded_frame_range, ratio):
    best_score = -1
    best_match = None
    accumulated_error = 0.0

    original_img_path = os.path.join(original_frames_dir, original_frame)
    original_img = cv2.imread(original_img_path)
    if original_img is None:
        return original_frame, None, best_score, 1.0

    for recorded_frame in recorded_frame_range:
        recorded_img_path = os.path.join(recorded_frames_dir, recorded_frame)
        recorded_img = cv2.imread(recorded_img_path)
        if recorded_img is None:
            continue

        score = calculate_similarity_score(original_img, recorded_img)
        if score > best_score:
            best_score = score
            best_match = recorded_frame

    difference = 1.0 - best_score
    return original_frame, best_match, best_score, difference


def process_frames(original_frames_dir, recorded_frames_dir, matches, output_csv):
    results = []

    # 按每两对关键帧为一组进行处理
    for k in range(len(matches) - 1):
        start_frame, next_start_frame = matches[k], matches[k + 1]
        start_frame_number = extract_frame_number(start_frame[0])
        next_start_frame_number = extract_frame_number(next_start_frame[0])
        recorded_start_frame_number = extract_frame_number(start_frame[1])
        next_recorded_start_frame_number = extract_frame_number(next_start_frame[1])

        print(
            f"Processing frames from {start_frame_number} to {next_start_frame_number} with recorded frames from {recorded_start_frame_number} to {next_recorded_start_frame_number}")

        original_frame_range = [f"frame_{i:06d}.png" for i in range(start_frame_number, next_start_frame_number + 1)]
        recorded_frame_range = [f"frame_{i:06d}.png" for i in range(recorded_start_frame_number, next_recorded_start_frame_number + 1)]

        # 计算帧数比例
        original_frame_count = next_start_frame_number - start_frame_number + 1
        recorded_frame_count = next_recorded_start_frame_number - recorded_start_frame_number + 1
        ratio = 1 - (recorded_frame_count / original_frame_count)
        print(f"Ratio for this group: {ratio}")

        # 使用多进程池来并行处理每组帧对
        frame_tasks = []
        with ProcessPoolExecutor() as executor:
            for original_frame in original_frame_range:
                frame_tasks.append(
                    executor.submit(process_frame_group, original_frames_dir, recorded_frames_dir, original_frame,
                                    recorded_frame_range, ratio))
            for future in frame_tasks:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f"Generated an exception: {exc}")

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Original Frame", "Matched Frame", "Similarity Score", "Difference to 1.0"])
        for result in results:
            writer.writerow(result)

    return results


if __name__ == "__main__":
    original_frames_dir = 'frames/original_frames'
    recorded_frames_dir = 'frames/recorded_frames'
    editable_matches_file = 'output/editable_matches.csv'
    output_csv = 'output/compare_results.csv'

    matches = read_editable_matches(editable_matches_file)
    results = process_frames(original_frames_dir, recorded_frames_dir, matches, output_csv)
