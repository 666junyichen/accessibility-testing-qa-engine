import pandas as pd


# Thresholds for rule-based detection
THRESHOLDS = {
    'duration_ratio_min': 0.3,
    'duration_ratio_max': 3.0,
    'silence_ratio_max': 0.6,
    'avg_confidence_min': 0.7,
    'narration_density_min': 0.2,
}


def detect_flags(audio_features_csv, video_metadata_csv, windows_csv, output_csv):
    """
    Run Layer 1 rule-based detection on all videos.
    Returns a DataFrame with one row per flag detected.
    """
    audio_df = pd.read_csv(audio_features_csv)
    metadata_df = pd.read_csv(video_metadata_csv)
    windows_df = pd.read_csv(windows_csv)

    window_info = windows_df.set_index('window_id')[
        ['video_filename', 'tester_name', 'project']
    ].to_dict('index')

    flags = []

    # --- Check video-level flags from metadata ---
    for _, row in metadata_df.iterrows():
        video_filename = row['video_filename']
        tester = row['tester_name']
        project = row['project']
        duration_ratio = row.get('duration_ratio', None)

        if pd.notna(duration_ratio):
            if duration_ratio < THRESHOLDS['duration_ratio_min']:
                flags.append({
                    'video_filename': video_filename,
                    'tester_name': tester,
                    'project': project,
                    'flag': 'DURATION_ANOMALY',
                    'detail': f"duration_ratio={duration_ratio} (< {THRESHOLDS['duration_ratio_min']})",
                    'window_id': None,
                    'start_time': None,
                    'end_time': None,
                    'value': duration_ratio,
                })
            elif duration_ratio > THRESHOLDS['duration_ratio_max']:
                flags.append({
                    'video_filename': video_filename,
                    'tester_name': tester,
                    'project': project,
                    'flag': 'DURATION_ANOMALY',
                    'detail': f"duration_ratio={duration_ratio} (> {THRESHOLDS['duration_ratio_max']})",
                    'window_id': None,
                    'start_time': None,
                    'end_time': None,
                    'value': duration_ratio,
                })

    # --- Check window-level flags from audio features ---
    for _, row in audio_df.iterrows():
        window_id = row['window_id']
        video_id = row['video_id']
        start_time = row.get('start_time', None)
        end_time = row.get('end_time', None)
        silence_ratio = row.get('silence_ratio', None)
        narration_density = row.get('narration_density', None)
        avg_confidence = row.get('avg_confidence', None)

        info = window_info.get(window_id, {})
        wf = info.get('video_filename')
        tn = info.get('tester_name')
        pj = info.get('project')

        if pd.notna(silence_ratio) and silence_ratio > THRESHOLDS['silence_ratio_max']:
            flags.append({
                'video_filename': wf,
                'tester_name': tn,
                'project': pj,
                'flag': 'EXCESSIVE_SILENCE',
                'detail': f"silence_ratio={silence_ratio} (> {THRESHOLDS['silence_ratio_max']})",
                'window_id': window_id,
                'start_time': start_time,
                'end_time': end_time,
                'value': silence_ratio,
            })

        if pd.notna(avg_confidence) and avg_confidence < THRESHOLDS['avg_confidence_min']:
            flags.append({
                'video_filename': wf,
                'tester_name': tn,
                'project': pj,
                'flag': 'LOW_AUDIO_QUALITY',
                'detail': f"avg_confidence={avg_confidence} (< {THRESHOLDS['avg_confidence_min']})",
                'window_id': window_id,
                'start_time': start_time,
                'end_time': end_time,
                'value': avg_confidence,
            })

        if pd.notna(narration_density) and narration_density < THRESHOLDS['narration_density_min']:
            flags.append({
                'video_filename': wf,
                'tester_name': tn,
                'project': pj,
                'flag': 'SPARSE_NARRATION',
                'detail': f"narration_density={narration_density} (< {THRESHOLDS['narration_density_min']})",
                'window_id': window_id,
                'start_time': start_time,
                'end_time': end_time,
                'value': narration_density,
            })

    flags_df = pd.DataFrame(flags)
    flags_df.to_csv(output_csv, index=False)

    print(f"Done! Detected {len(flags_df)} flags across {audio_df['video_id'].nunique()} videos.")
    print(f"\nFlag summary:")
    if not flags_df.empty:
        print(flags_df['flag'].value_counts().to_string())
    else:
        print("No flags detected.")

    return flags_df


if __name__ == "__main__":
    detect_flags(
        audio_features_csv='data/processed/audio_features.csv',
        video_metadata_csv='data/processed/video_metadata.csv',
        windows_csv='data/processed/windows.csv',
        output_csv='data/processed/layer1_flags.csv'
    )