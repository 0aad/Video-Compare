import os


def manual_calibration(frames_folder, num_frames_to_remove_start, num_frames_to_remove_end):
    frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.png')])
    print(f"Total frames before calibration: {len(frame_files)}")

    # 删除开头若干帧
    for i in range(num_frames_to_remove_start):
        frame_to_remove = os.path.join(frames_folder, frame_files[i])
        os.remove(frame_to_remove)

    # 删除尾部若干帧
    if num_frames_to_remove_end > 0:
        for i in range(num_frames_to_remove_end):
            frame_to_remove = os.path.join(frames_folder, frame_files[-(i + 1)])
            os.remove(frame_to_remove)

    # 重新命名剩余的帧
    remaining_frame_files = sorted([f for f in os.listdir(frames_folder) if f.endswith('.png')])
    for index, frame_file in enumerate(remaining_frame_files):
        old_frame_path = os.path.join(frames_folder, frame_file)
        new_frame_path = os.path.join(frames_folder, f"frame_{index:06d}.png")
        os.rename(old_frame_path, new_frame_path)

    print(f"Total frames after calibration: {len(remaining_frame_files)}")


def get_frames_folder(identifier):
    if identifier == 'R':
        return 'frames/recorded_frames'
    elif identifier == 'O':
        return 'frames/original_frames'
    else:
        raise ValueError("Invalid identifier. Use 'R' for recorded frames and 'O' for original frames.")


if __name__ == "__main__":
    identifier = input("Enter 'R' for recorded frames or 'O' for original frames: ").strip().upper()
    frames_folder = get_frames_folder(identifier)
    num_frames_to_remove_start = int(input("Enter the number of frames to remove from the beginning: "))
    num_frames_to_remove_end = int(input("Enter the number of frames to remove from the end: "))
    manual_calibration(frames_folder, num_frames_to_remove_start, num_frames_to_remove_end)
