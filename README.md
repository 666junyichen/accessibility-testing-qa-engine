# CS20 Project

## Data Source
AWS S3 bucket:
usyd-03-2025-cs20-1-proj-assets

## Structure
- data/raw: raw data (S3)
- data/processed: processed data
- src: core code
- notebooks: experiments
- outputs: results

## Pipeline
MP4 → JSON → Parser → Analysis

## Environment
Python 3.10+

## Setup
pip install -r requirements.txt

## Usage
Run notebooks or scripts in src/ for data processing and analysis.

## Step 1.1 — Transcript JSON Parser
- **Module**: `src/data/transcript_parser.py`
- Parses AWS Transcribe JSON into three structured CSVs: `transcripts.csv`, `items.csv`, `segments.csv`
- Completed for all 57 videos; segments.csv contains 26,191 rows

## Step 1.2 — 60-Second Window Splitter
- **Module**: `src/preprocessing/window_splitter.py`
- **Tests**: `tests/test_window_splitter.py` (16 tests)
- Aggregates `segments.csv` into ~60s time windows, outputs `data/processed/windows.csv` (3,331 windows, 57 videos)
- `word_count` is computed via `items.csv` by counting `type=pronunciation` entries
- `video_id` format: `{tester_name}_{project_abbr}` (wa / suncorp / uq)
- Some speech-sparse videos produce oversized windows; handled by Step 3.1 Recording Quality

```python
# Usage
import sys; sys.path.insert(0, 'src')
from preprocessing.window_splitter import split_windows, build_windows_csv

windows = split_windows('data/processed/segments.csv', 'data/processed/items.csv')
build_windows_csv('data/processed/segments.csv', 'data/processed/items.csv', 'data/processed/windows.csv')
```
## Step 1.3 — Audio Feature Extraction
- **Module**: `src/preprocessing/audio_features.py`
- Extracts audio features for each 60-second window from MP4 videos
- Features: `silence_ratio`, `narration_density`, `avg_silence_duration`, `words_per_minute`, `avg_confidence`
- `avg_confidence` is derived from `items.csv` (type=pronunciation entries)
- Output: `data/processed/audio_features.csv` (871 windows across 6 sample videos)

```python
# Usage
import sys; sys.path.insert(0, 'src')
from preprocessing.audio_features import extract_all_features

extract_all_features(
    windows_csv='data/processed/windows.csv',
    items_csv='data/processed/items.csv',
    videos_dir='data/videos/',
    output_csv='data/processed/audio_features.csv'
)
```

## Step 1.4 — Video Metadata Extraction
- **Module**: `src/preprocessing/video_metadata.py`
- Extracts video-level metadata using ffprobe: duration, resolution, file size
- Computes `duration_ratio = actual_duration / timeguide` using tasks.csv
- Output: `data/processed/video_metadata.csv` (15 sample videos)

```python
# Usage
import sys; sys.path.insert(0, 'src')
from preprocessing.video_metadata import extract_all_metadata

extract_all_metadata(
    videos_dir='data/videos/',
    tasks_dir='data/raw/',
    output_csv='data/processed/video_metadata.csv'
)
```

## Step 2.2 — Structured Data EDA
- **Notebook**: `notebooks/02_structured_data_eda.ipynb`
- Performs exploratory data analysis on structured data across three projects
- Focus areas:
  - Number of testers and tasks per project
  - Cross-project tester participation
  - Task type distribution
  - Timeguide distribution
  - Deviation between actual video duration and expected Timeguide (`duration_ratio`)
- Uses both processed data (`windows.csv`, `video_metadata.csv`) and minimal raw data (`tasks.csv`)
- Output: summary tables and visualizations (notebook-based, no fixed CSV output)

```python
# Usage
import sys; sys.path.insert(0, 'src')

import pandas as pd

# Load processed data
windows = pd.read_csv('data/processed/windows.csv')
video_metadata = pd.read_csv('data/processed/video_metadata.csv')

# Load task-level data (minimal raw dependency)
tasks_df = pd.read_csv('data/raw/.../tasks.csv')

# Example analysis
tester_per_project = windows.groupby("project")["tester_name"].nunique()
task_per_project = tasks_df.groupby("project")["Order"].nunique()
duration_ratio = video_metadata["duration_ratio"].describe()

## Step 3.1 — Layer 1 Rule-Based Detector
- **Module**: `src/layer1/rule_detector.py`
- Detects recording quality issues using hard-coded thresholds:

| Rule | Threshold | Flag |
|------|-----------|------|
| Video duration vs Timeguide | duration_ratio < 0.3 or > 3.0 | `DURATION_ANOMALY` |
| Silence ratio | silence_ratio > 0.6 | `EXCESSIVE_SILENCE` |
| Transcription confidence | avg_confidence < 0.7 | `LOW_AUDIO_QUALITY` |
| Narration density | narration_density < 0.2 | `SPARSE_NARRATION` |

- Each flag includes: video_filename, window_id, start_time, end_time, value
- Output: `data/processed/layer1_flags.csv` (333 flags across 15 videos)

```python
# Usage
import sys; sys.path.insert(0, 'src')
from layer1.rule_detector import detect_flags

detect_flags(
    audio_features_csv='data/processed/audio_features.csv',
    video_metadata_csv='data/processed/video_metadata.csv',
    output_csv='data/processed/layer1_flags.csv'
)
```