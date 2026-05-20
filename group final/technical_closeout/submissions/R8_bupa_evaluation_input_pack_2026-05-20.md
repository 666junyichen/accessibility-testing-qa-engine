# R8 Bupa Evaluation Input Pack

Date: 2026-05-20

Purpose: pre-checked inputs for R8 to write the Bupa held-out evaluation summary. This is not Final Report prose and should not be submitted as the R8 summary directly.

## Source Files

- Corrected run: `group final/technical_closeout/submissions/bupa_corrected_pipeline_run_2026-05-19.md`
- R3 case studies: `group final/technical_closeout/submissions/R3_bupa_case_studies_2026-05-19.md`
- R5 coaching review: `group final/technical_closeout/submissions/R5_bupa_coaching_review_2026-05-19.md`
- R6 performance sign-off: `group final/technical_closeout/submissions/R6_bupa_performance_review_signoff.md`
- Reconciliation: `group final/technical_closeout/submissions/member_returns_reconciliation_2026-05-20.md`
- Reports: `data/heldout/bupa/reports/_summary.csv`
- Performance: `data/heldout/bupa/performance/per_submission.csv`

## Run Facts

- Bupa videos: 21
- transcript JSON files: 21
- processed windows: 1252
- Layer 3 Level B: 21/21 succeeded
- Layer 3 Level A: 1252/1252 succeeded
- filtered L3 findings: 813
- JSON reports: 21/21 generated
- zero-duration reports: 0
- project key: `web-health-information-bupa`
- R6 lane: `with_overrides` for all 21 rows

## Report Quality Results

Report quality tier distribution:

| Report quality tier | Count |
|---|---:|
| acceptable | 14 |
| poor | 7 |

Top severity distribution by video:

| Top severity | Video count |
|---|---:|
| S1 | 4 |
| S2 | 3 |
| S3 | 10 |
| S4 | 3 |
| S5 | 1 |

Session-quality labels:

| Field | Distribution |
|---|---|
| narration | rich=20, adequate=1 |
| recording | acceptable=12, good=9 |

## Global L3 Finding Distribution

Friction type:

| Type | Count |
|---|---:|
| F1 | 233 |
| F2 | 151 |
| F6 | 145 |
| F3 | 115 |
| F5 | 74 |
| F7 | 62 |
| F4 | 33 |

Severity:

| Severity | Count |
|---|---:|
| S5 | 569 |
| S4 | 114 |
| S3 | 77 |
| S6 | 43 |
| S2 | 5 |
| S1 | 5 |

Sentiment:

| Sentiment | Count |
|---|---:|
| E4 | 682 |
| E3 | 103 |
| E2 | 16 |
| E5 | 11 |
| blank | 1 |

Calibrator score:

| Score | Count |
|---|---:|
| L2 | 560 |
| L3 | 189 |
| L1 | 54 |
| L4 | 6 |
| L5 | 4 |

## Highest-Finding Videos

| Video ID | Report tier | Findings | Top severity | Narration | Recording |
|---|---|---:|---|---|---|
| `olekwane__web-health-information-bupa` | poor | 82 | S1 | rich | good |
| `iakhtar1__web-health-information-bupa` | poor | 78 | S2 | rich | acceptable |
| `margieflint__web-health-information-bupa` | acceptable | 67 | S3 | rich | good |
| `daniellepaigejones07__web-health-information-bupa` | acceptable | 59 | S3 | rich | good |
| `lindarcole__web-health-information-bupa` | acceptable | 53 | S3 | rich | good |
| `ghum__web-health-information-bupa` | acceptable | 49 | S3 | rich | acceptable |
| `chiomaenenmoh__web-health-information-bupa` | acceptable | 47 | S3 | rich | good |
| `sharelinsonny__web-health-information-bupa` | poor | 46 | S1 | rich | acceptable |

## R6 Performance Results

R6 tester-performance tier distribution:

| R6 tier | Count |
|---|---:|
| Leading | 14 |
| Proficient | 2 |
| Developing | 5 |
| Foundational | 0 |

Cap reasons:

| Cap reason | Count |
|---|---:|
| none | 16 |
| S1 project-level blocker present | 4 |
| >=2 S2 task-blockers | 1 |

Interpretation requirement:

- Report quality tier and R6 tester-performance tier must be described separately.
- A poor report-quality session can still have a high R6 tester-performance score if the tester clearly surfaced serious friction.
- R6 confirmed no scoring rules, caps, lanes, or tier boundaries need to change.

## R3 Case-Study Synthesis

R3 returned 6 cases:

- `olekwane__web-health-information-bupa`: strongest product-risk case combining accessibility, readability, semantics/focus management, and loss of trust.
- `iakhtar1__web-health-information-bupa`: clearest screen-reader/accessibility case, especially inaccessible comparison-table and search interactions.
- `sharelinsonny__web-health-information-bupa`: pathway-level failure around location fit, booking prerequisites, and accessibility support discoverability.
- `margieflint__web-health-information-bupa`: acceptable-tier contrast case with dense but mostly recoverable content-not-found and comprehension friction.
- `daniellepaigejones07__web-health-information-bupa`: medium-severity visual discomfort and contrast/brightness access-cost case.
- `manyi_tan__web-health-information-bupa`: short-sample evidence-limit case with mild findability issues only.

R8 should cite R3 as qualitative support, not as statistical representativeness.

## R5 Coaching Review Synthesis

R5 overall judgement:

`PASS WITH CAVEATS`

Generated coaching recommendation totals:

| Category | Count |
|---|---:|
| severity | 20 |
| friction-aggregation | 17 |
| recording | 12 |
| narration | 1 |

Priority distribution:

| Priority | Count |
|---|---:|
| 5 | 7 |
| 4 | 30 |
| 2 | 12 |
| 1 | 1 |

R5 caveats for R8:

- friction-aggregation recommendations can still feel generic
- recording recommendations are often template-like
- coaching specificity varies across videos

R5 judged these as recommendation-quality caveats, not correctness failures.

## R6 Reconciliation Notes

R6 sign-off had two snapshot-based conditions. Current repository checks resolve them:

- `manyi_tan__web-health-information-bupa` is present in transcripts and performance outputs.
- performance CSVs exist with 21 submission rows and 21 tester rows.
- all rows use `with_overrides`.

R6 caveats still to preserve:

- Bupa has one submission per tester, so per-tester trajectory fields are not meaningful.
- Bupa Layer 1 flags were not regenerated; D3 may be slightly upward-biased for any duration-anomalous Bupa video.
- R6 tier language must be kept separate from report quality tier language.

## Required Limitations For R8

- Bupa was used only for held-out evaluation; no tuning was performed from Bupa outputs.
- Layer 1 and Layer 2 were not regenerated for Bupa.
- `l1_total=0` and `l2_coverage=0.0` therefore mean missing held-out L1/L2 artifacts, not absence of possible L1/L2 issues.
- R6 performance is submission-level external validation only; Bupa does not support longitudinal trajectory validation.
- R5 coaching outputs passed review with caveats about specificity and templating.
- R3 cases are selected qualitative examples, not a representative sample.

## R8 Next Action

R8 can now write `R8_bupa_evaluation_summary_2026-05-19.md` using this input pack plus the underlying source files. The output should remain a technical closeout summary, not course Final Report prose.
