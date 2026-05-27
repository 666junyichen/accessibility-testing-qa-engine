# Intelligent Tester Quality Assessment & Coaching Engine

Internal decision-support prototype for See Me Please tester-submission review.
The system turns AWS Transcribe outputs into transcript windows, quality flags,
LLM friction findings, per-video quality reports, coaching recommendations,
tester-performance tables, and a Streamlit review demo.

**Final technical status (2026-05-20):** dev55 is stable, the corrected Bupa
21-video held-out evaluation is complete, and final verification passed
`pytest` (155 tests), `sync_dev55.py --check` (55/55), performance-table
regeneration, and Bupa report readability / ID-alignment checks. Bupa outputs
are evaluation-only and must not be used for post-hoc tuning.

## Data Source
AWS S3 bucket: `usyd-03-2025-cs20-1-proj-assets`

## Environment
Python 3.10+

## Setup
```bash
pip install -r requirements.txt
```

## Functional Coverage
- Dev pipeline: 57 generated reports, with 55 official `dev55` reports after
  excluding two transcription-failure edge cases.
- Bupa held-out: 21 transcripts, 1,252 windows, 813 filtered L3 findings,
  21 reports, 21 R6 performance rows, zero failed reports.
- Demo: `app/streamlit_demo.py` reads precomputed dev55 artifacts.
- Held-out evidence: reproducible Bupa outputs live under `data/heldout/bupa/`;
  governance and evaluation synthesis live in `docs/eval_freeze.md` and
  `docs/evaluation_design.md`.

## Contents
- [Step 0.1 - Repository and Environment Setup](#step-01---repository-and-environment-setup)
- [Step 0.2 - AWS Transcribe Export Collection](#step-02---aws-transcribe-export-collection)
- [Step 0.3 - Structured Raw Data Preparation](#step-03---structured-raw-data-preparation)
- [Step 0.4 - End-to-End Data Flow](#step-04---end-to-end-data-flow)
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
- [Step 5.2 - Layer 3 LLM Classification and Postprocessing](#step-52---layer-3-llm-classification-and-postprocessing)
- [Step 5.3 - R3 Manual Annotation Set](#step-53---r3-manual-annotation-set)
- [Step 5.4 - LLM Kappa](#step-54--llm-kappa)
- [Step 6.1 - Fusion and QualityReport Generation](#step-61--fusion-and-qualityreport-generation)
- [Step 6.2 — Coaching Recommendation Engine](#step-62--coaching-recommendation-engine)
- [Step 6.3 — Performance Tracking](#step-63--performance-tracking)
- [Step 7.1 - Pipeline Orchestration](#step-71--pipeline-orchestration-fusion-runner)
- [Step 7.2 - Streamlit Demostration Interface](#step-72--streamlit-demonstration-interface)
- [Step 8.1 - Dev55 Batch Run](#step-81---dev55-batch-run)
- [Step 8.2 — Layer Ablation Study](#step-82--layer-ablation-study)
- [Step 8.3 - R3 Case Studies](#step-83---r3-case-studies)
- [How to reproduce from scratch](#how-to-reproduce-from-scratch)

## Step 0.1 - Repository and Environment Setup
- **Status**: completed
- **Purpose**: give new contributors a stable local layout before modelling work starts.
- **Python**: `3.10+`
- **Dependency file**: `requirements.txt`

| Path | Role |
|---|---|
| `data/raw/` | Local raw exports from the client sandbox / S3 snapshot, including structured CSVs and AWS Transcribe JSON. |
| `data/processed/` | Reproducible CSV / JSON artifacts consumed by Layer 1, Layer 2, Layer 3, fusion, performance tracking, and reports. |
| `src/` | Core Python modules for parsing, preprocessing, rule detection, clustering, LLM postprocessing, fusion, coaching, and tracking. |
| `scripts/` | CLI-style orchestration helpers for Layer 3, postprocessing, pipeline reports, ablation, dev55 sync, and performance outputs. |
| `docs/` | Governance notes, design docs, ablation findings, case studies, prompt notes, freeze rules, and Step 8.1 scope records. |
| `app/` | Streamlit demo that reads precomputed `dev55` report artifacts. |
| `tests/` | Unit and regression tests for preprocessing, Layer 2 utilities, fusion, coaching, and performance tracking. |

Raw client inputs stay under `data/raw/`. Downstream modules read reproducible
artifacts from `data/processed/`. Large generated files should be regenerated
from scripts where possible rather than manually edited.

### Data reality and scope

The data scope follows the current repository README and the governance mirror
in `docs/eval_freeze.md`. Canonical label and scoring references are:

| Reference | Purpose |
|---|---|
| `client/s3_snapshot/06-friction-sentiment-framework.md` | Canonical friction, severity, and sentiment label framework. |
| `client/s3_snapshot/07-friction-score-calibrator-prompt.md` | Canonical calibrator score prompt and `L1`-`L5` score language. |
| Katie scoring-reference materials | Client-side scoring and evaluation language used for final report alignment. |

Current project coverage:

| Project | Local raw status | Transcribe status | Survey status | Current role |
|---|---|---:|---|---|
| DPC-WA (`department-of-premier-and-cabinet-wa`) | Collated project, assignment, and task CSVs | 17 JSON outputs | No local survey CSVs | Dev source; 16 official `dev55` reports after excluding one transcription failure. |
| AAMI / Suncorp (`suncorp-insurance`) | Collated project, assignment, and task CSVs | 21 JSON outputs | No local survey CSVs | Dev source; 20 official `dev55` reports after excluding one transcription failure. |
| UQ (`the-university-of-queensland`) | Collated project, assignment, task, and survey CSVs | 19 JSON outputs | 4 survey CSVs present | Dev source; 19 official `dev55` reports. |
| Bupa (`web-health-information-bupa`) | Held-out inputs and transcript JSONs under `data/heldout/bupa/` | 21 JSON outputs | 4 survey CSVs present | Corrected full held-out evaluation completed on 21 collated videos. |
| Brighton | Raw-only package outside current local repo snapshot | Not run | Not available locally | Not included because collated metadata / survey / task alignment is unavailable. |

Evaluation split from `docs/eval_freeze.md`:

| Split | Contents | Size | Rationale |
|---|---|---:|---|
| Development set | Old 3 collated projects: AAMI 21 + UQ 19 + DPC-WA 17, with 2 transcription failures excluded for formal reporting | 55 videos | Prompt tuning, schema finalisation, manual Kappa checks, ablation, rotating validation, and demo reports. |
| Held-out set | Bupa collated videos | 21 videos | Completed as one-time post-freeze evaluation after Gate 1 and Gate 2 approval. |
| Not included | Brighton raw package and Bupa raw package | Brighton raw 105 + Bupa raw 315 noted in governance docs | Excluded because raw-only assets cannot be aligned reliably to collated tasks / survey / reporting scope. |

## Step 0.2 - AWS Transcribe Export Collection
- **Status**: completed for the three development projects and the corrected Bupa held-out run.
- **Input source**: S3 collated MP4 assets for the development projects.
- **Local JSON path**: `data/raw/transcribe-output/`
- **Parser**: `src/data/transcript_parser.py`

AWS Transcribe converts collated MP4 recordings into JSON outputs. The relevant
downstream payload is under `results`:

| AWS Transcribe field | Meaning in this project |
|---|---|
| `results.transcripts` | Full transcript text for each video. |
| `results.items` | Word-level and punctuation-level items with `start_time`, `end_time`, and confidence values for pronunciation tokens. |
| `results.audio_segments` | Segment-level transcript spans used to build `segments.csv` and later 60-second windows. |

The JSON preserves word-level confidence and second-based timestamps. The current
pipeline stores these timestamps as numeric seconds, so downstream windowing and
duration logic can operate at sub-second precision.

Current development transcribe coverage:

| Project | JSON count under `data/raw/transcribe-output/` |
|---|---:|
| `department-of-premier-and-cabinet-wa` | 17 |
| `suncorp-insurance` | 21 |
| `the-university-of-queensland` | 19 |
| **Total generated development JSONs** | **57** |

Two development outputs are retained as abnormal transcription cases rather than
silently deleted:

| Video ID | Project | Handling |
|---|---|---|
| `troyparnell_suncorp` | AAMI / Suncorp | Retained as a near-empty / failed transcript edge case, excluded from formal `dev55`. |
| `thanoptions_wa` | DPC-WA | Retained as a sparse / failed transcript edge case, excluded from formal `dev55`. |

This is why the repo can contain `57` generated reports while the official
development reporting scope is `55`.

## Step 0.3 - Structured Raw Data Preparation
- **Status**: completed with source-data limitations documented.
- **Primary local path**: `data/raw/`

Structured data currently available in the repository:

| Path / file group | Current contents | Use |
|---|---|---|
| `data/raw/organisations-data.csv` | Organisation-level structured export | Organisation reference and project context. |
| `data/raw/tester_db.csv` | Tester roster / profile export | Tester reference, with caution around restricted or unclear attributes. |
| `data/raw/schema-research.sql` | Database schema reference | Helps interpret CSV fields and likely source relationships. |
| `data/raw/department-of-premier-and-cabinet-wa/` | Project CSV, assignment CSV, 14 task rows | DPC-WA dev structured context. |
| `data/raw/suncorp-insurance/` | Project CSV, assignment CSV, 11 task rows | AAMI / Suncorp dev structured context. |
| `data/raw/the-university-of-queensland/` | Project CSV, assignment CSV, 10 task rows, 4 survey CSVs | UQ dev structured and survey context. |
| `data/raw/bupa-uk/` | 4 survey CSVs: 580 answers, 43 questions, 20 responses, survey metadata | Survey context for the Bupa held-out evaluation; processed held-out videos and transcripts are stored under `data/heldout/bupa/`. |
| `data/raw/tester_video_mapping.csv` | Local mapping helper | Practical bridge for video filename, project, and tester identity where recoverable. |

Known structured-data limitation:

- The current `*-assignments.csv` files contain useful roster fields such as tester name, opt-in status, and cohort information.
- They do not provide a reliable tester-to-task linkage in the current local snapshot.
- Therefore `assignment_id`, `task_id`, and `task_title` should not be treated as fully recoverable ground truth.
- Task context is useful for project-level interpretation, but task-level joins should remain documented as incomplete unless a richer export is provided later.

The structured-data review used this snapshot to inspect project coverage,
tester participation, task distributions, Timeguide fields, actual-duration vs
expected-duration behavior, and survey availability.

## Step 0.4 - End-to-End Data Flow
- **Status**: documented for W10 Step 9.2-A.
- **Purpose**: show how raw data becomes model-ready artifacts, fused reports, performance tables, and demo outputs.

High-level flow:

```text
S3 collated MP4 / sandbox CSV
  -> AWS Transcribe JSON + structured raw CSVs
  -> transcript_parser.py
  -> transcripts.csv / items.csv / segments.csv
  -> window_splitter.py
  -> windows.csv
  -> audio_features.py + video_metadata.py
  -> audio_features.csv / video_metadata.csv
  -> Layer 1 rule detector
  -> layer1_flags.csv
  -> Layer 2 feature engineering + clustering
  -> feature matrices + cluster assignments
  -> Layer 3 Bedrock LLM classification + postprocessing
  -> layer3_findings_filtered.csv + layer3_video_assessments.csv
  -> fusion pipeline
  -> data/processed/reports/*.json + _summary.csv
  -> dev55 filtering / sync
  -> data/processed/reports/dev55/ + _summary_dev55.csv
  -> R6 performance tracking
  -> per_submission.csv + per_tester.csv
  -> Streamlit demo / final report evidence
```

Current processed artifact inventory:

| Stage | Artifact | Current rows / files | Purpose |
|---|---|---:|---|
| Transcript parser | `data/processed/transcripts.csv` | 57 rows | One full transcript row per generated development video. |
| Transcript parser | `data/processed/segments.csv` | 26,191 rows | Segment-level transcript spans from `results.audio_segments`. |
| Transcript parser | `data/processed/items.csv` | Regenerable, gitignored intermediate | Word-level timing and confidence table from `results.items`; used when rebuilding windows from raw transcripts. |
| Windowing | `data/processed/windows.csv` | 3,331 rows | Approximately 60-second analysis windows across 57 videos. |
| Audio features | `data/processed/audio_features.csv` | 876 rows | Window-level silence, narration density, words-per-minute, confidence, and silence duration features. |
| Video metadata | `data/processed/video_metadata.csv` | 15 rows | Sample video metadata and duration-ratio checks. |
| Layer 1 | `data/processed/layer1_flags.csv` | 278 rows | Rule-based quality flags such as `LOW_AUDIO_QUALITY`, `SPARSE_NARRATION`, and `DURATION_ANOMALY`. |
| Layer 2 | `data/processed/feature_matrix_raw.csv` | 876 rows | Raw L2 feature matrix. |
| Layer 2 | `data/processed/feature_matrix_scaled.csv` | 876 rows | Scaled L2 feature matrix. |
| Layer 2 | `data/processed/layer2_cluster_assignments.csv` | 876 rows | Window-level cluster labels. |
| Layer 2 | `data/processed/layer2_cluster_summary.csv` | 6 rows | Cluster-level feature summaries. |
| Layer 2 | `data/processed/layer2_cluster_composition.csv` | 47 rows | Cluster composition by tester and project. |
| Layer 3 | `data/processed/layer3_findings.csv` | 2,219 rows | Raw flattened L3 finding outputs after Bedrock classification. |
| Layer 3 | `data/processed/layer3_findings_filtered.csv` | 2,133 rows | Filtered L3 findings used by fusion. |
| Layer 3 | `data/processed/layer3_video_assessments.csv` | 57 rows | Video-level narration, recording, and coaching-evidence assessment. |
| Fusion / reports | `data/processed/reports/*.json` | 57 files | One QualityReport JSON per generated development video. |
| Fusion / reports | `data/processed/reports/_summary.csv` | 57 rows | Batch-level report summary, including the two abnormal transcript cases. |
| Step 8.1 scope | `data/processed/reports/dev55_official_list.csv` | 55 rows | Official development whitelist. |
| Step 8.1 scope | `data/processed/reports/_summary_dev55.csv` | 55 rows | Official filtered report summary. |
| Step 8.1 scope | `data/processed/reports/dev55/*.json` | 55 files | Physical whitelist subset of current main reports. |
| R6 performance | `data/processed/performance/per_submission.csv` | Generated by Step 6.3 script | Per-video score, tier, caps, findings, and quality dimensions. |
| R6 performance | `data/processed/performance/per_tester.csv` | Generated by Step 6.3 script | Per-tester aggregate score, trajectory sketch, and persistent friction types. |

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
- **Review artifact**: transcript EDA summary retained in this README; extended
  report-support material is archived outside the runtime repository.
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
- Uses processed transcript/audio tables such as `windows.csv`, `segments.csv`,
  regenerable `items.csv`, and `audio_features.csv`. `data/processed/items.csv`
  is intentionally gitignored because it is a large intermediate artifact.
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
- **Review artifact**: structured-data EDA summary retained in this README;
  extended report-support material is archived outside the runtime repository.
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
- **Summary location**: this README and `docs/layer1_design.md`
- Consolidates findings from:
  - Step 2.1 — Transcript Data EDA
  - Step 2.2 — Structured Data EDA
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
- Output: integrated README summary plus Layer 1 calibration rationale in
  `docs/layer1_design.md`.

```python
# Usage
from pathlib import Path
report_path = Path("docs/layer1_design.md")
print(report_path.read_text(encoding="utf-8")[:1000])  # preview first part of the report
```

## Step 3.1 — Layer 1 Rule-Based Detector
- **Module**: `src/layer1/rule_detector.py`
- **Design rationale**: see [`docs/layer1_design.md`](docs/layer1_design.md) for feature provenance, threshold derivation, and the fusion-cap contract.
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
- **Validation record**: threshold outcomes are summarised below and in
  `docs/layer1_design.md`.
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
  - optional local imputation log (gitignored; per-column nan_count / nan_rate / filled)
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
#   optional local imputation log
```

## Step 4.2 — Layer 2 Clustering

Runs exploratory KMeans and DBSCAN clustering over 876 60-second windows in a
seven-feature standardized space.

**Inputs:** `data/processed/feature_matrix_scaled.csv` for model fitting and
`data/processed/feature_matrix_raw.csv` for cluster summaries.

**Module:** `src/layer2/cluster_utils.py` provides `fit_kmeans`, `fit_dbscan`,
`build_cluster_summary`, and `pca_project`.

**Orchestration:** `scripts/run_layer2_clustering.py`

**Algorithm configuration:**
- KMeans: `k in {2,3,4,5}`, `n_init=10`, `random_state=42`; silhouette,
  elbow, and cluster-size checks informed the selected `final_k`.
- DBSCAN: `min_samples in {7,14}` and k-distance review were used during
  exploration; the retained baseline is `min_samples=7`, `eps=0.8`.
- `primary_cluster_id = kmeans_cluster_id`.
- Round 1 retained the heuristic baseline (`final_k=3`, `min_samples=7`,
  `eps=0.8`) so downstream joins remain stable.

**Outputs:**
- `data/processed/layer2_cluster_assignments.csv` (876 rows x 7 columns,
  consumed by Step 4.3 joins)
- `data/processed/layer2_cluster_summary.csv` (one row per cluster, raw feature
  mean/std with `ddof=0`)
- `data/processed/layer2_cluster_composition.csv` (long form:
  `algorithm x cluster_id x dimension x value x count`)

**Boundary statement:** Layer 2 clustering is exploratory evidence, not a
quality label. DBSCAN is retained for comparison only and does not drive
downstream joins. If clusters are dominated by a single tester, the correct
response is sample expansion rather than exclusion experiments on the current
small sample. HDBSCAN, GMM, and spectral clustering remain future work.

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
- Uses the client taxonomy through `docs/l3_design.md`, based on `Friction & Sentiment Classification Framework.pdf`.
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
- **Document**: `docs/l3_design.md` (unified Layer 3 design reference; schema source-of-truth lives in pydantic models)
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

## Step 5.2 - Layer 3 LLM Classification and Postprocessing
- **Module**: `src/layer3/llm_classifier.py`
- **Runner**: `scripts/run_layer3_dev.py`
- **Postprocess CLI**: `scripts/postprocess_layer3.py`
- **Filter CLI**: `scripts/filter_l3_ok_contamination.py`
- **Inputs**:
  - `data/processed/windows.csv`
  - `src/layer3/prompts_a.py` / `src/layer3/prompts_b.py`
  - `src/layer3/schemas_a.py` / `src/layer3/schemas_b.py`
- **Outputs**:
  - `data/processed/layer3_findings.csv` (2,219 raw flattened findings)
  - `data/processed/layer3_findings_filtered.csv` (2,133 production findings)
  - `data/processed/layer3_video_assessments.csv` (57 video-level assessments)

Step 5.2 invokes AWS Bedrock with the canonical 5.1-A / 5.1-B prompts, repairs
and validates JSON through Pydantic schemas, checkpoints raw results under
`outputs/`, then flattens accepted rows into reproducible CSV artifacts. The
filtered finding table is the L3 evidence consumed by fusion, coaching, R6
performance tracking, ablation, case studies, and Bupa held-out reporting.

```powershell
# Dry-run request construction
python scripts\run_layer3_dev.py --level A --input data/processed/windows.csv --limit 3 --dry-run
python scripts\run_layer3_dev.py --level B --input data/processed/windows.csv --limit 3 --dry-run

# Postprocess raw model outputs after an approved run
python scripts\postprocess_layer3.py --level A
python scripts\postprocess_layer3.py --level B
python scripts\filter_l3_ok_contamination.py
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
| `r3_manual_annotations_round1.csv` | Initial reviewer / lead review | Legacy R3 round-1 annotation input | No |
| `r3_manual_annotations_round1_canonical.csv` | Primary reviewer / independent reviewer / lead review | R3 canonical annotation output with 14 completed rows | Yes |
| `round1_blind_for_r8.csv` | R8 independent annotation | Context-only blind sample | No |
| `r8_manual_annotations_round1.csv` | Independent reviewer / lead review | R8 canonical annotation output | Yes |
| `window_semantic_labels_template_canonical.csv` | Future annotators | Empty canonical annotation template | No |

```powershell
# Legacy setup (already completed)
python scripts\create_r3_manual_annotation_round1.py

# Canonical migration / regeneration
python scripts\migrate_r3_annotations_to_canonical.py
```

### R8 Manual Annotation Set + Kappa Agreement Check
- **Script / summary:** `scripts/annotate_r8_round1_updated.py`,
  `docs/evaluation_design.md`
- **Inputs:** `docs/l3_design.md`, `data/annotations/round1_blind_for_r8.csv`, `data/annotations/r3_manual_annotations_round1_canonical.csv`
- **Outputs:** `data/annotations/r8_manual_annotations_round1.csv`, agreement tables, and Cohen's kappa per dimension
- Creates the R8 independent first-round manual annotation file for the same 14-window sample used in Step 5.3, using the Round 5 canonical schema.
- Uses the field definitions and boundary rules from `docs/l3_design.md` to guide manual annotation.
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
| `docs/evaluation_design.md` | Team / review | Agreement calculation, disagreement inspection, and confidence-propagation summary |

> **Methodology, full Kappa tables, and downstream confidence-propagation rules are documented in [`docs/evaluation_design.md`](docs/evaluation_design.md) (§3.2 dimension grouping, §3.3 LC-1 to LC-4 rules, §7 Step 5.4 evaluation).** This README section covers the operational artefacts only.

```python
# Usage
python scripts\annotate_r8_round1_updated.py
# Then review the committed evaluation summary:
docs\evaluation_design.md
```

## Step 5.4 — LLM Kappa
- **Summary**: `docs/evaluation_design.md`
- **Inputs:**
  - `data/processed/layer3_findings_filtered.csv` (2,133 findings, pseudo-positives removed)
  - `data/processed/layer3_video_assessments.csv` (57 videos, 5.1-B video-level labels)
  - `data/annotations/r8_manual_annotations_round1.csv` (14 windows, R8 round-1 human annotations)
- **Join strategy**: join on `window_id`; 10 of 14 windows have LLM findings; 4 no-finding windows treated as `friction_type='none'`; multi-finding windows resolved by highest `calibrator_score_l` (ties: first occurrence)
- **Decision gate**: `friction_type` κ ≥ 0.5 → V2 prompt acceptable, no V3 revision needed
- **Verdict (2026-04-25)**: `friction_type` κ = **0.7407** (Substantial) — gate passed, V2 retained.

> **Full result tables (LLM V2 vs R8 across all 8 dimensions), R3 vs R8 reference comparison, error pattern analysis, and confidence-propagation rules are in [`docs/evaluation_design.md`](docs/evaluation_design.md) §3.2 + §7.**

```python
# Usage - Step 5.4 LLM Kappa
# Inputs required:
#   data/processed/layer3_findings_filtered.csv
#   data/processed/layer3_video_assessments.csv
#   data/annotations/r8_manual_annotations_round1.csv

# Committed result summary:
docs\evaluation_design.md
```


## Step 6.1 — Fusion and QualityReport Generation
- **Module**: `src/pipeline/fusion.py`
- **Schema**: `src/pipeline/schemas.py`
- **Tests**: `tests/test_fusion.py`
- **Batch runner**: `scripts/run_pipeline.py`
- **Inputs**:
  - `data/processed/windows.csv`
  - `data/processed/layer1_flags.csv`
  - `data/processed/layer2_cluster_assignments.csv`
  - `data/processed/layer3_findings_filtered.csv`
  - `data/processed/layer3_video_assessments.csv`
- **Outputs**:
  - `data/processed/reports/*.json`
  - `data/processed/reports/_summary.csv`
  - `data/processed/reports/dev55/*.json`
  - `data/processed/reports/_summary_dev55.csv`

Step 6.1 binds the three-layer evidence stack into one `QualityReport` per
video. L1 contributes rule flags, L2 contributes exploratory cluster context,
L3 contributes finding distributions and video-level assessment, and the fusion
rule computes the final `good` / `acceptable` / `poor` tier. The module also
passes finding-level evidence into the coaching engine so severity and
friction-aggregation recommendations are included in the report JSON.

```powershell
python scripts\run_pipeline.py --all --output-dir data/processed/reports
python scripts\sync_dev55.py --check
```

## Step 6.2 — Coaching Recommendation Engine
- **Module**: `src/coaching/recommendation_engine.py`
- **Tests**: `tests/test_recommendation_engine.py` (26 tests covering MVP, severity-aware, friction-aggregation, meta, suppression, and edge cases)
- **Templates**: `docs/coaching_templates.md`
- **Inputs**:
  - one `VideoAssessment` row from 5.1-B (`narration_quality` / `recording_quality` / `coaching_evidence`)
  - optional 5.1-A finding-level records (`severity_s`, representative finding text)
- **Output**: zero or more `Recommendation` objects, each with `category`, `title`, `summary`, ordered `advice[]`, integer `priority`, optional `evidence_note`, and `tags[]`.

  The V3.1 engine additionally supports:
  - severity-aware recommendation routing
  - representative finding evidence injection
  - finding-level priority escalation
  - friction-type aggregation across multi-pattern submissions
  - meta recommendations that combine sparse narration and weak recording

### Trigger logic (MVP, template-based)
- **Narration templates** keyed off `narration_quality` (`none` / `sparse` / `adequate` / `rich`) — produce coaching focused on think-aloud density and framing language
- **Recording templates** keyed off `recording_quality` (`poor` / `acceptable` / `good`) — produce coaching on audio capture, mic placement, ambient noise
- **Moderation templates** keyed off `coaching_evidence` (`explicit` / `none`, two-valued per Round 11) — flag explicit moderator intervention so review teams can spot tester guidance leakage

### V3.1 Finding-aware Extension
The V3.1 extension consumes Step 5.1-A finding-level outputs and introduces severity-aware and friction-aggregation orchestration.

#### Severity routing
- `S1` / `S2`
  - generate high-priority coaching recommendations
  - prioritise task-blocking or near-blocking friction
- `S3` / `S4`
  - generate targeted severity coaching
  - preserve standard narration / recording / moderation recommendations
- `S5` / `S6`
  - treated as low-priority evidence
  - may be omitted or merged in future aggregation stages

#### Representative finding evidence
The recommendation engine now summarises:
- finding-level severity distribution
- representative findings
These are surfaced through `evidence_note` to provide more grounded coaching context.

#### Backward compatibility
The original session-level API remains unchanged:
```python
engine.generate(assessment)
```

### Boundaries
- The current engine is deterministic and template-based. It does not generate free-form coaching with an LLM at report time.
- Timestamp-aware recommendation synthesis remains future work; report consumers should use finding timestamps directly for detailed review.
- **No coupling to R6 calibrator-mismatch flag**: per W9 P1#8b lock-in, coaching priority is **not** auto-bumped from R6 audit signals; R5 and R6 stay decoupled by hard constraint.

## Result on dev 57
Across 57 reports, V3.1 produces more differentiated coaching behaviour through
severity-aware recommendations, friction-aggregation, and meta suppression.
High-severity findings (`S1` / `S2`) generate elevated priority and inject
representative findings into `evidence_note`; mixed-friction sessions receive
one aggregation item when they pass the distribution guards. The extension
preserves backward compatibility with the original session-level API while
enabling grounded coaching from 5.1-A evidence.

## Step 6.3 — Performance Tracking
- **Module**: `src/tracking/performance_model.py`
- **Tests**: `tests/test_performance_model.py` (33 tests)
- **Script**: `scripts/build_performance_tracking.py`
- **Document**: `docs/performance_tracking.md`
- **Inputs**:
  - `data/processed/layer3_findings_filtered.csv` (5.1-A finding-level rows)
  - `data/processed/layer3_video_assessments.csv` (5.1-B video-level rows)
  - Optional auxiliaries: `data/processed/windows.csv` (`total_windows`), `data/processed/layer1_flags.csv` (`duration_anomaly`)
- **Outputs**:
  - `data/processed/performance/per_submission.csv` (57 rows — per-video score / tier / cap reasoning)
  - `data/processed/performance/per_tester.csv` (27 rows — per-tester aggregate, trajectory, persistent friction)

### SMP alignment principle
R6 adopts SMP **score language** — 0–100 scale, four-tier output (Foundational / Developing / Proficient / Leading), cap-based severity rules. R6 does **not** reproduce SMP Model B, does not own product-accessibility scoring, and does not inject any SMP cohort weighting into the scoring chain. R6 produces *tester-performance-dimension aggregation*; Model B remains the SMP-side product scorer. Mapping to the four SMP design docs (`01-scoring-model-success-criteria.md` / `02-scoring-model-comparison-A-B-C-D.md` / `03-scoring-model-assessment-ABDC2.md` / `04-model-E-reworked-cap-based.md`) is documented section-by-section in `docs/performance_tracking.md` §2.

### Per-submission scoring

Three named dimension scores feed a weighted composite, then severity caps bind:

| Dimension | Source | Weight | Lookup / formula |
|---|---|---:|---|
| D1 — Narration Substantiveness | `narration_quality` | 0.50 | rich=90, adequate=75, sparse=55, none=25 |
| D2 — Friction-Surfacing Quality | findings density + alignment + mid-high severity share | 0.35 | `60 + 20·clamp(density/0.6) + 10·aligned_share + 10·mid_high_share` |
| D3 — Recording Usability | `recording_quality` (+ `duration_anomaly` cap to 60) | 0.15 | good=90, acceptable=70, poor=40 |

Severity caps (Model E style — applied after raw composite, minimum cap binds):

| Trigger | Cap |
|---|---:|
| Any S1 finding present | ≤ 55 |
| ≥2 S2 findings | ≤ 65 |
| `narration_quality == 'none'` AND no findings | ≤ 40 |
| `recording_quality == 'poor'` | ≤ 70 |

Tier mapping:

| Score range | Tier |
|---|---|
| 85–100 | Leading |
| 70–84 | Proficient |
| 55–69 | Developing |
| 0–54 | Foundational |

`calibrator_score_l` (L1–L5) is audit-only per Step 6.1 main/auxiliary discipline — never enters score or cap. `sentiment_e` is surfaced as a per-tester facet, not as a score input (E3 excluded from aggregate per `06`).

### Per-tester trajectory
For each tester with ≥2 non-low-evidence submissions:
- ordered by `(project, video_id)` (placeholder until real submission timestamps land — `ordering_basis` field documents this)
- `direction ∈ {improving, stable, declining}` from `delta = score[last] − score[first]` with ±5 stable band
- `persistent_friction_types` = friction types appearing in top-3 across ≥2 submissions
- `cross_check_lane ∈ {with_overrides, raw_only, dev_only}` per Katie's UQ note (UQ has no Model C3 overrides, so AAMI/Bupa vs UQ must bucket separately)
- `low_evidence` (total_windows < 5) records are emitted in per-submission CSV but excluded from trajectory slope (protects against single noisy submissions swinging direction)

### Result summary

| Layer | Distribution |
|---|---|
| Per-submission tier | Leading 23 · Proficient 5 · Developing 27 · Foundational 2 |
| Cap binding rate | 29 / 57 submissions (51%) — caps doing the work the design intends |
| Per-tester tier | Leading 7 · Proficient 8 · Developing 11 · Foundational 1 (n=27 dev testers) |
| Trajectory direction | improving 3 · stable 7 · declining 8 (n=18 testers with ≥2 scored submissions) |

Worked example — `Sharelinsonny_suncorp`: D1=90, D2=83.7, D3=70 → raw=84.8; ≥2 S2 cap binds → final 65.0 / Developing. The cap-based shape is binding here, exactly as Model E intends.

### Boundaries
- W9 deliverable was design + reference module + per-tester sketch on dev 57. Freeze 4 sign-off was later completed through `docs/eval_freeze.md` Gate 2.
- Bupa R6 mapping has now been generated for the 21-video held-out set as an evaluation-only artefact. The Bupa outputs must not be used to tune R6 rules, caps, thresholds, or coaching logic.

```python

# Reads:
#   data/processed/layer3_findings_filtered.csv
#   data/processed/layer3_video_assessments.csv

# Writes:
#   data/processed/performance/per_submission.csv
#   data/processed/performance/per_tester.csv
```

```python

from src.tracking.performance_model import (
    score_submissions_from_csv, build_per_tester_table,
)

records = score_submissions_from_csv(
    findings_csv="data/processed/layer3_findings_filtered.csv",
    assessments_csv="data/processed/layer3_video_assessments.csv",
    windows_csv="data/processed/windows.csv",
    layer1_flags_csv="data/processed/layer1_flags.csv",
)
trajectories = build_per_tester_table(records)
```

## Step 7.1 — Pipeline Orchestration (Fusion Runner)

- **Script**: `scripts/run_pipeline.py`
- **Tests**: `tests/test_run_pipeline.py`

Implements the orchestration layer that integrates outputs from Layer 1, Layer 2, and Layer 3 and generates final video-level Quality Reports.

### Functionality
- Loads processed CSV inputs from `data/processed/`:
  - `windows.csv`
  - `layer1_flags.csv`
  - `layer2_cluster_assignments.csv`
  - `layer3_findings_filtered.csv`
  - `layer3_video_assessments.csv`
- Collects all available `video_id`s across datasets
- For each video:
  - Filters relevant rows
  - Calls `fuse_video(...)` from `src/pipeline/fusion.py`
  - Writes one JSON report per video

### Output
- Per-video reports:
  - `data/processed/reports/{video_id}.json`
- Summary file:
  - `data/processed/reports/_summary.csv`

### CLI Usage

```bash
# Run for a single video
PYTHONPATH=. python scripts/run_pipeline.py --video <video_filename>

# Run for all videos
PYTHONPATH=. python scripts/run_pipeline.py --all

# Specify output directory
PYTHONPATH=. python scripts/run_pipeline.py --all --output-dir data/processed/reports
```

## Step 7.2 — Streamlit Demonstration Interface

### Overview

In this step, a lightweight Streamlit-based demonstration interface was implemented to visualise the outputs of the end-to-end pipeline. The purpose of this component is to provide a simple reviewer-facing interface that allows users to explore Quality Reports without re-running the full pipeline.

The demo integrates both:
- The **summary-level overview** (`_summary_dev55.csv`)
- The **detailed per-video Quality Report JSON files**

This aligns with the project objective of supporting internal reviewers in efficiently assessing tester submissions.

### Data Sources

The demo reads from the following pre-generated outputs:

- `data/processed/reports/dev55/`  
  → 55 per-video **Quality Report JSON files**

- `data/processed/reports/_summary_dev55.csv`  
  → Aggregated summary table (one row per video)

The demo operates on the **dev55 official dataset**, excluding transcription-failed videos, to ensure consistency with Step 8.1 evaluation scope.

### Key Features

#### 1. Video Selection

Users can select a specific video via a sidebar dropdown. Each selection loads:
- Corresponding row from `_summary_dev55.csv`
- Corresponding detailed JSON report

#### 2. Summary Overview Panel

Displays high-level information extracted from the summary CSV:

- `video_id`
- `tester`
- `project`
- `quality tier`
- `number of L3 findings`
- `reason for classification`

This provides a quick overview of the tester’s performance.

#### 3. Detailed Quality Report

Displays structured outputs from the pipeline:

- **Basic Information**
  - Total windows
  - Duration

- **Layer 1 (Rule-based)**
  - Flags and anomalies

- **Layer 2 (Clustering)**
  - Coverage and cluster distribution

- **Layer 3 (LLM Classification)**
  - Findings distribution (F1–F7, S1–S6, E1–E5)
  - Top findings

- **Video-level Assessment**
  - Narration quality
  - Recording quality
  - Coaching evidence

- **Overall Assessment**
  - Quality tier
  - Reasoning

#### 4. Coaching Recommendations

Displays generated coaching suggestions, including:

- Category (e.g., recording)
- Summary
- Actionable advice
- Trigger conditions

#### 5. Raw JSON Viewer

A collapsible section allows full inspection of the original JSON output for transparency and debugging.

#### Design Rationale

- **Separation of concerns**:  
  The demo reads precomputed outputs instead of invoking the pipeline, ensuring fast and stable interaction.

- **Consistency with evaluation scope**:  
  Only dev55 data is used to match Step 8.1 and avoid inconsistencies caused by failed transcripts.

- **Reviewer-oriented design**:  
  Combines summary-level scanning with deep inspection of individual reports.

### How to Run

From the project root directory:

```bash
streamlit run app/streamlit_demo.py
```

## Step 8.1 - Dev55 Batch Run

- **Status**: completed as a dev-batch reporting close-out
- **Entrypoint**: `scripts/run_pipeline.py`
- Existing batch run produced:
  - `data/processed/reports/*.json`
  - `data/processed/reports/_summary.csv` (`57` rows)
- Official `Step 8.1` reporting scope is the governance-defined `dev55`, not all `57` generated rows
- Official scope files:
  - `data/processed/reports/dev55_official_list.csv`
  - `data/processed/reports/_summary_dev55.csv`
  - `data/processed/reports/dev55/` (`55` official JSON reports)
- Excluded from the formal `dev55` set:
  - `troyparnell_suncorp`
  - `thanoptions_wa`
- Basis for exclusion:
  - `docs/eval_freeze.md` defines the dev set as `57` total with `2` transcription failures, yielding `55` official videos
  - `README.md` already documents `troyparnell` as a retained transcript-failure / near-empty edge case
  - both excluded rows have near-empty outputs in the current batch artifacts
- This Step 8.1 close-out uses existing processed CSV/JSON artifacts only; it does not introduce new API calls or held-out evaluation

## Step 8.2 — Layer Ablation Study
- **Script**: `scripts/ablation_study.py`
- **Document**: `docs/ablation_study.md`
- **Output**: `data/processed/ablation_summary.csv` (220 rows = 55 dev55 videos × 4 configurations)
- **Scope**: 55 official dev55 videos by default; `--full-57` flag retained as edge-case sensitivity run
- **Configurations**: `Full` (production baseline) / `No-L1` (empty `l1_flags`) / `No-L2` (empty `l2_assignments`) / `No-L3` (empty findings + neutral assessment default `{narration: rich, recording: good, coaching_evidence: none}`)

### Method
`scripts/ablation_study.py` reuses `load_inputs()` and the per-video filter helpers from `scripts/run_pipeline.py` (R7 orchestrator) so input-loading semantics match production exactly, then replays `fuse_video()` under each configuration. For each (video, configuration) pair we record final `quality_tier`, `reasoning` string, mean L1 flag count, and mean L3 finding count. Tier deltas are computed against the `Full` baseline.

### Headline result
| Configuration | good | acceptable | poor |
|---|---:|---:|---:|
| Full | 0 | 15 | 40 |
| No-L1 | 0 | 15 | 40 |
| No-L2 | 0 | 15 | 40 |
| No-L3 | 55 | 0 | 0 |

L3 is the binding signal under the current fusion rules — without finding-level evidence, every dev55 video collapses to the neutral default. L1 and L2 contribute supporting context but do not flip the tier on this dataset; the §4.2 ablation document soft-frames this as "current fusion tier decision is L3-dependent under this counterfactual" rather than as a permanent architectural claim, since L1/L2 may bind on different distributions (e.g. Bupa held-out).

### Boundaries
- Counterfactual is **input ablation** at the fusion layer, not retraining. The 5.2 LLM classifier is not re-run.
- Edge-case 57-video run is reported only as sensitivity, not as the headline number — see `docs/step8_1_dev55_scope.md` for scope rationale.

## Step 8.3 - R3 Case Studies
- **Document**: `docs/case_studies.md`
- Uses selected video-level MVP reports from `data/processed/reports/` to write qualitative case studies for accessibility, missing information, comprehension, confidence, excessive-effort, recording-quality, and coaching issues.
- Current case studies cover 5 selected videos (`ghum_uq`, `margieflint_wa`, `giuliaclemente26_wa`, `jenniferparry7_uq`, `mgblackwell2001_suncorp`) across different tiers and trigger reasons.
- Each case cites `quality_tier` + reason, L1 flags, L3 finding summaries (`friction_type`, `severity_s`, `sentiment_e`, `calibrator_score_l`), and coaching recommendations from the corresponding JSON report.
- The original 4 window-level examples are retained inside `docs/case_studies.md` as supporting qualitative evidence rather than standalone case studies.

| Case study focus | Related evidence source | Taxonomy link |
|------------------|-------------------------|---------------|
| Accessibility or assistive technology barrier | Video report top findings + retained window evidence | F3 |
| Missing or hidden pathway | Video-level L3 finding summaries + user narration | F6 |
| Readability or comprehension problem | Retained window evidence + L3 findings | F1 |
| Confidence or trust uncertainty | Video report top findings and stated/observed signals | F2 |
| High cognitive or process effort | Video report top findings and qualitative notes | F7 |
| Recording or narration quality risk | 5.1-B video-level assessment + coaching recommendations | Session quality |


## R3 Current Limitations
- Layer 2 clustering remains exploratory and tester-dominated, so Step 8.3 uses it only as supporting context rather than as a final quality label.
- Step 8.3 is now aligned with the MVP video-level reports, but the selected cases should still be spot-checked before final client-facing submission.
- Recording-poor dev55 sessions such as `mgblackwell2001_suncorp` should be used to demonstrate evidence-quality caution, not as strong product conclusions.
- Case wording should remain aligned with Step 5.4 agreement findings as the progress report is finalised.

## How to reproduce from scratch

The target smoke-test outcome is that a new contributor can reach the existing
development report state within about one hour once AWS SSO, S3, Bedrock, and
local video/audio prerequisites are available. The Bupa held-out evaluation has
already been completed after budget approval and freeze-gate sign-off; reruns
should be treated as verification/reproduction only and must not be used for
post-hoc tuning.

### 1. Clone, environment, and AWS identity

```powershell
git clone https://github.com/seemeplease/usyd-03-2025-cs20-1.git
cd usyd-03-2025-cs20-1
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
aws sso login --profile smp-cs20
aws sts get-caller-identity --profile smp-cs20
```

### 2. Prepare raw data and transcript tables

```powershell
New-Item -ItemType Directory -Force data\raw\transcribe-output
aws s3 sync s3://usyd-03-2025-cs20-1-proj-assets/transcribe-output/ data/raw/transcribe-output/ --profile smp-cs20
python src/data/transcript_parser.py
python src/preprocessing/window_splitter.py
python src/preprocessing/audio_features.py
python src/preprocessing/video_metadata.py
```

Expected transcript/preprocessing checkpoints:

```powershell
(Import-Csv data/processed/transcripts.csv).Count
(Import-Csv data/processed/segments.csv).Count
(Import-Csv data/processed/windows.csv).Count
(Import-Csv data/processed/audio_features.csv).Count
```

Expected current values are `57`, `26191`, `3331`, and `876` respectively,
assuming the same development transcribe JSON and local video/audio availability.

### 3. Run Layer 1 and Layer 2 artifacts

```powershell
python src/layer1/rule_detector.py
python src/layer2/feature_engineering.py
python scripts/run_layer2_clustering.py
```

Expected current processed outputs:

```powershell
(Import-Csv data/processed/layer1_flags.csv).Count
(Import-Csv data/processed/feature_matrix_raw.csv).Count
(Import-Csv data/processed/feature_matrix_scaled.csv).Count
(Import-Csv data/processed/layer2_cluster_assignments.csv).Count
```

Expected current values are `278`, `876`, `876`, and `876`.

### 4. Run Layer 3 with Bedrock

Layer 3 uses AWS Bedrock LLM calls. Before running the non-dry-run commands,
confirm that the AWS use-case form / Bedrock model access has been approved for
the `smp-cs20` profile. To test the wiring without cost:

```powershell
python scripts/run_layer3_dev.py --level A --input data/processed/windows.csv --limit 3 --dry-run
python scripts/run_layer3_dev.py --level B --input data/processed/windows.csv --limit 3 --dry-run
```

Full development run:

```powershell
python scripts/run_layer3_dev.py --level A --input data/processed/windows.csv --output outputs/layer3_dev_level_A_results.csv --checkpoint outputs/layer3_dev_level_A_checkpoint.csv --max-concurrency 4
python scripts/run_layer3_dev.py --level B --input data/processed/windows.csv --output outputs/layer3_dev_level_B_results.csv --checkpoint outputs/layer3_dev_level_B_checkpoint.csv --max-concurrency 2
python scripts/postprocess_layer3.py --level A --input outputs/layer3_dev_level_A_results.csv --output data/processed/layer3_findings.csv
python scripts/postprocess_layer3.py --level B --input outputs/layer3_dev_level_B_results.csv --output data/processed/layer3_video_assessments.csv
python scripts/filter_l3_ok_contamination.py
```

Expected current Layer 3 checkpoints:

```powershell
(Import-Csv data/processed/layer3_findings.csv).Count
(Import-Csv data/processed/layer3_findings_filtered.csv).Count
(Import-Csv data/processed/layer3_video_assessments.csv).Count
```

Expected current values are `2219`, `2133`, and `57`.

### 5. Build reports, dev55 subset, and performance tables

```powershell
python scripts/run_pipeline.py --all --output-dir data/processed/reports
python scripts/sync_dev55.py --check
python scripts/build_performance_tracking.py
```

Expected final checkpoints:

```powershell
Get-ChildItem data/processed/reports -Filter *.json | Measure-Object
(Import-Csv data/processed/reports/_summary.csv).Count
Get-ChildItem data/processed/reports/dev55 -Filter *.json | Measure-Object
(Import-Csv data/processed/reports/_summary_dev55.csv).Count
(Import-Csv data/processed/performance/per_submission.csv).Count
(Import-Csv data/processed/performance/per_tester.csv).Count
```

Expected report state:

| Output | Expected result |
|---|---:|
| `data/processed/reports/*.json` | 57 files |
| `data/processed/reports/_summary.csv` | 57 rows |
| `data/processed/reports/dev55/*.json` | 55 files |
| `data/processed/reports/_summary_dev55.csv` | 55 rows |
| `data/processed/performance/per_submission.csv` | 57 rows |
| `data/processed/performance/per_tester.csv` | 27 rows |

### 6. Optional local review surfaces

```powershell
pytest
python scripts/ablation_study.py --scope dev55 --output data/processed/ablation_summary.csv
streamlit run app/streamlit_demo.py
```

Use `data/processed/reports/_summary.csv` for the full generated development
batch, and `data/processed/reports/_summary_dev55.csv` for formal dev-set
reporting, demo, and final-report evidence.
