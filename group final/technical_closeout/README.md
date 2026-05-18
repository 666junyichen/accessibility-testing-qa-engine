# Technical Closeout - Bupa Held-out Run

Date: 2026-05-18

## Current Status

The project is in final technical closeout. The next blocking step is the official Bupa held-out pipeline run.

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

## Next Owner

R7 owns the next step:

`tasks/R7_ivy_bupa_pipeline_run_2026-05-18.md`

R7 should run the frozen Bupa pipeline with path-isolated outputs and record exact commands, output paths, success/failure count, and dev55 demo sanity status.

There is no separate R2 task to assign at this stage. R2/Nix has already completed the directly actionable pre-run work: input correction, 21/21 transcript validation, R4 status reconciliation, and R6 lane/key confirmation.

## Dependencies After R7

After R7 generates Bupa reports and processed CSVs:

- R6 generates Bupa performance outputs.
- R3 writes Bupa case studies.
- R5 reviews Bupa coaching recommendations.
- R8 writes the Bupa held-out evaluation summary.
- Nix/Codex directly reconciles final technical closeout after the member outputs return.

Do not start Final Report prose, presentation bullet points, contribution statement, AI usage statement, or signatures from this folder.
