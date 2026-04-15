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

## Step 4.3 - R3 Cluster Interpretation Preparation
- **Documents**: `docs/cluster_interpretation.md`
- **Data files**: `data/annotations/r3_window_review_sample.csv`, `data/annotations/window_semantic_labels_template.csv`
- Reviews sampled 60-second transcript windows and records early semantic patterns for later cluster interpretation.
- The current draft uses sampled window text because Layer 2 cluster outputs are not yet available.
- Final interpretation should be updated once `cluster_id`, representative windows, cluster sizes, and top terms are produced.

| Semantic pattern | Example signal | Taxonomy link |
|------------------|----------------|---------------|
| Navigation / findability | User cannot locate a feedback page, claim path, or key action | F1 |
| Content clarity | User says wording is formal, unclear, or hard to understand | F2 |
| Interaction / control | Form, MFA, upload, or validation flow blocks progress | F3 |
| Accessibility / AT | Screen reader, VoiceOver, PDF, heading, or focus issue appears | F4 |
| Support / trust / safety | User questions trust, support, sensitivity, or reassurance | F6 |

```powershell
# Usage
python scripts\sample_r3_windows.py
```

## Step 5.1 - R3 Prompt Design
- **Module**: `src/layer3/prompts.py`
- **Documents**: `docs/friction_taxonomy.md`, `docs/prompt_design.md`
- Defines the R3 semantic taxonomy, prompt structure, and JSON output schema for future LLM-based window classification.
- `src/layer3/prompts.py` builds chat-style prompt messages only; it does not call an LLM API.
- Output labels align with the manual annotation template used in Step 5.3.

| Output field | Purpose |
|--------------|---------|
| `friction_type` | Dominant F1-F7 semantic friction category |
| `severity` | Estimated seriousness of the issue |
| `sentiment` | User attitude or emotional tone in the window |
| `narration_type` | Main narration mode, such as navigation or feedback |
| `primary_evidence` | Short quote supporting the chosen label |
| `rationale` | Brief explanation for the classification |

```python
# Usage
import sys; sys.path.insert(0, 'src')
from layer3.prompts import build_messages

messages = build_messages(
    window_id='example_window_id',
    project='example_project',
    video_id='example_video_id',
    window_text='Transcript window text goes here.',
    task_title='Task title goes here.',
    task_instructions='Task instructions go here.'
)
```

## Step 5.3 - R3 Manual Annotation Set
- **Script**: `scripts/create_r3_manual_annotation_round1.py`
- **Input**: `data/annotations/r3_window_review_sample.csv`
- **Outputs**: `data/annotations/r3_manual_annotations_round1.csv`, `data/annotations/round1_blind_for_r8.csv`
- Creates a 14-window first-round annotation set covering the F1-F7 friction categories.
- Adds `task_title` and `task_instructions` from the project task CSV files in `data/raw/`.
- Produces a blind copy for R8 so Step 5.4 can later calculate inter-annotator agreement.

| File | Audience | Contains R3 labels |
|------|----------|--------------------|
| `r3_manual_annotations_round1.csv` | R3 / Nix review | Yes |
| `round1_blind_for_r8.csv` | R8 independent annotation | No |

```powershell
# Usage
python scripts\create_r3_manual_annotation_round1.py
```

## Step 8.3 - R3 Case Studies
- **Document**: `docs/case_studies.md`
- Uses selected transcript windows to write qualitative case studies for accessibility, navigation, readability, and support-related issues.
- Current case studies are draft examples based on sampled R3 windows.
- Final case studies should be updated after full clustering, LLM classification, and agreement results are available.

| Case study focus | Related evidence source |
|------------------|-------------------------|
| Accessibility or assistive technology barrier | Transcript window + task context |
| Navigation or findability breakdown | Window-level user narration |
| Readability or content clarity problem | User feedback quote |
| Support, trust, or safety concern | Window text and qualitative notes |

## R3 Current Limitations
- Layer 2 clustering results are not yet available in the current repository.
- LLM classification outputs are not yet available.
- Step 5.3 still requires R8 independent annotation, adjudication, and agreement evaluation.
- Step 8.3 should be revised once final cluster and classification outputs are complete.

- LLM classification outputs are not yet available.
- Task context has not yet been automatically joined into each annotation row.
- Step 5.3 and Step 8.3 will need updates after team-level annotation, clustering, and classification results are complete.


