import pandas as pd
import subprocess
import json
import os
import re


def get_video_metadata(video_path):
    """Extract video metadata using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_streams', '-show_format',
        video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)

    # Duration
    duration = float(data['format'].get('duration', 0))

    # File size in MB
    file_size_mb = round(os.path.getsize(video_path) / (1024 * 1024), 2)

    # Resolution
    width, height = None, None
    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video':
            width = stream.get('width')
            height = stream.get('height')
            break

    return {
        'duration_seconds': round(duration, 2),
        'file_size_mb': file_size_mb,
        'width': width,
        'height': height,
        'resolution': f"{width}x{height}" if width and height else None,
    }


def extract_all_metadata(videos_dir, tasks_dir, output_csv):
    """Extract metadata for all videos and compute duration_ratio."""

    # Load all tasks CSV files
    tasks_frames = []
    for project in os.listdir(tasks_dir):
        project_path = os.path.join(tasks_dir, project)
        if not os.path.isdir(project_path):
            continue
        for f in os.listdir(project_path):
            if f.endswith('-tasks.csv'):
                df = pd.read_csv(os.path.join(project_path, f))
                df['project'] = project
                tasks_frames.append(df)

    tasks_df = pd.concat(tasks_frames, ignore_index=True) if tasks_frames else pd.DataFrame()
    print(f"Loaded {len(tasks_df)} tasks")

    results = []

    # Walk through all video files
    for root, dirs, files in os.walk(videos_dir):
        for filename in files:
            if not filename.endswith('.mp4'):
                continue

            video_path = os.path.join(root, filename)
            print(f"Processing: {filename}")

            metadata = get_video_metadata(video_path)
            if metadata is None:
                print(f"  Failed to extract metadata, skipping")
                continue

            # Extract tester name from filename
            tester_name = filename.replace('_video.mp4', '').split('_')[-1]
            project = os.path.basename(root)

            # Compute duration_ratio by summing all task Timeguides for this project
            duration_ratio = None
            if not tasks_df.empty and 'Timeguide' in tasks_df.columns:
                project_tasks = tasks_df[tasks_df['project'] == project]
                if not project_tasks.empty:
                    total_minutes = 0
                    for tg in project_tasks['Timeguide']:
                        tg_str = str(tg).strip()
                        tg_match = re.search(r'(\d+)', tg_str)
                        if tg_match:
                            val = int(tg_match.group(1))
                            if 'second' in tg_str.lower():
                                val = val / 60
                            total_minutes += val
                    if total_minutes > 0:
                        duration_ratio = round(
                            metadata['duration_seconds'] / (total_minutes * 60), 4
                        )

            results.append({
                'video_filename': filename,
                'tester_name': tester_name,
                'project': project,
                'duration_seconds': metadata['duration_seconds'],
                'file_size_mb': metadata['file_size_mb'],
                'resolution': metadata['resolution'],
                'width': metadata['width'],
                'height': metadata['height'],
                'duration_ratio': duration_ratio,
            })

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"\nDone! Processed {len(results)} videos. Saved to {output_csv}")
    return output_df


if __name__ == "__main__":
    extract_all_metadata(
        videos_dir='data/videos/',
        tasks_dir='data/raw/',
        output_csv='data/processed/video_metadata.csv'
    )