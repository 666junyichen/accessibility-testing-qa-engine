# R3 Task Brief - Bupa Held-out Case Studies

Date: 2026-05-19

## Goal

Write Bupa held-out qualitative case-study notes from the corrected reports. This is an evidence review task, not a pipeline rerun.

## Files To Use

- `data/heldout/bupa/reports/_summary.csv`
- `data/heldout/bupa/reports/*.json`
- `data/heldout/bupa/processed/layer3_findings_filtered.csv`
- `data/heldout/bupa/performance/per_submission.csv`
- `group final/technical_closeout/submissions/bupa_corrected_pipeline_run_2026-05-19.md`
- Existing style reference: `docs/case_studies.md`

## Recommended Case Candidates

Use 4-6 cases. Recommended candidates:

| Candidate | Why useful |
|---|---|
| `olekwane__web-health-information-bupa` | report tier poor; 82 findings; S1 accessibility/readability and task-blocking issues; strong product-risk case |
| `iakhtar1__web-health-information-bupa` | report tier poor; screen-reader/table-access issue; strong accessibility evidence |
| `sharelinsonny__web-health-information-bupa` | report tier poor; task abandonment/geographic mismatch; S1/S2 evidence |
| `margieflint__web-health-information-bupa` | report tier acceptable but 67 findings; good contrast case showing many recoverable comprehension/content issues |
| `daniellepaigejones07__web-health-information-bupa` | report tier acceptable; strong visual discomfort / contrast evidence |
| `manyi_tan__web-health-information-bupa` | short-sample caveat; useful only as an evidence-limit case, not as a major product conclusion |

## Required Content

For each selected case include:

- video ID
- report tier and reason from `_summary.csv` or JSON `overall`
- windows and L3 finding count
- top severity
- dominant friction types
- 2-3 concrete top findings with `window_id`, `friction_type`, `severity_s`, and a short paraphrase
- interpretation: what product/session risk the case demonstrates
- caveat if relevant, especially for `manyi_tan` or missing L1/L2 context

## Constraints

- Do not tune taxonomy, prompts, scoring, or report logic from Bupa.
- Do not present R6 performance tier as product quality tier.
- Do not reuse dev-set case-study wording as if it came from Bupa.
- Do not start Final Report prose, presentation bullets, contribution statements, AI usage statements, or signatures.

## Expected Output

Send back one markdown file or message:

`R3_bupa_case_studies_2026-05-19.md`

It should be report-ready notes, but not the final report section.
