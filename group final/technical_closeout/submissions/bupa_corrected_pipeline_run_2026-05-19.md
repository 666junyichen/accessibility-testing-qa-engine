# Bupa Corrected Pipeline Run Closeout

Date: 2026-05-19

## Scope

- Held-out project: `web-health-information-bupa`
- Expected videos: `21`
- Transcript JSON files: `21`
- Transcript parse failures: `0`
- Hard input blockers: `0`
- Evaluation boundary: Bupa was used for evaluation only. No prompts, schemas, thresholds, filters, scoring logic, coaching logic, or tier boundaries were tuned using Bupa outputs.

## Correction Applied Before Run

The earlier Bupa first run produced readable reports, but its `windows.csv` was built by a separate fixed-window path and missed required fields such as `duration`. That made report `_summary.csv` show `duration_s=0`.

The preprocessing script was corrected before this official run:

- `scripts/build_bupa_processed_inputs.py` now reads the Bupa manifest explicitly.
- Processed `video_id` values preserve manifest IDs such as `tester__web-health-information-bupa`.
- The script reuses the frozen dev windowing implementation from `src/preprocessing/window_splitter.py`.
- Generated windows now include expected report fields such as `duration`, `word_count`, `segment_ids`, and `video_filename`.

## Commands Run

### Build held-out processed inputs

```bash
python scripts/build_bupa_processed_inputs.py \
  --manifest data/heldout/bupa/processed/manifest.csv \
  --transcript-dir data/heldout/bupa/raw/transcribe-output/web-health-information-bupa \
  --output-dir data/heldout/bupa/processed
```

Result:

- transcripts: `21`
- items: `204981`
- segments: `10194`
- windows: `1252`

### Run Layer 3 video-level inference

```bash
PYTHONPATH=. python scripts/run_layer3_dev.py \
  --level B \
  --input data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_video_assessments_raw.csv \
  --checkpoint outputs/heldout/bupa/layer3_B_checkpoint.csv \
  --max-concurrency 2
```

Result:

- videos succeeded: `21/21`
- schema errors: `0`
- json errors: `0`
- api errors: `0`
- estimated cost: `$0.06265925`

### Run Layer 3 window-level inference

```bash
PYTHONPATH=. python scripts/run_layer3_dev.py \
  --level A \
  --input data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_findings.csv \
  --checkpoint outputs/heldout/bupa/layer3_A_checkpoint.csv \
  --max-concurrency 4
```

Result:

- windows succeeded: `1252/1252`
- schema errors: `0`
- json errors: `0`
- api errors: `0`
- estimated cost: `$1.37485225`

### Postprocess Layer 3 findings

```bash
PYTHONPATH=. python scripts/postprocess_layer3.py \
  --level A \
  --input data/heldout/bupa/processed/layer3_findings.csv \
  --windows data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_findings_filtered.csv
```

Result:

- filtered finding rows: `813`
- failed rows skipped: `0`

### Postprocess Layer 3 video assessments

```bash
PYTHONPATH=. python scripts/postprocess_layer3.py \
  --level B \
  --input data/heldout/bupa/processed/layer3_video_assessments_raw.csv \
  --windows data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_video_assessments.csv
```

Result:

- video assessment rows: `21`
- failed rows skipped: `0`

### Generate reports

```bash
PYTHONPATH=. python scripts/run_pipeline.py \
  --all \
  --processed-dir data/heldout/bupa/processed \
  --output-dir data/heldout/bupa/reports
```

Result:

- successful reports: `21`
- failed reports: `0`

## Output Paths

- `data/heldout/bupa/processed/items.csv`
- `data/heldout/bupa/processed/segments.csv`
- `data/heldout/bupa/processed/transcripts.csv`
- `data/heldout/bupa/processed/windows.csv`
- `data/heldout/bupa/processed/layer3_findings.csv`
- `data/heldout/bupa/processed/layer3_findings_filtered.csv`
- `data/heldout/bupa/processed/layer3_video_assessments_raw.csv`
- `data/heldout/bupa/processed/layer3_video_assessments.csv`
- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/reports/_summary.csv`

Checkpoint files were written under `outputs/heldout/bupa/`, but `outputs/` is not part of the committed held-out deliverable.

## Final Verification

Verification after cleanup:

```text
summary_rows 21
reports_json 21
bad_reports []
id_diff_summary_reports [] []
id_diff_manifest_reports [] []
project_reports ['web-health-information-bupa']
duration_zero_summary 0
tier Counter({'acceptable': 14, 'poor': 7})
l1_total Counter({'0': 21})
l2_coverage Counter({'0.0': 21})
```

## Layer 1 / Layer 2 Caveat

The corrected Bupa run did not regenerate:

- `data/heldout/bupa/processed/layer1_flags.csv`
- `data/heldout/bupa/processed/layer2_cluster_assignments.csv`

Report generation completed successfully without these files, but the final Bupa reports therefore show:

- `l1_flags=0`
- `l2_coverage=0.0`

No dev-set Layer 1 or Layer 2 artifacts were reused. This should be reported as a held-out evaluation limitation, not treated as a tuning target.

## Final Status

The corrected Bupa held-out pipeline run is complete and ready for downstream evaluation work:

- R6 performance/scoring outputs
- R3 case study review
- R5 coaching recommendation review
- R8 held-out evaluation summary
