import pandas as pd
import numpy as np
import librosa
import subprocess
import os

# Silence energy threshold for short-term energy silence detection (16kHz sample rate)
# Initial value based on empirical setting; should be validated against different
# recording devices during EDA phase
SILENCE_ENERGY_THRESHOLD = 0.001


def extract_audio_from_video(video_path, audio_path):
    """Extract audio from MP4 video using ffmpeg."""
    subprocess.run([
        'ffmpeg', '-i', video_path,
        '-ac', '1', '-ar', '16000',
        '-y', audio_path
    ], capture_output=True)


def get_audio_features_for_window(y, sr, start_time, end_time):
    """Extract audio features for a single 60-second window."""
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    y_window = y[start_sample:end_sample]

    if len(y_window) == 0:
        return None

    # Silence detection using short-term energy
    frame_length = 2048
    hop_length = 512
    energy = np.array([
        np.sum(np.abs(y_window[i:i+frame_length]**2))
        for i in range(0, len(y_window)-frame_length, hop_length)
    ])
    silence_threshold = SILENCE_ENERGY_THRESHOLD
    silence_ratio = np.mean(energy < silence_threshold)

    # Narration density (proportion of time with speech)
    narration_density = 1.0 - silence_ratio

    # Average silence segment duration
    is_silence = energy < silence_threshold
    silence_durations = []
    count = 0
    for s in is_silence:
        if s:
            count += 1
        elif count > 0:
            silence_durations.append(count * hop_length / sr)
            count = 0
    avg_silence_duration = np.mean(silence_durations) if silence_durations else 0.0

    return {
        'silence_ratio': round(float(silence_ratio), 4),
        'narration_density': round(float(narration_density), 4),
        'avg_silence_duration': round(float(avg_silence_duration), 4),
    }


def compute_avg_confidence(items_df, video_filename, start_time, end_time):
    """Compute average transcription confidence for a window from items.csv."""
    mask = (
        (items_df['video_filename'] == video_filename) &
        (items_df['start_time'] >= start_time) &
        (items_df['end_time'] <= end_time) &
        (items_df['type'] == 'pronunciation')
    )
    subset = items_df[mask]
    if len(subset) == 0:
        return None
    return round(float(subset['confidence'].mean()), 4)


def find_video_path(videos_dir, video_filename):
    """Search for a video file by exact filename across all subdirectories."""
    targets = {
        video_filename,
        video_filename + '.mp4',
        video_filename.replace('.mp4', '_video.mp4'),
    }
    for root, dirs, files in os.walk(videos_dir):
        for f in files:
            if f in targets:
                return os.path.join(root, f)
    return None


def extract_all_features(windows_csv, items_csv, videos_dir, output_csv):
    """Extract audio features for all windows and save to CSV."""
    windows_df = pd.read_csv(windows_csv)
    items_df = pd.read_csv(items_csv)

    results = []
    audio_cache = {}

    for _, row in windows_df.iterrows():
        video_id = row['video_id']
        window_id = row['window_id']
        start_time = float(row['start_time'])
        end_time = float(row['end_time'])
        duration = float(row['duration'])
        word_count = int(row['word_count'])
        video_filename = str(row['video_filename'])

        print(f"Processing window: {window_id}")

        # Find and load audio
        if video_filename not in audio_cache:
            mp4_path = find_video_path(videos_dir, video_filename)
            if mp4_path is None:
                print(f"  Video not found: {video_filename}, skipping")
                audio_cache[video_filename] = None
                continue

            audio_path = mp4_path.replace('.mp4', '.wav')
            if not os.path.exists(audio_path):
                print(f"  Extracting audio: {mp4_path}")
                extract_audio_from_video(mp4_path, audio_path)

            y, sr = librosa.load(audio_path, sr=16000)
            audio_cache[video_filename] = (y, sr)

        if audio_cache[video_filename] is None:
            continue

        y, sr = audio_cache[video_filename]

        features = get_audio_features_for_window(y, sr, start_time, end_time)
        if features is None:
            continue

        wpm = round(word_count / (duration / 60), 2) if duration > 0 else 0
        avg_conf = compute_avg_confidence(items_df, video_filename, start_time, end_time)

        results.append({
            'window_id': window_id,
            'video_id': video_id,
            'video_filename': video_filename,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'silence_ratio': features['silence_ratio'],
            'narration_density': features['narration_density'],
            'avg_silence_duration': features['avg_silence_duration'],
            'words_per_minute': wpm,
            'avg_confidence': avg_conf,
        })

    output_df = pd.DataFrame(results)
    output_df.to_csv(output_csv, index=False)
    print(f"\nDone! Processed {len(results)} windows. Saved to {output_csv}")
    return output_df


if __name__ == "__main__":
    extract_all_features(
        windows_csv='data/processed/windows.csv',
        items_csv='data/processed/items.csv',
        videos_dir='data/videos/',
        output_csv='data/processed/audio_features.csv'
    )