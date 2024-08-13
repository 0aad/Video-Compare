import cv2
import os
import json
import csv
import matplotlib.pyplot as plt

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

def find_best_match_for_keyframes(original_keyframes, original_frames_dir, recorded_keyframes, recorded_frames_dir, threshold=0.9, range_value=200):
    best_matches = []

    for i, original_frame_file in enumerate(original_keyframes):
        original_frame_path = os.path.join(original_frames_dir, original_frame_file)
        original_frame = cv2.imread(original_frame_path)
        if original_frame is None:
            continue

        best_match_files = []
        best_match_score = -1
        best_match_index = -1

        original_frame_number = extract_frame_number(original_frame_file)

        for j, recorded_frame_file in enumerate(recorded_keyframes):
            recorded_frame_number = extract_frame_number(recorded_frame_file)
            if abs(recorded_frame_number - original_frame_number) > range_value:
                continue  # 只在设定范围内进行对比

            recorded_frame_path = os.path.join(recorded_frames_dir, recorded_frame_file)
            recorded_frame = cv2.imread(recorded_frame_path)
            if recorded_frame is None:
                continue

            score = calculate_similarity_score(original_frame, recorded_frame)
            print(f"Similarity score between {original_frame_file} and {recorded_frame_file}: {score:.4f}")

            if score > best_match_score:
                best_match_score = score
                best_match_files = [recorded_frame_file]
                best_match_index = j
            elif score == best_match_score:
                best_match_files.append(recorded_frame_file)

        if best_match_score < threshold:
            best_matches.append((original_frame_file, None, best_match_score, "N/A"))
        else:
            best_match_frame_number = extract_frame_number(recorded_keyframes[best_match_index])
            frame_diff = best_match_frame_number - original_frame_number
            best_matches.append((original_frame_file, best_match_files, best_match_score, frame_diff))

    return best_matches

def save_matches_to_csv(matches, csv_filename):
    os.makedirs(os.path.dirname(csv_filename), exist_ok=True)
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Original Frame", "Matched Frame(s)", "Similarity Score", "Frame Difference"])
        for original_frame, recorded_frames, match_score, frame_diff in matches:
            if recorded_frames is None:
                writer.writerow([original_frame, "None", match_score, frame_diff])
            else:
                writer.writerow([original_frame, "; ".join(recorded_frames), match_score, frame_diff])

def save_editable_matches(matches, editable_filename):
    os.makedirs(os.path.dirname(editable_filename), exist_ok=True)
    with open(editable_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Original Frame", "Matched Frame"])
        for original_frame, recorded_frames, _, _ in matches:
            if recorded_frames is None:
                writer.writerow([original_frame, ""])
            else:
                writer.writerow([original_frame, recorded_frames[0]])

def plot_frame_differences(matches, plot_filename):
    frame_differences = [match[3] for match in matches if isinstance(match[3], int)]

    plt.figure(figsize=(10, 6))
    plt.bar(range(len(frame_differences)), frame_differences, color='skyblue')
    plt.ylabel('Frame Difference')
    plt.xlabel('Original Frames')
    plt.title('Frame Differences between Original and Recorded Keyframes')
    plt.xticks(range(len(frame_differences)), [match[0] for match in matches if isinstance(match[3], int)], rotation='vertical')
    plt.tight_layout()
    os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
    plt.savefig(plot_filename)
    plt.close()

if __name__ == "__main__":
    original_frames_dir = 'frames/original_frames'
    recorded_frames_dir = 'frames/recorded_frames'

    # 读取关键帧信息文件
    with open('keyframes.json', 'r') as f:
        keyframes_info = json.load(f)

    original_keyframes = keyframes_info["original_keyframes"]
    recorded_keyframes = keyframes_info["recorded_keyframes"]

    # 设置范围值，明确标注位置以便之后修改
    range_value = 250  # 这里是范围值，您可以在需要时修改

    best_matches = find_best_match_for_keyframes(original_keyframes, original_frames_dir, recorded_keyframes, recorded_frames_dir, range_value=range_value)

    for original_frame, recorded_frames, match_score, frame_diff in best_matches:
        if recorded_frames is None:
            print(f"Original frame {original_frame} has no match (score: {match_score:.4f}, frame difference: {frame_diff})")
        else:
            print(f"Original frame {original_frame} matches with {recorded_frames} (score: {match_score:.4f}, frame difference: {frame_diff})")

    # 输出文件夹路径
    output_dir = 'output/'

    # 保存最佳匹配到CSV文件
    save_matches_to_csv(best_matches, os.path.join(output_dir, 'best_matches.csv'))

    # 生成可编辑的关键帧匹配文件
    save_editable_matches(best_matches, os.path.join(output_dir, 'editable_matches.csv'))

    # 绘制帧差异柱状图
    plot_frame_differences(best_matches, os.path.join(output_dir, 'frame_differences.png'))
