# Bupa Held-out Fact Pack

Date: 2026-05-20

Use this as a concise Final Report / presentation source. The authoritative
technical evidence is still the closeout bundle in
`need/03_final_checking/technical_closeout/`.

## Evaluation Boundary

- Bupa project key: `web-health-information-bupa`.
- Held-out path: `data/heldout/bupa/`.
- Bupa was used for final external evaluation only.
- No prompts, schemas, Layer 1 thresholds, Layer 2 settings, fusion rules,
  postprocess filters, R6 scoring rules, or coaching logic were tuned using
  Bupa outputs.

## Pipeline Facts

| Item | Value |
|---|---:|
| Collated videos | 21 |
| Transcript JSON files | 21 |
| Transcript parse failures | 0 |
| Processed windows | 1,252 |
| Filtered Layer 3 findings | 813 |
| Generated report JSON files | 21 |
| R6 per-submission rows | 21 |
| R6 per-tester rows | 21 |
| Zero-duration reports | 0 |

## Report Quality

| Report quality tier | Count |
|---|---:|
| acceptable | 14 |
| poor | 7 |

All 7 poor-tier reports were caused by task-blocking S1/S2 friction. This is a
report-quality construct and must not be conflated with the R6
tester-performance tier.

## Main Finding Pattern

| Friction type | Count |
|---|---:|
| F1 Comprehension | 233 |
| F2 Confidence | 151 |
| F6 Content Not Found | 145 |
| F3 Accessibility | 115 |
| F5 Unexpected Behaviour | 74 |
| F7 Flow / Navigation | 62 |
| F4 Account / Authentication | 33 |

The dominant Bupa pattern is comprehension, confidence, and content-discovery
friction, with accessibility as a strong secondary signal.

## R6 Tester-performance Facts

| R6 tier | Count |
|---|---:|
| Leading | 14 |
| Proficient | 2 |
| Developing | 5 |
| Foundational | 0 |

The 5 Developing outcomes are cap-driven. Their uncapped composites were higher;
the cap reflects product-risk severity in the tested experience, not a failure
to surface friction.

## Selected Case Evidence

| Case | Evidence value |
|---|---|
| `olekwane__web-health-information-bupa` | Strongest combined accessibility, comprehension, readability, focus-management, and trust-risk case. |
| `iakhtar1__web-health-information-bupa` | Clearest screen-reader and comparison-table accessibility case. |
| `sharelinsonny__web-health-information-bupa` | Pathway-level failure around location fit, booking prerequisites, and support discoverability. |
| `margieflint__web-health-information-bupa` | Dense but recoverable comprehension and content-discovery friction without a hard blocker. |
| `daniellepaigejones07__web-health-information-bupa` | Repeated visual discomfort and contrast/brightness access-cost evidence. |
| `manyi_tan__web-health-information-bupa` | Short evidence-density case; useful for explaining inference limits. |

## Caveats to Preserve

- Bupa Layer 1 and Layer 2 artifacts were not regenerated, so Bupa conclusions
  should not be narrated as cross-layer L1/L2 evidence.
- `l1_total=0` and `l2_coverage=0.0` in Bupa reports are input-scope caveats,
  not findings that no L1/L2 issues existed.
- Without Layer 1 flags, D3 can be upward-biased by at most about 4.5 composite
  points where duration anomaly would otherwise have applied.
- Bupa has one submission per tester, so it does not validate longitudinal
  tester trajectory.
- Case studies are selected examples, not a statistically representative
  sample of all 21 sessions.

