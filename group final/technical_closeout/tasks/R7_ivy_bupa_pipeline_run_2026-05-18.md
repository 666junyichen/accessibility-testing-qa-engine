# R7 Ivy Task Brief - Bupa Frozen Pipeline Run

Date: 2026-05-18

## Goal

Run the frozen pipeline on the full Bupa held-out set and verify that the existing dev55 demo still works.

This is the next blocking technical closeout task.

## Current Input Status

- Bupa scope: 21 collated videos.
- Manifest: `data/heldout/bupa/processed/manifest.csv`.
- Transcript status: 21/21 success.
- Transcript JSON folder: `data/heldout/bupa/raw/transcribe-output/web-health-information-bupa/`.
- R4 sanity status: clear, 0 hard blockers.
- R6 lane/key status: clear, no pre-inference R6 fix required.
- Required processed project key: `web-health-information-bupa`.

Do not exclude `manyi_tan`. It is now processable and should only be treated as a short-sample caveat.

## Hard Rules

Do not tune or modify frozen model/rule surfaces using Bupa:

- L3 prompts or few-shot examples
- 5.x schemas
- Layer 1 thresholds
- Layer 2 parameters
- 6.1 fusion rules
- R6 scoring logic
- postprocess filters
- coaching logic

All Bupa weaknesses should be recorded as caveats or future work, not fixed by changing the frozen pipeline.

## Output Isolation

Use only Bupa-specific output roots:

- processed CSVs: `data/heldout/bupa/processed/`
- L3 raw/checkpoint outputs: `outputs/heldout/bupa/`
- QualityReport JSON: `data/heldout/bupa/reports/`
- performance handoff: `data/heldout/bupa/performance/`

Do not write Bupa outputs to:

- `data/processed/`
- `data/processed/reports/`
- `data/processed/performance/`
- `outputs/layer3_dev_*`

## Implementation Cautions

1. Do not run `src/data/transcript_parser.py` blindly on Bupa JSON files.
   - Its current metadata extraction is dev-format oriented.
   - Bupa filenames such as `allenabegum123__web-health-information-bupa__transcript.json` need manifest-aware parsing.

2. Full Layer 1 regeneration needs Bupa MP4/VTT access.
   - Manifest S3 paths are available.
   - If MP4/VTT are not local, download or mount them through isolated held-out paths.
   - If any L1/audio/video artifact cannot be regenerated, document exactly what is missing. Do not substitute dev values.

3. Real L3 inference must use the frozen AWS/Bedrock classifier.
   - Dry-run output is not valid held-out evaluation output.
   - Record commands and output paths because this is the official only-once held-out run.

4. Every processed Bupa row must use:

   `project=web-health-information-bupa`

   Do not use `project=bupa-uk`.

## Required Artifacts

Generate or verify:

- `data/heldout/bupa/processed/windows.csv`
- `data/heldout/bupa/processed/layer1_flags.csv`
- `data/heldout/bupa/processed/layer2_cluster_assignments.csv` if required by the report step; otherwise document if empty/audit-only
- `data/heldout/bupa/processed/layer3_findings.csv`
- `data/heldout/bupa/processed/layer3_findings_filtered.csv`
- `data/heldout/bupa/processed/layer3_video_assessments.csv`
- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/reports/_summary.csv`

Final report generation should use explicit Bupa paths, for example:

```bash
PYTHONPATH=. python scripts/run_pipeline.py \
  --all \
  --processed-dir data/heldout/bupa/processed \
  --output-dir data/heldout/bupa/reports
```

## Required Checks

Before finishing, verify:

- expected videos: 21
- successful reports
- failed reports and failure reasons
- `_summary.csv` exists
- report JSON files are readable
- processed `project` is `web-health-information-bupa`
- Bupa outputs did not overwrite dev paths
- dev55 Streamlit demo still opens
- dev55 demo views work:
  - Single Video
  - Tester Trajectory
  - Cohort Overview

## Output Note

Submit a markdown note to:

`group final/technical_closeout/submissions/R7_ivy_bupa_pipeline_demo_2026-05-18.md`

If the local `group final` folder is not available, either commit the note under the repository path above or send the markdown file directly to Nix.

Include:

- exact commands used
- generated output paths
- expected videos
- successful reports
- failed reports and reasons
- project-key verification result
- path-isolation verification result
- dev55 demo check result
- blockers, if any

## Completion Criteria

R7 is complete when:

- Bupa reports and `_summary.csv` exist, or failures are documented clearly;
- all Bupa outputs are path-isolated;
- exact commands are recorded;
- dev55 demo sanity check is complete;
- downstream R6/R3/R5/R8 can start.
