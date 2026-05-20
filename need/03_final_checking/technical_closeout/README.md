# Technical Closeout - Bupa Held-out Run

Date: 2026-05-20

## Current Status

The project technical closeout is complete. The corrected official Bupa held-out pipeline run, supporting technical review summary, evaluation summary, and final verification checks have all been completed.

Bupa scope is fixed at 21 collated videos. The earlier 42 count was 21 MP4 files plus 21 VTT sidecars.

Current input readiness:

- Manifest rows: 21.
- Transcript JSON files: 21 present.
- Transcript parse failures: 0.
- Transcript validation failures: 0.
- Hard input blockers: 0.
- `manyi_tan` is now processable after the S3 key correction in commit `91a95cb`.

Current lane/key status:

- Processed Bupa project key must be `web-health-information-bupa`.
- `web-health-information-bupa` maps to R6 `cross_check_lane=with_overrides`.
- `bupa-uk` is only a source/S3 folder alias. It must not be used as the processed `project` value because it falls back to `dev_only`.

Corrected run status:

- An earlier first Bupa run on 2026-05-18 produced 21/21 reports.
- Review found that the first generated `windows.csv` did not use the frozen dev windowing logic and lacked required columns such as `duration`.
- `scripts/build_bupa_processed_inputs.py` was corrected to use manifest-aware metadata and the frozen `src/preprocessing/window_splitter.py` logic.
- The corrected official run was executed on 2026-05-19.
- Corrected preprocessing generated 21 transcripts, 204981 items, 10194 segments, and 1252 windows.
- Corrected Layer 3 Level B succeeded for 21/21 videos with 0 schema/json/api errors.
- Corrected Layer 3 Level A succeeded for 1252/1252 windows with 0 schema/json/api errors.
- Corrected report generation produced 21/21 reports with 0 failed reports.
- Corrected report summary has no zero-duration videos.
- Old first-run `*_bupa.json` reports were removed; final report filenames now use the manifest video IDs.

## Freeze Boundary

Bupa is evaluation only. Do not use Bupa outputs to tune:

- L3 prompts or few-shot examples
- 5.x schemas
- Layer 1 thresholds
- Layer 2 parameters or interpretation
- 6.1 fusion rules
- R6 scoring weights, caps, lanes, or tier boundaries
- postprocess filters
- coaching logic

Any weakness found on Bupa should be recorded as a limitation or future-work item.

## Run Record

Clean final handoff index:

`FINAL_TECHNICAL_HANDOFF.md`

Primary corrected run record:

`evidence/bupa_corrected_pipeline_run_2026-05-19.md`

Data preparation provenance:

`evidence/R1_youwei_bupa_data_preparation.md`

Supporting review summary:

`evidence/bupa_supporting_review_summary_2026-05-20.md`

Final Bupa evaluation summary:

`evidence/bupa_evaluation_summary_2026-05-20.md`

Final verification note:

`evidence/final_technical_verification_2026-05-20.md`

## Technical Dependency Status

- R6 performance outputs have been generated in `data/heldout/bupa/performance/`.
- Supporting case-study, coaching, and performance-review conclusions have been consolidated into `evidence/bupa_supporting_review_summary_2026-05-20.md`.
- Bupa held-out evaluation summary has been completed and reviewed.
- Final verification commands passed.

No further project-system iteration should be performed from Bupa outputs. Remaining work now belongs to Final Report, final project status/demo checking, presentation/video, contribution statement, AI acknowledgement, client handover, and Q&A preparation.
