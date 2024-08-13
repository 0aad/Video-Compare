import csv
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

class FrameComparisonVisualizer:
    def __init__(self, csv_file, video_length_seconds):
        self.csv_file = csv_file
        self.results = self.load_results()
        self.video_length_seconds = video_length_seconds

    def load_results(self):
        results = []
        with open(self.csv_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                original_frame = self.format_frame_name(row[0], "O")
                matched_frame = self.format_frame_name(row[1], "R")
                similarity_score = float(row[2])
                difference = float(row[3])
                results.append((original_frame, matched_frame, similarity_score, difference))
        return results

    def format_frame_name(self, frame_name, prefix):
        frame_number = frame_name.split('_')[1].split('.')[0]
        return f"{prefix} frame{int(frame_number)}"

    def frame_to_time(self, frame_number, total_frames):
        seconds = (frame_number / total_frames) * self.video_length_seconds
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def save_colored_csv(self, output_html):
        # 使用 Pandas DataFrame 处理结果
        df = pd.DataFrame(self.results, columns=["Original Frame", "Matched Frame", "Similarity Score", "Difference to 1.0"])

        # 创建颜色编码
        def color_negative_red(val):
            color = f'background-color: rgba(255, 0, 0, {val})' if val > 0 else 'background-color: white'
            return color

        df_styled = df.style.map(color_negative_red, subset=['Difference to 1.0'])

        # 保存为 HTML 文件
        html = df_styled.to_html()
        with open(output_html, 'w') as f:
            f.write(html)

    def plot_similarity_differences(self, plot_filename):
        differences = [result[3] for result in self.results]
        num_results = len(differences)
        total_frames = len(self.results)

        plt.figure(figsize=(10, 6))
        plt.bar(range(num_results), differences, color='skyblue')
        plt.ylabel('Difference to 1.0')
        plt.xlabel('Frame Pairs')
        plt.title('Similarity Differences to 1.0 between Original and Recorded Frames')

        # 仅显示每10%位置上的标签
        step = max(1, num_results // 10)
        xticks = range(0, num_results, step)
        xtick_labels = [f"{self.results[i][0]} ({self.frame_to_time(i, total_frames)})" for i in xticks]

        plt.xticks(xticks, xtick_labels, rotation='vertical')
        plt.tight_layout()
        os.makedirs(os.path.dirname(plot_filename), exist_ok=True)
        plt.savefig(plot_filename)
        plt.close()

# 示例如何使用该类
if __name__ == "__main__":
    csv_file = 'output/compare_results.csv'
    output_html = 'output/colored_compare_results.html'
    plot_filename = 'output/similarity_differences_diagram.png'

    # 询问原视频总长度（以秒为单位）
    video_length_seconds = float(input("Enter the total length of the original video in seconds: "))

    visualizer = FrameComparisonVisualizer(csv_file, video_length_seconds)
    visualizer.save_colored_csv(output_html)
    visualizer.plot_similarity_differences(plot_filename)
