# Bupa Held-out Supporting Review Summary

Date: 2026-05-20

## Purpose

This file consolidates the useful technical conclusions from the Bupa closeout
review process into a client/school-facing evidence note. It replaces internal
task briefs, transfer messages, intermediate input packs, and raw member-return
documents that are not appropriate for the final project repository.

## Data Readiness

- Bupa held-out scope is 21 collated videos.
- The earlier count of 42 referred to 21 MP4 files plus 21 VTT sidecar files.
- All 21 transcript JSON files are present and parseable.
- `manyi_tan__web-health-information-bupa` is included in the corrected run
  after the S3 key correction; it remains a short evidence-density case.
- Processed Bupa outputs use `project=web-health-information-bupa`.
- `bupa-uk` is only the source/S3 alias and is not used as the processed
  project key.

## Pipeline Evidence

- Corrected preprocessing generated 21 transcripts, 204,981 items, 10,194
  segments, and 1,252 windows.
- Layer 3 Level B succeeded for 21/21 videos.
- Layer 3 Level A succeeded for 1,252/1,252 windows.
- Filtered Layer 3 findings: 813.
- Report generation produced 21/21 readable report JSON files.
- No zero-duration Bupa reports remain.
- Bupa outputs stayed under held-out paths and did not overwrite dev55
  artefacts.

## Case-study Evidence

Six Bupa sessions were selected as qualitative examples. They were chosen to
cover tier extremes, evidence-density variation, and different failure modes;
they are not a statistically representative sample of all 21 sessions.

| Case | Report tier | Evidence value |
|---|---|---|
| `olekwane__web-health-information-bupa` | poor | Strongest combined accessibility, comprehension, readability, focus-management, and trust-risk case. |
| `iakhtar1__web-health-information-bupa` | poor | Clearest screen-reader / comparison-table accessibility case. |
| `sharelinsonny__web-health-information-bupa` | poor | Pathway-level failure around location fit, booking prerequisites, and support discoverability. |
| `margieflint__web-health-information-bupa` | acceptable | Dense but mostly recoverable comprehension and content-discovery friction. |
| `daniellepaigejones07__web-health-information-bupa` | acceptable | Repeated visual discomfort and contrast/brightness access-cost evidence. |
| `manyi_tan__web-health-information-bupa` | acceptable | Short-sample evidence-limit case with only mild findability friction. |

## Coaching Review

The coaching output passed qualitative review with caveats.

Positive findings:

- Severity recommendations are generally grounded in genuine high-friction
  findings.
- Recording and narration recommendations are mostly consistent with
  session-level labels.
- V3.1 friction aggregation is materially better controlled than earlier broad
  triggering behaviour.

Caveats:

- Some friction-aggregation recommendations remain broad.
- Recording recommendations are deterministic and template-like.
- Coaching specificity varies by session.

These are quality caveats, not correctness failures.

## Performance Review

- Bupa performance outputs contain 21 per-submission rows and 21 per-tester
  rows.
- All rows use `cross_check_lane=with_overrides`.
- Report quality tier and tester-performance tier are different outputs and
  must not be conflated.
- R6 tester-performance tier distribution:

| Tier | Count |
|---|---:|
| Leading | 14 |
| Proficient | 2 |
| Developing | 5 |
| Foundational | 0 |

No scoring rules, caps, lane mappings, or tier boundaries were changed from
Bupa results.

## Preserved Limitations

- Bupa Layer 1 and Layer 2 artefacts were not regenerated; `l1_total=0` and
  `l2_coverage=0.0` are input-scope limitations, not product findings.
- Bupa has one submission per tester, so it does not validate longitudinal
  tester trajectory.
- Case studies are selected evidence examples, not a representative sample.
- Coaching recommendations are useful as reviewer support but should not be
  overstated as fully contextual human coaching.

## Freeze Boundary

Bupa was used only for external evaluation. It did not change prompts, schemas,
Layer 1 thresholds, Layer 2 settings, fusion rules, postprocess filters, R6
scoring, or coaching logic.
