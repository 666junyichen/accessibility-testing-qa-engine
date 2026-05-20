# Step 6.3 — Performance Tracking

> **Author**: Ruihan Shan
> **Inputs**:
> - `data/processed/layer3_findings_filtered.csv` — finding-level rows from Step 5.1-A
> - `data/processed/layer3_video_assessments.csv` — video-level rows from Step 5.1-B
>
> **Inputs** — fill in two fields the two primary CSVs can't supply:
> - `data/processed/windows.csv` → `total_windows` (else: lower-bounded by distinct findings windows)
> - `data/processed/layer1_flags.csv` → `duration_anomaly` (else: defaults to False)
>
> **Outputs**:
> - `src/tracking/performance_model.py` — pure-function aggregation module
> - `data/processed/performance/per_submission.csv` (57 rows = dev 55 + 2 edge cases) and `per_tester.csv` (27 rows = one per dev tester) — per-tester analysis sketch. Regenerate with `python scripts/build_performance_tracking.py`.
> - this document (data model, scoring rules, SMP mapping table)
>
> **Out of scope**:
> - reproducing SMP Model B (product-accessibility scoring); we produce **tester-performance-dimension aggregation**
> - Bupa held-out — Step 6.3 stays inside dev set per `docs/eval_freeze.md`
> - schema mutations to fusion output — frozen by Gate 2 Freeze 3

---

## 1. Why this step exists

The fusion output in `data/processed/reports/*.json` answers *"how good is this single submission?"*. R6 has to answer two further questions:

1. **Per-submission rendering** — give each submission a single 0-100 score and a tier (Foundational / Developing / Proficient / Leading) using SMP score-language, so coaching, dashboards, and the Final Report all speak the same vocabulary.
2. **Cross-submission trajectory** — for testers with ≥2 submissions, classify their movement (improving / stable / declining) and surface persistent friction patterns (same `friction_type` recurring across submissions).

Per the dev split, 28 testers (27 dev + 1 edge case from full 57) cover 57 videos; 12 testers have 3 submissions and 6 have 2. That's enough longitudinal density for a meaningful trajectory layer in dev. (Bupa held-out: most testers ≤1 submission — trajectory layer there is a future-work caveat, not a goal.)

---

## 2. SMP alignment principle (Round 6 decision)

The plan is unambiguous: we **align to SMP language, we do not re-implement Model B**. Concretely:

| What we adopt from SMP | What we do not touch |
|---|---|
| 0–100 scale | Model B's product-accessibility scorer |
| Four-tier output: Foundational / Developing / Proficient / Leading | SMP base-70 production rule (we use base 70 *as language*, not as production logic) |
| Threshold caps for severe blockers | SMP cohort weighting numerical chains |
| "Score language" of the calibrator output | C3 overrides — those are SMP-side, we stay raw |

**Mapping to design docs (the four anchors named in the plan)** — required by Round 6 to avoid "verbal SMP reference, actual self-built mapping":

| SMP design doc | Anchor used here | Where it shows up below |
|---|---|---|
| `01-scoring-model-success-criteria.md` | Scoring must be *interpretable* and *defensible per submission*; cap rules must be tied to evidence, not derived weights | §4 (Submission score), §4.4 (cap rules) |
| `02-scoring-model-comparison-A-B-C-D.md` | Choice rationale: we do not reproduce A/B/C/D; we sit *outside* the product-scoring axis on a tester-aggregation axis using shared language | §2 table, §3 boundary statement |
| `03-scoring-model-assessment-ABDC2.md` | Acknowledges Model C2 sensitivity to sparse data — informs our handling of testers with sparse narration / few findings | §4.5 (low-evidence handling) |
| `04-model-E-reworked-cap-based.md` | The cap-based intuition (severe events cap the score regardless of base) is the structural shape we copy | §4.4 (severity caps), §4.6 (worked example) |
| `06-friction-sentiment-framework.md` | F1–F7 / S1–S6 / E1–E5 / L1–L5 vocabulary; E3 excluded from aggregate sentiment | §4.2 (dimension scores), §4.3 (sentiment rule) |

**What we do NOT pull in**: any of `06`'s production cohort-weighting numerical chain, the SMP base-70 production multiplier, or anything keyed to specific clients' Model C overrides.

---

## 3. Boundary against Model B / SMP — explicit statement

Model B scores **product accessibility per project**: the product is the unit, the score is the product's. R6 scores **tester performance per submission and per tester across submissions**: the tester is the unit, the score answers *"how well did this tester articulate their experience and surface real friction during this session?"*

Both axes are orthogonal. They share **score language** (0-100, four tiers, cap rules) so coaching / Final Report don't speak two dialects. They do not share **scorer mechanics**. This is the alignment object the plan calls out as the most likely silent-drift trap.

A simple way to test future PRs against this boundary: if a feature change starts answering "is the *product* accessible?" — that's Model B territory, route to SMP, do not put it in `performance_model.py`.

---

## 4. Per-submission scoring (PerformanceRecord)

Each video → one `PerformanceRecord`.

### 4.1 Inputs (frozen)

From `QualityReport` (Step 6.1):
- `l3_findings.by_friction_type` — dict[F1..F7 → count]
- `l3_findings.by_severity` — dict[S1..S6 → count]
- `l3_findings.by_sentiment` — dict[E1..E5 → count]
- `l3_findings.by_calibrator_score` — dict[L1..L5 → count] (audit-only, see §4.7)
- `l3_findings.signal_alignment_distribution` — dict[aligned/conflicted/stated_missing → count]
- `l3_findings.total_findings`
- `l3_assessment.narration_quality` ∈ {none, sparse, adequate, rich}
- `l3_assessment.recording_quality` ∈ {poor, acceptable, good}
- `l1.duration_anomaly`, `l1.flag_counts`
- `overall.quality_tier` ∈ {good, acceptable, poor}
- `total_windows`

### 4.2 Three dimension scores (each 0–100)

We expose three named dimensions so the Final Report can show *why* a submission scored what it did. Each dimension uses its own simple rule; weighted in §4.3.

**D1 — Narration Substantiveness** (does the tester articulate their reasoning richly enough to be analyzable)

| `narration_quality` | D1 contribution |
|---|---|
| rich | 90 |
| adequate | 75 |
| sparse | 55 |
| none | 25 |

**D2 — Friction-Surfacing Quality** (does the session surface real friction with aligned signals — not "everything's fine" empty narration, not unrelated chatter)

```
findings_density = total_findings / max(total_windows, 1)
aligned_share = aligned / max(total_findings, 1)        # signal_alignment
mid_high_severity = (S1+S2+S3+S4) / max(total_findings, 1)
```

D2 = 60
+ 20 · clamp(findings_density / 0.6, 0, 1)        # 0.6 findings/window ≈ rich tester baseline
+ 10 · aligned_share                              # rewards stated/observed agreement
+ 10 · mid_high_severity                          # rewards reaching real, not trivial, friction
clamped to [0, 100].

If `total_findings == 0` and narration is `rich` or `adequate`: D2 = 50 (neutral) — see §4.5 low-evidence handling.

**D3 — Recording / Session Usability**

| `recording_quality` | D3 contribution |
|---|---|
| good | 90 |
| acceptable | 70 |
| poor | 40 |

If `l1.duration_anomaly == True`: D3 = min(D3, 60) (cap, not penalty stacking).

### 4.3 Composite submission score (heuristic v1)

```
raw = 0.50 · D1 + 0.35 · D2 + 0.15 · D3
```

> **heuristic v1.** The 0.50 / 0.35 / 0.15 split is a defensible-but-not-validated heuristic locked in W9 (P2#8a, lead-confirmed). It has *not* been calibrated against held-out data. The ratio is intended to favor D1 (narration is the upstream prerequisite — without it D2 is mostly noise), then D2, then D3 (D3 mostly disqualifies extreme cases via the cap, not the weight). Weights are revisited once (a) per-tester sketch is reviewed and (b) Final Report cycle opens; until then any consumer of these numbers should treat them as a v1 working point, not as anointed weights.

Sentiment (E1–E5) deliberately does **not** enter `raw`. Per `06`, E3 is excluded from aggregation, and E4/E5 *about a product* should not penalize the tester. We instead surface sentiment in the per-tester layer as a *facet*, not as a score input.

### 4.4 Severity caps (cap-based, per Model E)

Caps are applied after `raw` is computed. The minimum across applicable caps wins.

| Trigger | Cap on submission score |
|---|---|
| Any S1 finding (project-level blocker present) | ≤ 55 |
| ≥2 S2 findings (multiple task blockers) | ≤ 65 |
| `narration_quality == 'none'` AND `total_findings == 0` | ≤ 40 (no analyzable signal at all) |
| `recording_quality == 'poor'` | ≤ 70 |

The caps are deliberately *output-language caps*, mirroring Model E's idea that severe single events cap the result regardless of the base. They do **not** inject extra weight into `raw` — keeping the rule auditable per `01`'s success criterion.

### 4.5 Low-evidence handling (per `03` — sensitivity to sparse data)

Two ambiguous rows in dev:
- `troyparnell_suncorp` (transcription edge case, 2 segments)
- `thanoptions_wa` (sparse — 7 segments)

Rule: if `total_windows < 5`, the record is emitted with `low_evidence=True` and the score is **reported but flagged** in per-tester aggregation (i.e., it shows up in the per-submission CSV but is excluded from trajectory slope computation). This avoids letting a single noisy submission swing a tester's trajectory.

### 4.6 Worked example — `Sharelinsonny_suncorp`

From `data/processed/reports/Sharelinsonny_suncorp.json`:
- narration `rich`, recording `acceptable` → D1 = 90, D3 = 70
- 27 findings / 81 windows = 0.333 density; aligned 26/27 = 0.96; mid-high (S2+S3+S4) = 8/27 = 0.296
- D2 = 60 + 20·(0.333/0.6) + 10·0.96 + 10·0.296 = 60 + 11.1 + 9.6 + 3.0 = **83.7**
- raw = 0.50·90 + 0.35·83.7 + 0.15·70 = 45 + 29.3 + 10.5 = **84.8**
- caps: S2 present (2 of them — note "≥2 S2" trigger). raw 84.8 → capped to **65**

Final: 65 → tier *Developing* (per §4.7). The cap is the binding constraint here, exactly as the SMP language intends — task-blocking friction caps the score.

### 4.7 Calibrator-L as audit signal only

Per §6.1 fusion's "main / auxiliary" rule, `calibrator_score_l` (L1–L5) is **never** weighted into `raw` or the cap. It's stored on the record as `calibrator_aggregate` (the per-video weighted-mean L-label) and surfaced as a sanity check.

**Mismatch flag (W9 P1#8b lock-in).** Each `PerformanceRecord` carries a boolean `calibrator_aggregate_mismatch_flag`. It is True iff the composite tier (from §4.8) and the *implied* tier of the calibrator aggregate diverge by **≥ 2 tier steps**. The implied-tier mapping is:

| `calibrator_aggregate` | Implied tier | Tier rank |
|---|---|---|
| L1 (minor friction) | Leading | 4 |
| L2 (moderate) | Proficient | 3 |
| L3 (significant) | Developing | 2 |
| L4 (severe / near-abandonment) | Foundational | 1 |
| L5 (blocking) | Foundational | 1 |

Tier-rank gap ≥ 2 is the threshold (e.g. composite = `Leading` but calibrator aggregate → `Foundational` ⇒ flag). At < 2-step gap, the cross-check is treated as agreement-within-noise.

**Audit-only contract (R5/R6 decoupling).** The mismatch flag is surfaced as a column on `per_submission.csv`, and as a roll-up count (`calibrator_aggregate_mismatch_count`) on `per_tester.csv`, for human review. It does **not** trigger a Step 6.2 (R5) coaching priority bump under any circumstance — keeping R5 and R6 cleanly decoupled is a hard W9 constraint, and any future "auto-bump on mismatch" is explicitly out of scope for the Final Report cycle.

When `calibrator_aggregate` is `null` (no findings, or all blanks) the flag is `False` — a missing audit signal is treated as "cross-check unavailable", not as "mismatch".

### 4.8 Final tier mapping

| Composite score | Tier |
|---|---|
| 85 – 100 | Leading |
| 70 – 84 | Proficient |
| 55 – 69 | Developing |
| 0 – 54 | Foundational |

(Tier boundaries derive from SMP four-tier language. Base score 70 is *the threshold for Proficient*, not a default starting point — we pick this interpretation deliberately so a "neutral" tester lands at the bottom of Proficient, not in the middle of Developing.)

---

## 5. Cross-submission tracking (TesterTrajectory)

For each tester with ≥2 non-low-evidence submissions:

### 5.1 Trajectory direction (ordered proxy / longitudinal sketch)

> **Wording lock-in (W9 P1#8c).** This section produces an *ordered proxy* — a longitudinal sketch — **not** a real improvement trend. The dev set has no reliable per-submission timestamps, so we order each tester's submissions by `(project, video_id)` (`ordering_basis = "project_video_id_proxy"` on the per-tester CSV). Any downstream prose must say "ordered proxy / longitudinal sketch" rather than "real improvement trend"; treating the direction label as a true time-series claim is explicitly out of scope until a submission-timestamp source lands.

Within that proxy ordering:

```
delta = score[last] − score[first]
```

| delta | direction |
|---|---|
| > +5 | improving |
| −5 ≤ delta ≤ +5 | stable |
| < −5 | declining |

The ±5 stable band is locked in (W9 P1#8c). It is intentionally narrow, but the chunked tier boundaries (15 points) absorb most noise; we use score deltas not tier deltas because tier deltas hide partial movement. The direction labels (`improving` / `stable` / `declining`) describe the *ordered proxy* only — they do not assert real-world improvement until a true timestamp ordering is available.

### 5.2 Persistent friction flag

For each `friction_type` F1..F7:
- count submissions where this type is the tester's top-3 friction type
- if ≥2 of the tester's submissions list this type in top-3 → `persistent_friction_types` includes it

This surfaces the "same problem recurring" pattern that's coaching-actionable, without false-positive on a tester who hits F1 once and F6 once.

### 5.3 Per-tester aggregate score

`tester_score = mean(submission scores, low_evidence excluded)`
`tester_tier = tier(tester_score)`

This is the headline number per tester; the per-submission scores stay separate so a coach can see whether a tester is getting better or got lucky once.

### 5.4 Sentiment facet (not a score input)

Per-tester `sentiment_distribution = sum of E1..E5 across submissions` — surfaced as a facet for coaching context (e.g., a tester who scores well but trends E5 may need a different conversation than one who trends E2).

---

## 6. UQ data limitation handling (Katie note)

`s3://.../scoring-reference/data/postgrad-enrolment-experience/` contains UQ raw survey scores only — no individual insights, no Katie Model C3 overrides (no LLM insights have ever been run on UQ at SMP). Therefore:

- **AAMI / Bupa lane** — when the per-tester layer is later cross-checked against an SMP score (Step 8.5 territory), the comparison is against `score-overrides.csv` values (post-C3).
- **UQ lane** — the per-tester layer is cross-checked against raw survey only, not against overrides. The output CSV carries a `cross_check_lane ∈ {with_overrides, raw_only, dev_only}` column so downstream readers don't silently treat empty UQ overrides as "we agree with SMP on UQ" — they're "no override exists" in the first place.

Lanes are pre-populated for known dev projects (`suncorp` / `wa` → `with_overrides`, `uq` → `raw_only`); Bupa held-out 触发后会消费此字段, so the column already exists when Step 8.5 needs it.

---

## 7. Boundaries and known limitations

**In scope**:
- design doc + reference module + per-tester sketch on the existing 57 reports
- mapping table to the four SMP design docs

**Out of scope / explicit non-goals**:
- Bupa held-out — gated by `docs/eval_freeze.md`. We must not run R6 mapping on Bupa data until Gate 1 ∧ Gate 2 are green and Freeze 4 (R6 mapping rules) is signed.
- Modifying fusion schema — that's Freeze 3 territory.
- Real chronological order — current dev set has no reliable submission timestamps. We use `(project, video_id)` ordering as a placeholder; this is documented in the per-tester CSV as `ordering_basis = project_video_id_proxy` (an *ordered proxy* — see §5.1).
- Coaching recommendation generation — owned by R5 (Step 6.2). R6 surfaces the facts (persistent friction, declining trajectory) but does not write coaching copy.

**Open items (for Final Report cycle)**:
1. The 0.50 / 0.35 / 0.15 weights are locked as **heuristic v1** for W9 (P2#8a). Revisit once the per-tester sketch CSV is reviewed; until then any downstream claim must label them v1, not "validated".
2. ~~Decide whether `calibrator_aggregate` mismatch flag should auto-trigger a coaching priority bump in Step 6.2 (R5 input needed).~~ **Closed (W9 P1#8b)**: mismatch flag stays audit-only and does not feed R5 priority. R5/R6 remain decoupled. (See §4.7.)
3. ~~The ±5 stable band for trajectory direction was set on intuition; revisit after looking at the actual delta distribution in the per-tester CSV.~~ **Closed (W9 P1#8c)**: ±5 band locked in; direction labels are documented as an *ordered proxy*, not a real trend. (See §5.1.)

---

## 8. Module API surface

`src/tracking/performance_model.py` exposes pure functions:

```python
def score_submission(report: dict) -> PerformanceRecord
def aggregate_tester(records: list[PerformanceRecord]) -> TesterTrajectory
def build_per_tester_table(records: list[PerformanceRecord]) -> list[TesterTrajectory]
```

No file I/O lives in the scoring functions — same pattern as `src/pipeline/fusion.py`. A thin loader `load_reports(reports_dir)` is provided as a convenience for the analysis script and tests; it's the only function that reads disk.

Schemas (`PerformanceRecord`, `TesterTrajectory`) live alongside the functions and use pydantic with `extra="forbid"` to mirror the discipline in `src/pipeline/schemas.py`.
