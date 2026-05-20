# R6 Bupa Performance Output — Sanity Review Sign-off

Author: R6 (Ruihan)
Date: 2026-05-19
Scope: Sanity review of the generated Bupa held-out R6 performance outputs. No rerun. No scoring change.

## Final status

**Pass** — the row counts, lane assignment, and tier-distribution shape reported in R7's closeout (`R6_bupa_performance_outputs_2026-05-19.md`) are consistent with R6's frozen scoring contract. No R6 scoring rules, caps, lane mapping, or tier boundaries need to change.

Conditional on two points (see §5 / §6 caveats): (a) the 21st row's provenance — R1's earlier note reported only 20 successful transcripts (`manyi_tan` failed), and the corrected pipeline closeout `bupa_corrected_pipeline_run_2026-05-19.md` is not in my local snapshot, so I cannot independently verify how `manyi_tan` was recovered; (b) the actual CSVs at `data/heldout/bupa/performance/` are also not in my local snapshot — my sign-off relies on R7's closeout report being accurate.

## 1. Row-count check

| File | Expected | Reported | Status |
|---|---:|---:|---|
| `data/heldout/bupa/performance/per_submission.csv` | 21 | 21 | 
| `data/heldout/bupa/performance/per_tester.csv` | 21 | 21 | 

`per_submission` == `per_tester` count is expected, since each Bupa tester has exactly one submission in this held-out set.

Discrepancy to flag (not blocking): R1's data-prep closeout reported 20/21 successful transcripts (`manyi_tan` AWS Transcribe failure). R7's corrected-pipeline closeout reports 21 rows. R8 should briefly confirm against `bupa_corrected_pipeline_run_2026-05-19.md` that `manyi_tan` was recovered (re-run, alternative source, or removed-and-replaced). If not recovered, the 21st row's provenance needs a one-line explanation in the Final Report data section.

## 2. Lane check

| Check | Result |
|---|---|
| `cross_check_lane == with_overrides` for all 21 submissions (per_submission.csv) |  Reported by R7 |
| `cross_check_lanes` in per_tester.csv contains only `with_overrides` | Implied by submission-level check (1 submission per tester) |
| Any `dev_only` / `raw_only` rows? | None reported |

This matches the Stage 1 prediction: `project=web-health-information-bupa` maps to `with_overrides` (line 70 of `src/tracking/performance_model.py`). No upstream `bupa-uk` key leakage into the `project` column.

## 3. Tier interpretation — `_summary.csv` tier ≠ R6 `tier`

These two columns share the name `tier` but are **not the same construct**. Calling this out for R8 / Final Report so the two are not conflated:

- **`data/heldout/bupa/reports/_summary.csv` `tier`** — product/session quality tier. Fused from the reports pipeline (L1 / L2 / L3 evidence about the session/product). Answers: *how clean was this session as a recording / how rich is the captured evidence?*
- **`data/heldout/bupa/performance/per_submission.csv` `tier`** (and per_tester.csv) — tester-performance score tier. Composite of D1 narration × D2 friction surfacing × D3 recording, with severity caps applied. Answers: *how well did this tester surface friction in this submission?*

Concretely, a session can be tagged low-quality at the report level (poor recording, sparse evidence) while the tester still earns a Leading R6 tier because they clearly surfaced serious friction (S1/S2 signals with aligned narration). The opposite can also happen — a clean-recorded session where the tester narrated little earns a Developing/Foundational R6 tier despite a healthy report-quality tier.

R8: when narrating Bupa results, label these explicitly as **"report quality tier"** vs **"R6 tester-performance tier"**. Do not refer to either as just "tier" in cross-table prose.

## 4. Sanity check against R7's reported distribution

R7's closeout reports for per_submission == per_tester:

| R6 tier | Count | Notes |
|---|---:|---|
| Leading | 14 | Score ≥ 85, no cap or cap ≥ raw |
| Proficient | 2 | Score 70–84.9 |
| Developing | 5 | Score 55–69.9 — four are at exactly 55.0 (S1 cap), one at 65.0 (≥2 S2 cap) |
| Foundational | 0 | None |

Cross-checks against `performance_model.py`:

- All four 55.0 rows show `cap_reasons = ["S1 project-level blocker present"]` → consistent with the `S1 ≥ 1 → cap at 55.0` rule (line 247).
- The 65.0 row shows `cap_reasons = [">=2 S2 task-blockers"]` → consistent with the `S2 ≥ 2 → cap at 65.0` rule (line 248).
- The 5 Developing rows landing at exactly the cap values (55.0, 65.0) is expected behaviour: the cap binds because the uncapped composite would have been higher. No tier-boundary drift.
- `low_evidence = 0` → no Bupa row had `total_windows < 5`. All 21 rows are scored cleanly.

R6 scoring rules, caps, lane mapping, and tier boundaries — all unchanged. 

## 5. Layer 1 flags caveat 

`data/heldout/bupa/processed/layer1_flags.csv` was **not regenerated** for the Bupa held-out run. R7 ran `build_performance_tracking.py` without a `--layer1-flags-csv` input.

Effect on R6 scoring:

- D3 recording score (`_d3_recording`, lines 193–205) takes `duration_anomaly` as input. Without Layer 1 flags, `duration_anomaly=False` is assumed for every Bupa video.
- The only path this gates is the secondary clamp `if duration_anomaly: base = min(base, 60.0)`. So if a Bupa video has `recording_quality=good` (D3=90.0) but is also duration-anomalous, the Bupa run will score D3=90.0 instead of 60.0.
- Net effect: a small **upward bias** on D3 for any Bupa video that would have tripped duration anomaly. Order of magnitude bounded — at most a ~4.5-point swing on the composite (D3 carries 15% weight × 30-point D3 delta = 4.5). For most rows the recording_quality alone is the binding factor.

**Important:** this is a held-out-input limitation, **not** an R6 scoring change. The fix lives in regenerating Layer 1 flags for Bupa, not in adjusting D3 logic.

R8: state this as a caveat under "limitations of Bupa external validation," not as a finding about D3.

## 6. Caveats summary 

1. **Trajectory columns are vacuous for Bupa.** `per_tester.csv` has 21 rows × 1 submission each → `direction = None`, `delta_first_to_last = None`, `persistent_friction_types = []` for every row. Bupa supports submission-level external validation only, not longitudinal/trajectory validation.
2. **Tier label hygiene.** Always distinguish "report quality tier" (`reports/_summary.csv`) from "R6 tester-performance tier" (`performance/*.csv`). Same column name, different semantics.
3. **Layer 1 flags missing.** D3 may be slightly upward-biased for any Bupa video with duration anomaly (see §5). Caveat only; do not retune D3.
4. **21-row provenance.** R1 reported 20 successful transcripts; R7 reports 21 rows. R8 to confirm the recovery path for `manyi_tan` (or whichever video was the 21st) against the corrected-pipeline closeout note.
5. **Cap distribution.** The lowest-tier Bupa rows are pinned at exactly 55.0 / 65.0 because R6 severity caps are biting (S1, ≥2 S2). This is **working as designed** under W9 lock-in; do not interpret it as score compression that needs retuning.
6. **Independent CSV verification deferred.** The Bupa performance CSVs and the corrected-pipeline closeout note are not present in my local snapshot. This review uses R7's closeout report as the source of truth for row counts, lane values, and the tier distribution. If R8 wants belt-and-braces verification, a quick `wc -l` and `awk -F, '{print $NF}' | sort | uniq -c` on the lane column of each CSV will confirm in seconds.

## 7. Sign-off line

R6 layer outputs are pass subject to caveats. No scoring change. Ready to be referenced in Final Report as Bupa submission-level external validation of the R6 tester-performance scoring contract.
