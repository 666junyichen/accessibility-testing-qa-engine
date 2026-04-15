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
## Step 2.1 — Transcript Data EDA
- **Notebook**: `notebooks/01_transcript_eda.ipynb`
- Performs exploratory data analysis on transcript-derived data for **6 development-sample videos**
- Development samples:
  - `ghum_wa`
  - `reneerussell99_wa`
  - `terryaflint17_suncorp`
  - `carlpatrickrobinson_suncorp`
  - `ramazankawish_uq`
  - `jenniferparry7_uq`
- Focus areas:
  - transcript / segment / item coverage after filtering
  - words-per-minute distribution
  - word-level and window-level confidence patterns
  - silence-related feature distribution
  - prototype cases for later Layer 1 rule design
- Key findings:
  - `ghum_wa` shows an anomalously high average WPM (~220), which requires verification
  - around **12% of words** fall below confidence **0.8**, suggesting the current `LOW_AUDIO_QUALITY` threshold of 0.7 may be too permissive
  - `terryaflint17_suncorp` is the clearest sparse-narration prototype (`narration_density` ≈ 0.23)
- Uses processed transcript/audio tables such as `windows.csv`, `segments.csv`, `items.csv`, and `audio_features.csv`
- Output: notebook-based summary tables and visualizations (no fixed CSV output)

```python
# Usage
import sys; sys.path.insert(0, 'src')

import pandas as pd

# Load processed transcript-related data
windows = pd.read_csv('data/processed/windows.csv')
segments = pd.read_csv('data/processed/segments.csv')
items = pd.read_csv('data/processed/items.csv')
audio_features = pd.read_csv('data/processed/audio_features.csv')

# Filter to 6 development samples
DEV_VIDEO_IDS = [
    'ghum_wa',
    'reneerussell99_wa',
    'terryaflint17_suncorp',
    'carlpatrickrobinson_suncorp',
    'ramazankawish_uq',
    'jenniferparry7_uq'
]

windows_dev = windows[windows['video_id'].isin(DEV_VIDEO_IDS)]
segments_dev = segments[segments['video_id'].isin(DEV_VIDEO_IDS)]
items_dev = items[items['video_id'].isin(DEV_VIDEO_IDS)]
audio_dev = audio_features[audio_features['video_id'].isin(DEV_VIDEO_IDS)]

# Example analyses
wpm_by_video = audio_dev.groupby('video_id')['words_per_minute'].mean().sort_values(ascending=False)
word_conf_dist = items_dev['confidence'].describe()
narration_density_by_video = audio_dev.groupby('video_id')['narration_density'].mean().sort_values()

print(wpm_by_video)
print(word_conf_dist)
print(narration_density_by_video)
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
```

## Step 2.3 — EDA Report 
- **Report**: `eda_report.md`
- Consolidates findings from:
  - Step 2.1 — Transcript Data EDA
  - Step 2.2 — Structured Data EDA
- Summarises key data quality issues, prototype cases, and implications for later Layer 1 rule design
- Main report themes:
  - dataset coverage and development-sample scope
  - anomalous speech-rate case (`ghum_wa`)
  - low-confidence transcription patterns
  - duration deviation from Timeguide
  - sparse-narration prototype case (`terryaflint17_suncorp`)
  - cross-project structural observations
  - preliminary threshold suggestions for Layer 1
- Key findings:
  - `ghum_wa` shows an anomalously high average WPM (~220), which requires verification
  - around **12% of words** fall below confidence **0.8**, suggesting the current `LOW_AUDIO_QUALITY` threshold may be too lenient
  - `terryaflint17_suncorp` is the clearest sparse-narration prototype (`narration_density` ≈ 0.23)
  - actual durations substantially exceed Timeguide expectations (**mean duration ratio ≈ 5.66×**)
- Output: integrated markdown report for W7/W8 discussion and Layer 1 calibration reference

```python
# Usage
from pathlib import Path

report_path = Path("eda_report.md")
print(report_path.read_text(encoding="utf-8")[:1000])  # preview first part of the report
```

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
- Output: `data/processed/layer1_flags.csv` (211 flags across 6 dev-sample videos)

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


## Step 3.2 — Layer 1 Validation on Development Samples
- **Notebook**: `notebooks/03_layer1_validation.ipynb`
- Validates Layer 1 on **6 development samples** through manual inspection and threshold review
- Reviews whether rule outputs are reasonable under the current hard-coded thresholds:

| Rule | Threshold | Verdict |
|------|-----------|---------|
| Video duration vs Timeguide | `duration_ratio < 0.3 or > 3.0` | Appropriate |
| Silence ratio | `silence_ratio > 0.6` | Appropriate |
| Transcription confidence | `avg_confidence < 0.7` | Too permissive |
| Narration density | `narration_density < 0.2` | Functional but conservative |

- Threshold adjustment record:

| Flag | Current | Recommended |
|------|---------|-------------|
| `DURATION_ANOMALY` | `< 0.3 or > 3.0` | No change |
| `EXCESSIVE_SILENCE` | `> 0.6` | No change |
| `LOW_AUDIO_QUALITY` | `< 0.7` | `< 0.75` |
| `SPARSE_NARRATION` | `< 0.2` | `< 0.3` |

- Development samples:
  - `ghum_wa`
  - `reneerussell99_wa`
  - `terryaflint17_suncorp`
  - `carlpatrickrobinson_suncorp`
  - `ramazankawish_uq`
  - `jenniferparry7_uq`

- Validation summary:
  - `DURATION_ANOMALY`: **2** flagged cases, both judged reasonable
  - `EXCESSIVE_SILENCE`: **38** flagged windows, all from `terryaflint17_suncorp`
  - `LOW_AUDIO_QUALITY`: **21** flagged windows across 4 development samples
  - `SPARSE_NARRATION`: **5** flagged windows, all from `terryaflint17_suncorp`

- Output:
  - sample-level validation notebook
  - manual rule assessment
  - threshold adjustment record
  - proposed Layer 1 threshold updates for v2

```python
import pandas as pd

flags = pd.read_csv('data/processed/layer1_flags.csv')
audio = pd.read_csv('data/processed/audio_features.csv')
metadata = pd.read_csv('data/processed/video_metadata.csv')

DEV_VIDEO_IDS = [
    'ghum_wa',
    'reneerussell99_wa',
    'terryaflint17_suncorp',
    'carlpatrickrobinson_suncorp',
    'ramazankawish_uq',
    'jenniferparry7_uq'
]

audio_dev = audio[audio['video_id'].isin(DEV_VIDEO_IDS)]
print(audio_dev['video_id'].nunique(), 'development samples')
print(flags['flag'].value_counts())
```

## Step 4.1 — Layer 2 Feature Engineering
- **Module**: `src/layer2/feature_engineering.py`
- **Tests**: `tests/test_feature_engineering.py` (27 tests)
- Builds the L2-only feature matrix (raw + standardized) from `audio_features.csv` and `windows.csv`
- 7 features: `silence_ratio`, `narration_density`, `words_per_minute`, `avg_silence_duration`, `avg_confidence`, `unique_words_ratio`, `avg_sentence_length`
- Two text features derived from `windows.text`:
  - `unique_words_ratio` = unique tokens / total tokens (alnum tokens only, lowercased)
  - `avg_sentence_length` = total tokens / sentence count (split on `.!?`, fallback = 1)
- Imputation policy: per-column NaN rate `< 1%` filled with column mean; rate `≥ 1%` raises and aborts (no silent drop). Concentration by `video_id` is logged for debugging
- Join consistency check: `video_id`, `video_filename`, `start_time`, `end_time` must agree between `audio_features.csv` and `windows.csv` (float tol = 1e-6)
- Standardization: `StandardScaler` (z-score) applied to the 7 feature columns; column names retained without `_z` suffix
- Outputs:
  - `data/processed/feature_matrix_raw.csv` (876 windows)
  - `data/processed/feature_matrix_scaled.csv` (876 windows)
  - `data/processed/feature_engineering_imputation.log` (per-column nan_count / nan_rate / filled)
- Scope: L2-only; not used by L3 / R5 / R6
- Dev-set sanity (qualitative): `ghum` `avg_sentence_length ≈ 10.4`, `terryaflint17` ≈ `6.3`, `reneerussell99` ≈ `26.3` (outlier flagged for Step 4.2 review)

```python
# Usage
python -m src.layer2.feature_engineering
# Reads:
#   data/processed/audio_features.csv
#   data/processed/windows.csv
# Writes:
#   data/processed/feature_matrix_raw.csv
#   data/processed/feature_matrix_scaled.csv
#   data/processed/feature_engineering_imputation.log
```

## R3 NLP Semantic Analysis

This section documents the R3 NLP semantic analysis deliverables for Step 4.3, Step 5.1, Step 5.3, and Step 8.3.

### Step 4.3 - Cluster Interpretation Preparation

- **Documents**: `docs/cluster_interpretation.md`
- **Data files**: `data/annotations/r3_window_review_sample.csv`, `data/annotations/window_semantic_labels_template.csv`
- **Purpose**: reviews representative transcript windows and records early semantic patterns such as navigation issues, content clarity problems, interaction failures, accessibility barriers, and support or trust concerns.
- **Current status**: draft interpretation preparation is complete based on sampled window-level transcript data.
- **Pending dependency**: final cluster interpretation still requires Layer 2 clustering outputs, including `cluster_id`, representative windows, cluster sizes, and top terms or keywords.

### Step 5.1 - Prompt Design

- **Documents**: `docs/friction_taxonomy.md`, `docs/prompt_design.md`
- **Module**: `src/layer3/prompts.py`
- **Purpose**: defines the R3 semantic taxonomy, prompt structure, and JSON output schema for future LLM-based window classification.
- **Current status**: prompt template and schema are implemented.
- **Important note**: `src/layer3/prompts.py` only builds prompt messages. It does not call an LLM API.

### Step 5.3 - Manual Annotation Set

- **Data file**: `data/annotations/r3_manual_annotations_round1.csv`
- **Script**: `scripts/create_r3_manual_annotation_round1.py`
- **Purpose**: creates a first-round manual annotation sample from the R3 reviewed windows.
- **Current status**: initial annotation sample is prepared with windows covering the F1-F7 friction categories.
- **Pending dependency**: formal validation still requires independent annotation by another team member, adjudicated labels, and agreement evaluation.

### Step 8.3 - Case Studies

- **Document**: `docs/case_studies.md`
- **Purpose**: records early qualitative case studies using selected transcript windows to explain accessibility, navigation, readability, and support-related issues.
- **Current status**: initial case study draft is complete.
- **Pending dependency**: final case studies should be updated after full clustering, LLM classification, and final analysis outputs are available.

### Helper Scripts

- `scripts/sample_r3_windows.py` samples transcript windows from `data/processed/windows.csv` for R3 semantic review.
- `scripts/create_r3_manual_annotation_round1.py` creates the first-round manual annotation CSV from the reviewed R3 sample.

### R3 Current Limitations

- Layer 2 clustering results are not yet available in the current repository.
- LLM classification outputs are not yet available.
- Task context has not yet been automatically joined into each annotation row.
- Step 5.3 and Step 8.3 will need updates after team-level annotation, clustering, and classification results are complete.


