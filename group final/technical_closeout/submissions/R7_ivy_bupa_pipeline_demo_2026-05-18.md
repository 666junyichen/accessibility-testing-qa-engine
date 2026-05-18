# R7 Ivy Bupa Pipeline Demo Closeout

Date: 2026-05-18

# Goal

Run the frozen pipeline on the Bupa held-out dataset using isolated held-out paths and verify that the existing dev55 Streamlit demo still functions correctly.


# Dataset Scope

- Held-out project: `web-health-information-bupa`
- Expected videos: `21`
- Transcript status: `21/21 success`

Manifest used:

```text
data/heldout/bupa/processed/manifest.csv
```

Processed project key verified as:

```text
web-health-information-bupa
```

`manyi_tan_bupa` was included successfully and was not excluded from the held-out run.


# Commands Used

## Build held-out processed inputs

```bash
python scripts/build_bupa_processed_inputs.py
```

## Run Layer 3 video-level inference (Level B)

```bash
PYTHONPATH=. python scripts/run_layer3_dev.py \
  --level B \
  --input data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_video_assessments.csv \
  --checkpoint outputs/heldout/bupa/layer3_B_checkpoint.json
```

## Run Layer 3 window-level inference (Level A)

```bash
PYTHONPATH=. python scripts/run_layer3_dev.py \
  --level A \
  --input data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_findings.csv \
  --checkpoint outputs/heldout/bupa/layer3_A_checkpoint.json
```

## Postprocess Layer 3 findings

```bash
PYTHONPATH=. python scripts/postprocess_layer3.py \
  --level A \
  --input data/heldout/bupa/processed/layer3_findings.csv \
  --windows data/heldout/bupa/processed/windows.csv \
  --output data/heldout/bupa/processed/layer3_findings_filtered.csv
```

## Postprocess Layer 3 video assessments

```bash
PYTHONPATH=. python scripts/postprocess_layer3.py \
  --level B \
  --input data/heldout/bupa/processed/layer3_video_assessments.csv \
  --output data/heldout/bupa/processed/layer3_video_assessments_processed.csv
```

## Run held-out report generation

```bash
PYTHONPATH=. python scripts/run_pipeline.py \
  --all \
  --processed-dir data/heldout/bupa/processed \
  --output-dir data/heldout/bupa/reports
```

---

# Generated Output Paths

## Processed CSVs

- `data/heldout/bupa/processed/windows.csv`
- `data/heldout/bupa/processed/layer3_findings.csv`
- `data/heldout/bupa/processed/layer3_findings_filtered.csv`
- `data/heldout/bupa/processed/layer3_video_assessments.csv`

## Layer 3 checkpoints

- `outputs/heldout/bupa/layer3_A_checkpoint.json`
- `outputs/heldout/bupa/layer3_B_checkpoint.json`

## Final reports

- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/reports/_summary.csv`

# Report Generation Result

## Successful reports

- Expected reports: `21`
- Successful reports: `21`
- Failed reports: `0`

Final pipeline summary:

```text
INFO: Done. success=21 failed=0
```

Generated reports were verified as readable JSON outputs.

`data/heldout/bupa/reports/_summary.csv` was also generated successfully.

# Layer 1 / Layer 2 Status

The following held-out artifacts were not regenerated during this run:

- `data/heldout/bupa/processed/layer1_flags.csv`
- `data/heldout/bupa/processed/layer2_cluster_assignments.csv`

Current report generation completed successfully without these files.

The generated held-out JSON reports remained structurally readable with expected report content and summary fields.

Pipeline output therefore contains:

- `l1_flags=0`
- `l2_rows=0`

## Reason

Full Layer 1 regeneration requires held-out MP4/VTT asset access.

`layer2_cluster_assignments.csv` was not regenerated because current report generation completed successfully without Layer 2 held-out artifacts.

The file remains optional/audit-only for this run.

No dev-set Layer 1 or Layer 2 artifacts were reused.

# Frozen Pipeline Verification

Real AWS/Bedrock Layer 3 inference was used during the held-out run.

No frozen prompts, schemas, thresholds, fusion rules, postprocess filters, coaching logic, or scoring logic were modified during the held-out evaluation.

No dry-run outputs were used.

# Path Isolation Verification

Verified:

- All Bupa outputs remained inside held-out paths.
- No files were written into:
- `data/processed/`
- `data/processed/reports/`
- `data/processed/performance/`
- `outputs/layer3_dev_*`

Held-out path isolation requirement passed successfully.

# Dev55 Demo Verification

Streamlit demo sanity check completed using:

```bash
streamlit run app/streamlit_demo.py
```

Verified working:

- Single Video view
- Tester Trajectory view
- Cohort Overview view

The Bupa held-out pipeline run did not break the existing dev55 demo workflow.

# Caveats / Notes

- `manyi_tan_bupa` remains a short-sample caveat but was processed successfully.
- Some held-out reports were generated without Layer 1 / Layer 2 held-out artifacts due to unavailable MP4/VTT regeneration assets.
- All current outputs were generated using held-out-specific paths only.

# Final Status

R7 held-out pipeline closeout completed successfully.

Downstream teams can now proceed with:

- R6 scoring
- R3 analysis
- R5 evaluation
- R8 review
