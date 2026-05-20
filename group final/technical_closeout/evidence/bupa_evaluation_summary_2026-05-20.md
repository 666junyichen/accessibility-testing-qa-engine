# Bupa Held-out Evaluation Summary

Date: 2026-05-20

---

## 1. Run Status

The corrected Bupa held-out pipeline run is complete. All 21 videos were processed end-to-end with zero failures at any stage. This run replaces the earlier partial Bupa run that produced zero-duration report artifacts; the root cause was that the windowing script built `windows.csv` via a separate fixed-window path that omitted required fields such as `duration`. The preprocessing script was corrected before this official run to read the Bupa manifest explicitly and reuse the frozen dev windowing implementation from `src/preprocessing/window_splitter.py`.

The `manyi_tan` provenance question has been resolved. The corrected pipeline produced 21 transcript JSON files, and `manyi_tan__web-health-information-bupa` is present in both `data/heldout/bupa/processed/transcripts.csv` and `data/heldout/bupa/performance/per_submission.csv`. The current repository is 21/21 at every stage.

---

## 2. Dataset and Path Isolation

- Project key: `web-health-information-bupa`
- All input data: `data/heldout/bupa/`
- Performance outputs: `data/heldout/bupa/performance/`
- Reports: `data/heldout/bupa/reports/`
- R6 cross-check lane: `with_overrides` for all 21 submissions, consistent with the `web-health-information-bupa` project mapping in `src/tracking/performance_model.py`.

Evaluation boundary: Bupa was used for held-out evaluation only. No prompts, schemas, scoring thresholds, coaching logic, friction taxonomy definitions, or tier boundaries were tuned using Bupa outputs. All design decisions were locked before this run.

---

## 3. Quantitative Results

### 3.1 Pipeline run summary

| Stage | Result |
|---|---|
| Bupa videos | 21 |
| Transcript JSON files | 21 |
| Transcript parse failures | 0 |
| Processed windows | 1,252 |
| Layer 3 Level B (video assessment) | 21/21 succeeded |
| Layer 3 Level A (window-level finding) | 1,252/1,252 succeeded |
| Filtered L3 findings | 813 |
| JSON reports generated | 21/21 |
| Zero-duration reports | 0 |

### 3.2 Report quality tier distribution

| Report quality tier | Count |
|---|---:|
| acceptable | 14 |
| poor | 7 |

Poor-tier reason for all 7: `task-blocking friction: S1/S2 present`.

Session-quality labels:

| Field | Distribution |
|---|---|
| narration | rich=20, adequate=1 |
| recording | good=9, acceptable=12 |

Top severity per video:

| Top severity | Video count |
|---|---:|
| S1 | 4 |
| S2 | 3 |
| S3 | 10 |
| S4 | 3 |
| S5 | 1 |

### 3.3 Global L3 finding distribution (813 filtered findings)

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

### 3.4 R6 tester-performance tier distribution

| R6 tester-performance tier | Count |
|---|---:|
| Leading | 14 |
| Proficient | 2 |
| Developing | 5 |
| Foundational | 0 |

Cap distribution:

| Cap reason | Count |
|---|---:|
| None | 16 |
| S1 project-level blocker present | 4 |
| >=2 S2 task-blockers | 1 |

---

## 4. Main Qualitative Patterns

**Friction type concentration.** F1 (Comprehension Friction) is the dominant friction type at 233 findings (28.7%), followed by F2 (Confidence Friction, 151, 18.6%) and F6 (Content Not Found, 145, 17.8%). These three together account for 65.1% of all filtered findings. The Bupa site's primary friction burden falls on comprehension, confidence, and content-discovery issues rather than on pure interface response mechanics. F3 (Accessibility Friction, 115) and F5 (Unexpected Behaviour, 74) together contribute another 23.2%, indicating that accessibility and unexpected-response issues are a secondary but substantial signal.

**Severity profile: bimodal.** 84.0% of findings fall at S5 (medium, 569) or S4 (high, 114). The bulk of friction is recoverable or non-blocking. However, 7 sessions contain at least one S1 or S2 finding, and these sessions all resolve to a poor report quality tier. The bimodal pattern — a majority of recoverable findings across most sessions alongside a concentrated set of task-blocking findings in a minority of sessions — is structurally consistent with the case-study evidence.

**Sentiment.** E4 (negative/frustrated) accounts for 682 of 812 non-blank sentiment labels (84.0%). E3 (neutral/indifferent) contributes 103 (12.7%). E2 (positive, 16) and E5 (negative/angry, 11) are minor. The Bupa held-out set skews toward negative participant sentiment, consistent with the high volume of comprehension, confidence, and content-discovery friction.

**Calibrator score.** L2 (560, 68.9%) is the dominant calibrator tier, with L3 (189, 23.2%) second. L1 (54), L4 (6), and L5 (4) are minor. This means most Bupa findings sit in the lower-to-mid calibrator-strength range, while only a small number of findings reach the strongest L4/L5 repair-concern levels.

**Narration quality.** 20 of 21 sessions were rated rich for narration. This supports using the Layer 3 evidence as primary qualitative signal across the held-out set. The one exception is manyi_tan (adequate narration, 6 windows, 2 findings), which has materially reduced evidence density.

---

## 5. R6 Performance Interpretation

### 5.1 Tier distinction

The **report quality tier** (from `data/heldout/bupa/reports/_summary.csv`) and the **R6 tester-performance tier** (from `data/heldout/bupa/performance/per_submission.csv` and `per_tester.csv`) share the column name `tier` but are distinct constructs and must be described separately.

- Report quality tier answers: how clean was this session as a recording and how rich is the captured evidence?
- R6 tester-performance tier answers: how well did this tester surface friction in this submission, scored across D1 narration, D2 friction surfacing, and D3 recording, with severity caps applied?

A session can have report tier `poor` while still earning a high R6 tester-performance score if the tester clearly surfaced the blocking friction. The reverse also holds.

### 5.2 Tier distribution interpretation

14 of 21 testers (66.7%) scored at Leading (composite ≥ 85), 2 at Proficient (70–84.9), and 5 at Developing (55–69.9). No tester scored Foundational.

All 5 Developing scores are cap-driven rather than driven by low uncapped composite scores:

| Tester | Score | Cap reason |
|---|---:|---|
| deanmills1987 | 55.0 | S1 project-level blocker present |
| gameoverdan | 55.0 | S1 project-level blocker present |
| olekwane | 55.0 | S1 project-level blocker present |
| sharelinsonny | 55.0 | S1 project-level blocker present |
| jadesharp92 | 65.0 | >=2 S2 task-blockers |

This is working as designed under the W9-locked scoring contract. The caps at 55.0 and 65.0 are product-risk signals: the tested product presented serious blocking friction. The uncapped composites for these testers were higher (ranging from 87.1 to 91.5), meaning the testers did surface friction effectively — the cap reflects the severity of what was found, not narration or surfacing failure.

The performance review confirmed that no scoring rules, caps, lane mappings, or tier boundaries need to change based on the Bupa run.

### 5.3 Trajectory note

Because Bupa has one submission per tester, the per-tester trajectory fields — `direction`, `delta_first_to_last`, and `persistent_friction_types` — are vacuous for all 21 rows. Bupa supports submission-level external validation only. Longitudinal trajectory conclusions are not possible from this held-out set.

---

## 6. Supporting Review Synthesis

### 6.1 Case-study evidence

Six Bupa sessions were selected as qualitative evidence examples spanning tier extremes, evidence-density variation, and failure-mode variety. They are not a statistically representative sample of all 21 sessions.

**olekwane__web-health-information-bupa** (poor tier, S1, 82 findings, 97 windows, rich narration, good recording): The strongest product-risk case in the Bupa set. Friction combines concrete accessibility breakdowns — readability, semantic markup, focus management — with loss of trust in the product offer. This case shows how accessibility and comprehension failures compound into both exclusion risk and commercial risk.

**iakhtar1__web-health-information-bupa** (poor tier, S2, 78 findings, 76 windows, rich narration, acceptable recording): The clearest screen-reader accessibility case. The product prevents a screen-reader user from accessing plan comparison and search functions needed for decision-making. Inaccessible comparison-table markup and absent search-field exposure are specifically evidenced. Fine-grained claims should stay close to reported finding text given acceptable (not good) recording quality.

**sharelinsonny__web-health-information-bupa** (poor tier, S1, 46 findings, 82 windows, rich narration, acceptable recording): A pathway-level failure rather than a single broken interaction. Location fit, booking prerequisites, and accessibility support discoverability all fail to sustain task completion. This is product risk around service discoverability and decision confidence.

**margieflint__web-health-information-bupa** (acceptable tier, S3, 67 findings, 72 windows, rich narration, good recording): A contrast case showing that acceptable-tier sessions can still contain dense, repeated content-not-found and comprehension costs. A large volume of F1/F2/F6 friction is present without a single hard blocker. Useful for illustrating cumulative failure without catastrophic breakdown.

**daniellepaigejones07__web-health-information-bupa** (acceptable tier, S3, 59 findings, 78 windows, rich narration, good recording): A medium-severity visual discomfort and contrast access-cost case. The participant can continue but colour scheme and brightness create sustained visual strain across multiple windows. Supports a claim about access cost rather than a one-off annoyance.

**manyi_tan__web-health-information-bupa** (acceptable tier, S5, 2 findings, 6 windows, adequate narration, acceptable recording): An evidence-limit example. Only mild findability friction is surfaced. This case shows how a short session can still produce valid findings without supporting broader product conclusions. Claims from this session should stay within its sample-size constraint.

### 6.2 Coaching review

The coaching review sampled 8 representative videos and produced an overall judgement of **PASS WITH CAVEATS**.

Coaching recommendation totals across all 21 Bupa sessions:

| Category | Count |
|---|---:|
| severity | 20 |
| friction-aggregation | 17 |
| recording | 12 |
| narration | 1 |

Priority distribution:

| Priority | Count |
|---|---:|
| 4 | 30 |
| 5 | 7 |
| 2 | 12 |
| 1 | 1 |

Coaching findings:

- Severity recommendations are generally well-grounded in high-friction evidence. Strong examples identified: iakhtar1 (severity grounded in real accessibility barriers), sharelinsonny (severity and aggregation coexist without conflicting priorities), gracieha22 (correctly avoids over-triggering aggregation), manyi_tan (narration recommendation appropriately conservative given sparse verbalisation).
- Friction-aggregation recommendations are technically correct but occasionally feel generic and have lower actionability.
- Recording recommendations are template-driven rather than highly contextual.
- Coaching specificity varies: some outputs are highly grounded, others are more category-level summaries.

None of these caveats are recommendation correctness failures. The V3.1 friction-aggregation logic represents a material improvement over earlier broader triggering behaviour.

---

## 7. Limitations

**L1 / L2 not regenerated for Bupa.** The corrected Bupa run did not regenerate `layer1_flags.csv` or `layer2_cluster_assignments.csv`. All 21 Bupa reports therefore show `l1_total=0` and `l2_coverage=0.0`. These values reflect missing held-out Layer 1 and Layer 2 artifacts; they do not indicate that no L1 or L2 issues existed in the sessions. Cross-layer interpretation using L1 or L2 evidence is not possible for this held-out set.

**D3 upward bias.** Without Layer 1 flags, `duration_anomaly=False` is assumed for every Bupa video. Any video that would have triggered duration anomaly under the full pipeline has its D3 score potentially upward-biased. The effect is bounded: D3 carries 15% composite weight and the D3 delta from this path is at most 30 points, giving a maximum composite swing of ~4.5 points. For most videos the recording quality label is the binding D3 factor, not the duration-anomaly clamp. This is a held-out-input limitation; it carries no consequence for R6 scoring logic.

**No longitudinal validation.** Bupa has one submission per tester. Per-tester trajectory fields are not meaningful. The held-out set supports submission-level external validation of the R6 scoring contract but cannot validate how tester performance evolves over multiple submissions.

**Evaluation-only boundary maintained.** No tuning was performed using Bupa outputs. This is both a strength (clean external validation) and a constraint: any mismatches between Bupa results and dev-set expectations cannot be corrected from the Bupa side.

**Case studies are selected examples.** The 6 qualitative cases were chosen to cover failure mode variety and tier extremes, not to be statistically representative. Claims derived from these notes should be attributed to specific cases, not generalised across the full Bupa set.

**Coaching caveats.** Coaching output specificity is variable, and aggregation and recording recommendations can be generic. These are quality caveats, not correctness failures, but they limit the precision of coaching-based conclusions in the Final Report.

**manyi_tan session sparseness.** With only 6 windows, 2 findings, adequate narration, and acceptable recording, manyi_tan provides materially less evidence than any other Bupa session. It is usable as an evidence-limit example only.

---

## 8. Final Technical Readiness Judgement

The Bupa held-out evaluation run is technically complete and ready to be referenced in the Final Report as external held-out validation evidence.

- The pipeline processed all 21 Bupa videos without failures at any stage, with zero schema errors, JSON errors, or API errors across both Layer 3 inference passes.
- Report quality tiers (14 acceptable, 7 poor) and R6 tester-performance tiers (14 Leading, 2 Proficient, 5 Developing, 0 Foundational) are internally consistent with the locked scoring contracts.
- Performance review confirmed that no scoring rules, caps, lane mappings, or tier boundaries require adjustment based on the Bupa run.
- Case-study and coaching evidence have been integrated; neither raises correctness failures.
- The `manyi_tan` provenance issue is resolved: 21 rows are confirmed in all performance and report files.
- The Layer 1 / Layer 2 limitation is documented and requires no corrective action within the held-out evaluation scope.

When the Final Report references Bupa results, three standard caveats apply: (1) L1/L2 were not regenerated, so cross-layer evidence is absent; (2) one submission per tester precludes longitudinal trajectory interpretation; (3) the evaluation boundary — no tuning from Bupa — was maintained throughout.
