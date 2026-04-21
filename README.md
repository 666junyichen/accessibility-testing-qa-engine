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

## Contents
- [Step 1.1 — Transcript JSON Parser](#step-11--transcript-json-parser)
- [Step 1.2 — 60-Second Window Splitter](#step-12--60-second-window-splitter)
- [Step 1.3 — Audio Feature Extraction](#step-13--audio-feature-extraction)
- [Step 1.4 — Video Metadata Extraction](#step-14--video-metadata-extraction)
- [Step 2.1 — Transcript Data EDA](#step-21--transcript-data-eda)
- [Step 2.2 — Structured Data EDA](#step-22--structured-data-eda)
- [Step 2.3 — EDA Report](#step-23--eda-report)
- [Step 3.1 — Layer 1 Rule-Based Detector](#step-31--layer-1-rule-based-detector)
- [Step 3.2 — Layer 1 Validation on Development Samples](#step-32--layer-1-validation-on-development-samples)
- [Step 4.1 — Layer 2 Feature Engineering](#step-41--layer-2-feature-engineering)
- [Step 4.2 — Layer 2 Clustering](#step-42--layer-2-clustering)
- [Step 4.3 - R3 Cluster Interpretation Preparation](#step-43---r3-cluster-interpretation-preparation)
- [Step 5.1 - R3 Prompt Design](#step-51---r3-prompt-design)
- [Step 5.3 - R3 Manual Annotation Set](#step-53---r3-manual-annotation-set)
- [Step 8.3 - R3 Case Studies](#step-83---r3-case-studies)

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

## Step 4.2 — Layer 2 Clustering

在 876 个 60s 窗口的 7 维 standardized feature space 上运行 KMeans + DBSCAN exploratory clustering。

**输入：** `data/processed/feature_matrix_scaled.csv`（scaled）+ `data/processed/feature_matrix_raw.csv`（summary 用）

**模块：** `src/layer2/cluster_utils.py`（4 纯函数：fit_kmeans / fit_dbscan / build_cluster_summary / pca_project）

**Orchestration：** `notebooks/04_layer2_clustering.ipynb`

**算法配置：**
- KMeans：k ∈ {2,3,4,5}，n_init=10，random_state=42，silhouette + elbow + cluster size 人工选 `final_k`
- DBSCAN：`min_samples ∈ {7, 14}` 双档对比，k-distance plot 人选 eps；两档都可用时 notebook 写理由人工选一档，不预设偏好
- `primary_cluster_id = kmeans_cluster_id`（无条件继承，不做小簇 -1 保护）
- Round 1 先用启发式默认参数（`final_k=3` / `min_samples=7` / `eps=0.8`）跑通 pipeline；后续参数优化环节依据上述指标重选并更新 notebook 决策 cell。

**输出：**
- `outputs/layer2_cluster_assignments.csv`（876 行 × 7 列，R3 4.3 join key）
- `outputs/layer2_cluster_summary.csv`（每簇一行，raw feature mean/std，ddof=0）
- `outputs/layer2_cluster_composition.csv`（long-form：algorithm × cluster_id × dimension × value × count）
- `outputs/figures/layer2_{silhouette,kdist,pca,tsne}.png`

**边界声明：** fixed L1 v1 thresholds + 6 dev sample exploratory；DBSCAN 仅对照不进下游 join；若 cluster 结构被单一 tester 主导（当前观察值：`tester_name = terryaflint17`），唯一后续动作 = 扩样 + 第二轮 4.2，不在当前样本做剔除实验。高级算法（HDBSCAN / GMM / Spectral）属于 Future Work。

## Step 4.3 - R3 Cluster Interpretation Preparation
- **Document**: `docs/cluster_interpretation.md`
- **Data files**: `data/annotations/r3_window_review_sample.csv`, `data/annotations/window_semantic_labels_template.csv`
- Reviews sampled 60-second transcript windows and records early semantic patterns for later Layer 2 cluster interpretation.
- Uses the client taxonomy from `docs/friction_taxonomy.md`, based on `Friction & Sentiment Classification Framework.pdf`.
- The current draft uses sampled window text because final Layer 2 cluster outputs are not yet available.
- Final interpretation should be updated once `cluster_id`, representative windows, cluster sizes, and top terms are produced.

| Semantic pattern | Example signal | Official taxonomy link |
|------------------|----------------|------------------------|
| Comprehension friction | User says wording is formal, unclear, technical, or hard to understand | F1 |
| Confidence friction | User is unsure what to do next, whether to trust a result, or what will happen | F2 |
| Accessibility friction | Screen reader, VoiceOver, PDF, heading, focus, keyboard, or zoom issue appears | F3 |
| Unresponsive interface | User acts but the page gives no clear response or feedback | F4 |
| Unexpected behaviour | Interface behaves differently from the label, design, or user expectation | F5 |
| Content not found | User cannot locate a feedback page, claim path, support page, or needed information | F6 |
| Excessive effort | Task is possible but requires too many steps, setup, scrolling, repeated entry, or cognitive effort | F7 |
| No observed friction | Positive feedback, neutral reading, or successful task progress without a clear impediment | `none` |

```powershell
# Usage
python scripts\sample_r3_windows.py
```

## Step 5.1 - R3 Prompt Design
- **Module**: `src/layer3/prompts.py`
- **Documents**: `docs/friction_taxonomy.md`, `docs/prompt_design.md`
- Defines the R3 prompt structure and JSON output schema for future LLM-based window classification.
- `src/layer3/prompts.py` builds chat-style prompt messages only; it does not call an LLM API.
- Output labels align with the official client F1-F7 friction framework, S1-S6 severity framework, and E1-E5 sentiment framework.
- `F7` means `Excessive Effort`; no-friction windows are labelled with `friction_type = "none"`.

| Output field | Purpose |
|--------------|---------|
| `friction_type` | Dominant official friction code: F1-F7, `none`, or `unclear` |
| `friction_label` | Human-readable label for the selected friction type |
| `severity_id` | Client source severity ID: S1-S6, `none`, or `unclear` |
| `severity` | Simplified severity label: `none`, `low`, `medium`, or `high` |
| `sentiment_id` | Client source sentiment ID: E1-E5 or `unclear` |
| `sentiment` | Simplified sentiment label: `positive`, `neutral`, `negative`, `mixed`, or `unclear` |
| `narration_type` | Main narration mode, such as navigation, reading, or feedback evaluation |
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
- **Outputs**: `data/annotations/r3_manual_annotations_round1.csv`, `data/annotations/round1_blind_for_r8.csv`, `data/annotations/r8_manual_annotations_round1.csv`
- Creates a 14-window first-round annotation set for R3 using the official client taxonomy.
- Adds `task_title` and `task_instructions` from the project task CSV files in `data/raw/`.
- Produces a blind context-only file for R8 and a blank R8 annotation template so another annotator can label independently.
- Supports later Step 5.4 agreement evaluation between R3 and R8.

| File | Audience | Purpose | Contains R3 labels |
|------|----------|---------|--------------------|
| `r3_manual_annotations_round1.csv` | R3 / Nix review | R3 completed round 1 annotation | Yes |
| `round1_blind_for_r8.csv` | R8 independent annotation | Context-only blind sample | No |
| `r8_manual_annotations_round1.csv` | R8 independent annotation | Blank annotation template for R8 | No |

```powershell
# Usage
python scripts\create_r3_manual_annotation_round1.py
```
### R8 Manual Annotation Set + Kappa Agreement Check
- **Script / Notebook:** `scripts/annotate_r8_round1_updated.py`, `notebooks/04_kappa_agreement.ipynb`
- **Inputs:** `docs/friction_taxonomy.md`, `docs/prompt_design.md`, `data/annotations/round1_blind_for_r8.csv`
- **Outputs:** `data/annotations/r8_manual_annotations_round1.csv`, agreement tables, and Cohen's kappa per dimension
- Creates the R8 independent first-round manual annotation file for the same 14-window sample used in Step 5.3, using the Round 5 canonical schema.
- Uses the field definitions from `docs/friction_taxonomy.md` and `docs/prompt_design.md` to guide manual annotation.
- Keeps the annotation process blind by using `round1_blind_for_r8.csv`, which does not contain R3 labels.
- The annotation script does **not** read `data/annotations/r3_manual_annotations_round1.csv`, `docs/cluster_interpretation.md`, or `docs/case_studies.md` during annotation.
- Fields align with Round 5 canonical schema from `src/layer3/schemas_a.py` and `src/layer3/schemas_b.py`:
  - **5.1-A finding-level:** `finding`, `observed_signal`, `stated_signal`, `signal_alignment`, `friction_type` (F1-F7 / none / unclear), `severity_s` (S1-S6 / none / unclear), `sentiment_e` (E1-E5 / null), `calibrator_score_l` (L1-L5), `rationale`, `structural_amplification_note`
  - **5.1-B video-level:** `narration_quality`, `recording_quality`, `coaching_evidence`
  - **Other:** `annotated`, `confidence`, `notes`, `annotator`
- Tracks annotation completion via explicit `annotated` flag to correctly handle no-friction windows where `finding` is legitimately blank.
- Compares R3 and R8 annotations on the shared 14-window sample using `window_id`.
- Reports Cohen's kappa for:
  - **5.1-A:** `friction_type`, `severity_s` (nominal + linear weighted), `sentiment_e`, `calibrator_score_l`
  - **5.1-B:** `narration_quality`, `recording_quality`, `coaching_evidence`
- Also reports a weighted kappa for `severity_s` since severity is ordinal (S1 > S2 > ... > S6 > none).
- Produces cross-tab agreement tables and supporting field presence audit.
- Eval discipline:
  - `sentiment_e = E3` (neutral expressed) is not equal to null (no verbal expression)
  - `calibrator_score_l` is audit signal only; not merged with `severity_s`
  - E3 excluded from aggregate sentiment per client framework but retained in distribution stats

| File | Audience | Purpose |
|---|---|---|
| `r8_manual_annotations_round1.csv` | R8 independent annotation | Blind manual annotation output (Round 5 schema) |
| `04_kappa_agreement.ipynb` | Team / review | Agreement calculation and disagreement inspection |

### Kappa Agreement Results Summary

> **Pending** - R3 must re-annotate the same 14-window sample using Round 5 canonical schema before Kappa can be calculated. R8 round 1 annotation completed.

Previous results (old schema, for reference only - not comparable to Round 5):
- `friction_type` kappa = **0.6606**
- `severity` kappa = **0.3869** (simplified label)
- `sentiment` kappa = **0.6640** (simplified label)
- weighted `severity` kappa = **0.6038**

```python
# Usage
python scripts\annotate_r8_round1_updated.py
# Then open and run after R3 re-annotation:
notebooks/04_kappa_agreement.ipynb
```
## Step 8.3 - R3 Case Studies
- **Document**: `docs/case_studies.md`
- Uses selected transcript windows to write qualitative case studies for accessibility, missing information, comprehension, confidence, and excessive-effort issues.
- Current case studies are draft examples based on sampled R3 windows.
- Final case studies should be updated after full clustering, LLM classification, and agreement results are available.

| Case study focus | Related evidence source | Taxonomy link |
|------------------|-------------------------|---------------|
| Accessibility or assistive technology barrier | Transcript window + task context | F3 |
| Missing or hidden pathway | Window-level user narration | F6 |
| Readability or comprehension problem | User feedback quote | F1 |
| Confidence or trust uncertainty | Window text and qualitative notes | F2 |
| High cognitive or process effort | Window text and qualitative notes | F7 |


## R3 Current Limitations
- Layer 2 clustering results are not yet finalised for R3 cluster interpretation.
- LLM classification outputs are not yet available.
- R8 still needs to complete independent annotation in `data/annotations/r8_manual_annotations_round1.csv`.
- Step 5.4 agreement evaluation should be calculated after R8 annotation is complete.
- Step 8.3 should be revised once final cluster assignments, LLM outputs, and agreement results are available.

- LLM classification outputs are not yet available.
- Task context has not yet been automatically joined into each annotation row.
- Step 5.3 and Step 8.3 will need updates after team-level annotation, clustering, and classification results are complete.

