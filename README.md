<img width="1635" height="554" alt="image" src="https://github.com/user-attachments/assets/d0c293f0-dce1-4fd9-b0e4-b85313d1d14e" /># CS20 Project

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
- [Step 0.1 - Repository and Environment Setup](#step-01---repository-and-environment-setup)
- [Step 0.2 - AWS Transcribe Export Collection](#step-02---aws-transcribe-export-collection)
- [Step 0.3 - Structured Raw Data Preparation](#step-03---structured-raw-data-preparation)
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
- [Step 5.1 - Prompt Design (Round 5 canonical)](#step-51---prompt-design-round-5-canonical)
- [Step 5.3 - R3 Manual Annotation Set](#step-53---r3-manual-annotation-set)
- [Step 8.3 - R3 Case Studies](#step-83---r3-case-studies)

## Step 0.1 - Repository and Environment Setup
- **Status**: completed
- Sets up the project repository skeleton and shared working structure:
  - `data/raw/`
  - `data/processed/`
  - `src/`
  - `notebooks/`
  - `tests/`
- Uses Python `3.10+` with dependencies tracked in `requirements.txt`
- Provides the baseline project README and runnable repository layout for team development

## Step 0.2 - AWS Transcribe Export Collection
- **Status**: completed with one retained edge case
- Collects AWS Transcribe JSON outputs under `data/raw/transcribe-output/`
- Current repository state includes transcribe outputs for the development projects used in downstream parsing
- Known edge case retained in the dataset:
  - `troyparnell` is kept as a transcript failure / near-empty-file case for later validation handling
- These JSON files are the source inputs for `src/data/transcript_parser.py`

## Step 0.3 - Structured Raw Data Preparation
- **Status**: completed with source-data limitation noted
- Organises structured raw files under `data/raw/`, including:
  - `organisations-data.csv`
  - `tester_db.csv`
  - `schema-research.sql`
  - project folders such as `department-of-premier-and-cabinet-wa/`, `suncorp-insurance/`, `the-university-of-queensland/`, and `bupa-uk/`
- Maintains `data/raw/tester_video_mapping.csv` for the currently recoverable mapping:
  - `video_filename -> project -> tester_name`
- Source-data limitation:
  - the current `*-assignments.csv` files in the repo contain tester roster fields such as `TesterFullName`, `OptedIn`, and `TesterCohorts`
  - they do **not** contain tester-to-task linkage, so `assignment_id`, `task_id`, and `task_title` cannot be reliably recovered from the current source files
- Practical implication:
  - Step 0.3 is complete for data organisation and video/project/tester mapping
  - task-level mapping should remain documented as unavailable unless a richer assignment export is provided later

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

## Step 2.2 - Structured Data EDA
- **Notebook**: `notebooks/02_structured_data_eda.ipynb`
- Performs exploratory data analysis on the current local structured-data snapshot
- Structured scope in the current snapshot:
  - full structured EDA for the 3 development projects (`department-of-premier-and-cabinet-wa`, `suncorp-insurance`, `the-university-of-queensland`)
  - survey-only analysis for `bupa-uk`
  - Brighton excluded because only raw videos are currently available locally
- Focus areas:
  - raw-data coverage by project
  - number of testers and tasks per development project
  - cross-project tester participation
  - task type distribution
  - Timeguide distribution
  - deviation between actual video duration and expected Timeguide (`duration_ratio`)
  - survey bundle scale and question-type mix where local survey files exist
- Uses both processed data (`windows.csv`, `video_metadata.csv`) and raw structured files such as project `tasks.csv`, `tester_db.csv`, and local survey bundles
- Current raw-data limitation:
  - `tester_video_mapping.csv` supports video/project/tester joins
  - task-level tester assignment is not available from the current `*-assignments.csv` exports, so Step 2.2 should not assume a recoverable tester-to-task mapping
  - AAMI / Suncorp survey files are not present in the current local snapshot
- Output: summary tables and visualizations plus the following CSV exports in `outputs/`:
  - `step2_2_project_overview.csv`
  - `step2_2_tester_cross_project.csv`
  - `step2_2_task_type_distribution.csv`
  - `step2_2_tasks_with_timeguide_minutes.csv`
  - `step2_2_data_coverage.csv`
  - `step2_2_survey_project_summary.csv`
  - `step2_2_survey_question_types.csv`

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
- **Report**: `docs/eda_report.md`
- Consolidates findings from:
  - Step 2.1 — Transcript Data EDA (`notebooks/01_transcript_eda.ipynb`)
  - Step 2.2 — Structured Data EDA (`notebooks/02_structured_data_eda.ipynb`)
- Summarises key data quality issues, prototype cases, and implications for Layer 1 rule design
- Main report themes:
  - dataset coverage and development-sample scope
  - anomalous speech-rate case (`ghum_wa`)
  - low-confidence transcription patterns
  - duration deviation from Timeguide
  - sparse-narration prototype case (`terryaflint17_suncorp`)
  - cross-project structural observations and survey coverage
  - Layer 1 threshold outcomes (v2 applied 2026-04-22)
- Key findings:
  - `ghum_wa` shows an anomalously high average WPM (~220), which requires verification before use as a modelling signal
  - **5.6% of words** fall below confidence **0.5**; **12.0% of words** fall below **0.8** — `LOW_AUDIO_QUALITY` threshold raised from 0.7 → **0.75** (applied 2026-04-22)
  - `terryaflint17_suncorp` is the clearest sparse-narration prototype (`narration_density` = 0.233) — `SPARSE_NARRATION` threshold raised from 0.2 → **0.3** (applied 2026-04-22)
  - actual recording durations are shorter than Timeguide expectations (**mean duration ratio = 0.53**); 3 videos flagged as `DURATION_ANOMALY` (ratio < 0.3)
  - 18 testers appear across multiple projects; survey EDA covers UQ + Bupa only (AAMI/Suncorp survey files not present locally)
- Output: `docs/eda_report.md` — integrated markdown report for W7/W8 discussion and Layer 1 calibration reference

```python
# Usage
from pathlib import Path
report_path = Path("docs/eda_report.md")
print(report_path.read_text(encoding="utf-8")[:1000])  # preview first part of the report
```

## Step 3.1 — Layer 1 Rule-Based Detector
- **Module**: `src/layer1/rule_detector.py`
- Detects recording quality issues using hard-coded thresholds:

| Rule | Threshold | Flag |
|------|-----------|------|
| Video duration vs Timeguide | duration_ratio < 0.3 or > 3.0 | `DURATION_ANOMALY` |
| Silence ratio | silence_ratio > 0.6 | `EXCESSIVE_SILENCE` |
| Transcription confidence | avg_confidence < 0.75 | `LOW_AUDIO_QUALITY` |
| Narration density | narration_density < 0.3 | `SPARSE_NARRATION` |

- Each flag includes: video_filename, window_id, start_time, end_time, value
- Output: `data/processed/layer1_flags.csv` (278 flags across 15 dev-sample videos)
- Threshold recalibration: `LOW_AUDIO_QUALITY` raised from 0.7 → 0.75 and `SPARSE_NARRATION` from 0.2 → 0.3, per Step 3.2 recommendation. Flag count changed from 214 → 278 (+29 LOW_AUDIO_QUALITY, +35 SPARSE_NARRATION; EXCESSIVE_SILENCE and DURATION_ANOMALY unchanged).

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
- Validates Layer 1 on **6 development samples** through manual inspection, threshold review, and precision/recall analysis
- Threshold recalibration applied 2026-04-22: `LOW_AUDIO_QUALITY` raised 0.7 → **0.75**, `SPARSE_NARRATION` raised 0.2 → **0.3**; flag count changed from 214 → **278** across all 55 dev videos (+29 LOW_AUDIO_QUALITY, +35 SPARSE_NARRATION; EXCESSIVE_SILENCE and DURATION_ANOMALY unchanged)
- Rule assessment (v2 — post-recalibration):

| Rule | Threshold v1 | Threshold v2 | Verdict |
|------|-------------|-------------|---------|
| Video duration vs Timeguide | `duration_ratio < 0.3 or > 3.0` | `< 0.3 or > 3.0` | ✅ No change needed |
| Silence ratio | `silence_ratio > 0.6` | `> 0.6` | ✅ No change needed |
| Transcription confidence | `avg_confidence < 0.7` | `< 0.75` | ✅ Target achieved |
| Narration density | `narration_density < 0.2` | `< 0.3` | ✅ Target achieved |

- Threshold adjustment record:

| Flag | v1 threshold | v2 threshold | Status |
|------|-------------|-------------|--------|
| `DURATION_ANOMALY` | `< 0.3 or > 3.0` | `< 0.3 or > 3.0` | No change |
| `EXCESSIVE_SILENCE` | `> 0.6` | `> 0.6` | No change |
| `LOW_AUDIO_QUALITY` | `< 0.7` | `< 0.75` | ✅ Applied 2026-04-22 |
| `SPARSE_NARRATION` | `< 0.2` | `< 0.3` | ✅ Applied 2026-04-22 |

- Development samples:
  - `ghum_wa`
  - `reneerussell99_wa`
  - `terryaflint17_suncorp`
  - `carlpatrickrobinson_suncorp`
  - `ramazankawish_uq`
  - `jenniferparry7_uq`

- Validation summary (dev 6 samples, v2 thresholds, 95 total flags):

| Flag | v1 count | v2 count | Change | Notes |
|------|---:|---:|---:|---|
| `DURATION_ANOMALY` | 2 | 2 | — | `carlpatrickrobinson_suncorp` (0.144) + `jenniferparry7_uq` (0.159), both genuine short recordings |
| `EXCESSIVE_SILENCE` | 38 | 38 | — | All from `terryaflint17_suncorp` (mean silence_ratio 0.618) |
| `LOW_AUDIO_QUALITY` | 21 | 40 | +19 | `terryaflint17_suncorp` (28) + `jenniferparry7_uq` (9) + `ramazankawish_uq` (2) + `reneerussell99_wa` (1) |
| `SPARSE_NARRATION` | 5 | 15 | +10 | All from `terryaflint17_suncorp`; no new samples affected |
| **Total** | **66** | **95** | **+29** | |

- Precision / Recall analysis (Section 7 of notebook) — `DURATION_ANOMALY` and `EXCESSIVE_SILENCE` excluded (thresholds unchanged):

| Rule | Version | Precision | Recall | Change vs v1 |
|------|---------|----------:|-------:|---|
| `LOW_AUDIO_QUALITY` | v1 `< 0.70` | 1.000 | 0.525 | baseline |
| `LOW_AUDIO_QUALITY` | v2 `< 0.75` | 0.975 | 0.709 | precision −0.025; recall +0.184 |
| `SPARSE_NARRATION` | v1 `< 0.20` | 1.000 | 0.333 | baseline |
| `SPARSE_NARRATION` | v2 `< 0.30` | 1.000 | 0.395 | precision unchanged; recall +0.062 |

- Precision/Recall conclusion: precision did not drop substantially for either rule (LOW_AUDIO_QUALITY: −2.5%; SPARSE_NARRATION: unchanged). No threshold rollback or further adjustment recommended. One marginal FP noted in `LOW_AUDIO_QUALITY` (`ramazankawish_uq_w061`, confidence=0.721) — isolated spike in otherwise high-confidence sample (mean=0.934).

- Output:
  - updated sample-level validation notebook (v2) with precision/recall analysis
  - manual rule assessment with v1/v2 comparison
  - threshold adjustment record (applied to `src/layer1/rule_detector.py`)

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
- `data/processed/layer2_cluster_assignments.csv`（876 行 × 7 列，R3 4.3 join key）
- `data/processed/layer2_cluster_summary.csv`（每簇一行，raw feature mean/std，ddof=0）
- `data/processed/layer2_cluster_composition.csv`（long-form：algorithm × cluster_id × dimension × value × count）
- `outputs/figures/layer2_{silhouette,kdist,pca,tsne}.png`（gitignored，二进制图）

**边界声明：** fixed L1 v1 thresholds + 6 dev sample exploratory；DBSCAN 仅对照不进下游 join；若 cluster 结构被单一 tester 主导（当前观察值：`tester_name = terryaflint17`），唯一后续动作 = 扩样 + 第二轮 4.2，不在当前样本做剔除实验。高级算法（HDBSCAN / GMM / Spectral）属于 Future Work。

### Round-2 Diagnostic (2026-04-22)

Round-2 is diagnostic only; it does **not** update `layer2_cluster_assignments.csv` / `primary_cluster_id`. Artifacts live in `data/processed/layer2_round2_*.csv` and notebook cells 10–17.

- **KMeans k sweep (k=2-5)**: `k=2` max silhouette (0.504) but one cluster still 95.6% single-tester; `k=3/4/5` mean max tester share climbs 0.84 -> 0.88 -> 0.91.
- **DBSCAN grid**: `eps=0.8` keeps 97-100% tester dominance in non-noise clusters; `eps>=1.0` collapses to a single cluster. Tuning eps does not produce interpretable quality groups.
- **Tester specificity ratio**: `silence_ratio` / `narration_density` = 9.71 (mirror features, 1-x), `words_per_minute` = 3.01. PC1 explains 55% variance, dominated by silence/narration/confidence/unique-word axes - i.e., the principal axis encodes tester identity, not window quality.
- **Leave-one-tester-out**: holding out `terryaflint17` drops k=2 silhouette 0.50 -> 0.39; holding out `ghum` raises k=3 silhouette 0.42 -> 0.54. 6-tester sample is structurally unstable.

**Decision**: round-1 parameters (`final_k=3, min_samples=7, eps=0.8`) remain the current default. Round-3 parameter re-tune is deferred until sample expansion (more tester x project coverage via Step 8.1 batch pipeline). Downstream (R3 Step 4.3) should treat current clusters as exploratory tester-dominated evidence, not as quality labels.

## Step 4.3 - R3 Cluster Interpretation Preparation
- **Document**: `docs/cluster_interpretation.md`
- **Data files**: `data/annotations/r3_window_review_sample.csv`, `data/annotations/window_semantic_labels_template_canonical.csv`
- Reviews sampled 60-second transcript windows and records early semantic patterns for later Layer 2 cluster interpretation.
- Uses the client taxonomy from `docs/friction_taxonomy.md`, based on `Friction & Sentiment Classification Framework.pdf`.
- Uses Round 5 canonical annotation fields from `src/layer3/schemas_a.py` and `src/layer3/schemas_b.py`; the older `window_semantic_labels_template.csv` is retained only as a legacy template.
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

## Step 5.1 - Prompt Design (Round 5 canonical)
- **Modules**: `src/layer3/schemas_a.py` + `prompts_a.py` (5.1-A finding-level) / `schemas_b.py` + `prompts_b.py` (5.1-B video-level)
- **Documents**: `docs/friction_taxonomy.md`, `docs/prompt_design.md` (semantic definitions only; schema source-of-truth lives in pydantic models)
- Defines two prompt tracks for LLM-based classification:
  - **5.1-A** emits a list of findings per window (F1-F7 / S1-S6 / E1-E5 / L1-L5 per finding, with `observed_signal` / `stated_signal` / `signal_alignment` + optional `structural_amplification_note`).
  - **5.1-B** emits one video-level assessment (`narration_quality` / `recording_quality` / `coaching_evidence`).
- Modules build chat-style prompt messages only; they do not call an LLM API.
- Output labels align with the SMP canonical frameworks (F1-F7 friction, S1-S6 severity, E1-E5 sentiment, L1-L5 calibrator score).
- Field definitions, enums, and null discipline are documented in the `schemas_*.py` module docstrings — treat those as the single source of truth.

```python
# Usage (5.1-A finding-level)
import sys; sys.path.insert(0, 'src')
from layer3.prompts_a import build_messages

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
- **Legacy setup script**: `scripts/create_r3_manual_annotation_round1.py`
- **Canonical migration script**: `scripts/migrate_r3_annotations_to_canonical.py`
- **Inputs**: `data/annotations/r3_window_review_sample.csv`, `data/annotations/r3_manual_annotations_round1.csv`
- **Canonical outputs**: `data/annotations/r3_manual_annotations_round1_canonical.csv`, `data/annotations/window_semantic_labels_template_canonical.csv`
- The original 14-window first-round R3 file (`r3_manual_annotations_round1.csv`) is retained as a historical input and is no longer the Round 5 evaluation source.
- `scripts/migrate_r3_annotations_to_canonical.py` migrates reusable fields from the legacy R3 file and fills the canonical-only fields required by `src/layer3/schemas_a.py` and `src/layer3/schemas_b.py`.
- `r3_manual_annotations_round1_canonical.csv` matches the field order of `r8_manual_annotations_round1.csv`, so Step 5.4 can compare R3 and R8 labels directly.
- `window_semantic_labels_template_canonical.csv` is a header-only template for future Round 5 annotation work; the older `window_semantic_labels_template.csv` is retained only as a legacy template.

| File | Audience | Purpose | Round 5 evaluation source |
|------|----------|---------|--------------------------|
| `r3_manual_annotations_round1.csv` | R3 / Nix review | Legacy R3 round-1 annotation input | No |
| `r3_manual_annotations_round1_canonical.csv` | R3 / R8 / Nix | R3 canonical annotation output with 14 completed rows | Yes |
| `round1_blind_for_r8.csv` | R8 independent annotation | Context-only blind sample | No |
| `r8_manual_annotations_round1.csv` | R8 / Nix | R8 canonical annotation output | Yes |
| `window_semantic_labels_template_canonical.csv` | Future annotators | Empty canonical annotation template | No |

```powershell
# Legacy setup (already completed)
python scripts\create_r3_manual_annotation_round1.py

# Canonical migration / regeneration
python scripts\migrate_r3_annotations_to_canonical.py
```

### R8 Manual Annotation Set + Kappa Agreement Check
- **Script / Notebook:** `scripts/annotate_r8_round1_updated.py`, `notebooks/04_kappa_agreement.ipynb`
- **Inputs:** `docs/friction_taxonomy.md`, `docs/prompt_design.md`, `data/annotations/round1_blind_for_r8.csv`, `data/annotations/r3_manual_annotations_round1_canonical.csv`
- **Outputs:** `data/annotations/r8_manual_annotations_round1.csv`, agreement tables, and Cohen's kappa per dimension
- Creates the R8 independent first-round manual annotation file for the same 14-window sample used in Step 5.3, using the Round 5 canonical schema.
- Uses the field definitions from `docs/friction_taxonomy.md` and `docs/prompt_design.md` to guide manual annotation.
- Keeps the annotation process blind by using `round1_blind_for_r8.csv`, which does not contain R3 labels.
- The annotation script does **not** read `data/annotations/r3_manual_annotations_round1.csv`, `docs/cluster_interpretation.md`, or `docs/case_studies.md` during annotation.
- Fields align with Round 5 canonical schema from `src/layer3/schemas_a.py` and `src/layer3/schemas_b.py`:
  - **5.1-A finding-level:** `finding`, `observed_signal`, `stated_signal`, `signal_alignment`, `friction_type` (F1–F7 / none / unclear), `severity_s` (S1–S6 / none / unclear), `sentiment_e` (E1–E5 / null), `calibrator_score_l` (L1–L5), `rationale`, `structural_amplification_note`
  - **5.1-B video-level:** `narration_quality`, `recording_quality`, `coaching_evidence`
  - **Other:** `annotated`, `confidence`, `notes`, `annotator`
- Tracks annotation completion via explicit `annotated` flag to correctly handle no-friction windows where `finding` is legitimately blank.
- Compares `r3_manual_annotations_round1_canonical.csv` and `r8_manual_annotations_round1.csv` on the shared 14-window sample using `window_id`.
- Reports Cohen's kappa for all Round 5 canonical dimensions:
  - **5.1-A:** `friction_type`, `severity_s` (nominal + linear weighted), `sentiment_e`, `calibrator_score_l` (nominal + linear weighted), `signal_alignment`
  - **5.1-B:** `narration_quality`, `recording_quality`, `coaching_evidence`
- Produces cross-tab agreement tables, disagreement `window_id` lists per dimension, and supporting field presence audit.
- Eval discipline:
  - `sentiment_e = E3` (neutral expressed) is not equal to null (no verbal expression)
  - `calibrator_score_l` is audit signal only; not merged with `severity_s`
  - E3 excluded from aggregate sentiment per client framework but retained in distribution stats

| File | Audience | Purpose |
|---|---|---|
| `r3_manual_annotations_round1_canonical.csv` | R3 canonical annotation | Completed Round 5 schema output for the 14-window sample |
| `r8_manual_annotations_round1.csv` | R8 independent annotation | Blind manual annotation output (Round 5 schema) |
| `04_kappa_agreement.ipynb` | Team / review | Agreement calculation and disagreement inspection |

### Kappa Agreement Results Summary

Round 5 canonical Kappa computed 2026-04-22 using `r3_manual_annotations_round1_canonical.csv` + `r8_manual_annotations_round1.csv` (14 shared windows):

| Schema | Dimension | Kappa | Level |
|---|---|---|---|
| 5.1-A | `friction_type` | **0.8293** | Almost perfect |
| 5.1-A | `severity_s` (nominal) | **0.3378** | Fair |
| 5.1-A | `severity_s` (weighted) | **0.6056** | Substantial |
| 5.1-A | `sentiment_e` | **0.2222** | Fair |
| 5.1-A | `calibrator_score_l` (nominal) | **0.8971** | Almost perfect |
| 5.1-A | `calibrator_score_l` (weighted) | **0.9271** | Almost perfect |
| 5.1-A | `signal_alignment` | N/A | 100% agree (single class) |
| 5.1-B | `narration_quality` | **0.5882** | Moderate |
| 5.1-B | `recording_quality` | 0.0 (92.9% agree) | Class imbalance |
| 5.1-B | `coaching_evidence` | N/A | 100% agree (single class) |

Key observations:
- `friction_type` and `calibrator_score_l` show almost perfect agreement
- `severity_s` nominal kappa is fair (0.34) but weighted kappa is substantial (0.61) — all disagreements are between adjacent levels
- `sentiment_e` kappa is fair (0.22); 6 of 8 disagreements are at the E3/E4 boundary — joint calibration session recommended before Step 5.4 final evaluation
- `signal_alignment`, `coaching_evidence`: all 14 windows labelled identically by both annotators; kappa undefined (single class)
- `recording_quality` kappa = 0.0 due to class imbalance (13/14 = `good`); observed agreement is 92.9%

Previous results (old schema, for reference only — not comparable to Round 5):
- `friction_type` kappa = **0.6606**
- `severity` kappa = **0.3869** (simplified label)
- `sentiment` kappa = **0.6640** (simplified label)
- weighted `severity` kappa = **0.6038**

```python
# Usage
python scripts\annotate_r8_round1_updated.py
# Then open and run:
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
- Step 5.4 agreement evaluation still needs to be recomputed using `data/annotations/r3_manual_annotations_round1_canonical.csv` and `data/annotations/r8_manual_annotations_round1.csv`.
- Step 8.3 should be revised once final cluster assignments, LLM outputs, and agreement results are available.

- Task context has not yet been automatically joined into each annotation row.
- Step 8.3 will need updates after team-level annotation, clustering, and classification results are complete.
