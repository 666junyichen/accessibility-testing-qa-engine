# R6 Task Brief - Bupa Performance Output Review

Date: 2026-05-19

## Goal

Review and sign off the generated Bupa held-out R6 performance outputs. The outputs have already been generated; this task is a sanity review, not a rerun requirement.

## Files To Use

- `data/heldout/bupa/performance/per_submission.csv`
- `data/heldout/bupa/performance/per_tester.csv`
- `data/heldout/bupa/reports/_summary.csv`
- `group final/technical_closeout/submissions/R6_bupa_performance_outputs_2026-05-19.md`
- `group final/technical_closeout/submissions/bupa_corrected_pipeline_run_2026-05-19.md`

## Required Checks

1. Confirm all 21 Bupa rows use `cross_check_lane=with_overrides`.
2. Confirm row counts:
   - `per_submission.csv`: 21 rows
   - `per_tester.csv`: 21 rows
3. Confirm no R6 scoring rules, caps, lane mapping, or tier boundaries need to be changed.
4. Explicitly note that R6 `tier` is tester-performance tier, while report `_summary.csv` `tier` is product/session quality tier.
5. Note the caveat that Bupa Layer 1 flags were not regenerated, so duration anomaly is not included in R6 D3 scoring.

## Expected Output

Send back a short markdown note with:

- final status: pass / needs correction
- row-count check
- lane check
- tier interpretation note
- any caveat R8 should mention

Do not start Final Report prose, presentation bullets, contribution statements, AI usage statements, or signatures.
