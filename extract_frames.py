import cv2
import os
import shutil


def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
    else:
        os.makedirs(folder_path)


def extract_frames(video_path, output_folder, fps=5):
    # 清空文件夹
    clear_folder(output_folder)

    cap = cv2.VideoCapture(video_path)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(frame_rate / fps)

    frame_count = 0
    saved_frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count:06d}.png")
            cv2.imwrite(frame_filename, frame)
            saved_frame_count += 1

        frame_count += 1

    cap.release()
    print(f"Finished extracting frames from {video_path} to {output_folder}")


if __name__ == "__main__":
    original_video_path = 'AVC_1080_MP4_1.mp4'
    recorded_video_path = 'test2.ts'

    extract_frames(original_video_path, 'frames/original_frames', fps=10)
    extract_frames(recorded_video_path, 'frames/recorded_frames', fps=10)
