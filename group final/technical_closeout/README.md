# Technical Closeout - Bupa Held-out Run

Date: 2026-05-19

## Current Status

The project is in final technical closeout. The corrected official Bupa held-out pipeline run has been completed and committed-ready in held-out paths.

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

- R7 produced a first Bupa run on 2026-05-18 with 21/21 reports.
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

Primary corrected run record:

`submissions/bupa_corrected_pipeline_run_2026-05-19.md`

Earlier R7 first-run note:

`submissions/R7_ivy_bupa_pipeline_demo_2026-05-18.md`

## Remaining Technical Dependencies

After the corrected Bupa reports and processed CSVs are available:

- R6 performance outputs have been generated in `data/heldout/bupa/performance/`.
- R3 case-study notes have been returned.
- R5 coaching review has been returned.
- R6 performance review/sign-off has been returned.
- R8 writes the Bupa held-out evaluation summary next.
- The final technical reconciliation happens after the member outputs return.

Do not start Final Report prose, presentation bullet points, contribution statement, AI usage statement, or signatures from this folder.
