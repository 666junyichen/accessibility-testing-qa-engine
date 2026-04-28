# Step 8.2 — Layer Ablation Study

**Author**: R4 Peiyun He
**Date**: 2026-04-28
**Status**: draft v2 (dev55 official scope)

---

## 1. Objective

Quantify the individual contribution of Layer 1 (rule-based detection), Layer 2 (clustering), and Layer 3 (LLM classification + assessment) to the final per-video Quality Tier produced by the Step 6.1 fusion stage.

The study uses the 55 official dev-set reports (`data/processed/reports/dev55_official_list.csv`) as the baseline, and replays `fuse_video()` under three ablation configurations in addition to the baseline. The two videos excluded from the official scope (`troyparnell_suncorp`, `thanoptions_wa`) are transcript-failure / near-empty edge cases and are documented in `docs/step8_1_dev55_scope.md`. A 57-video sensitivity run is available via the `--full-57` flag and summarised briefly in §7.

## 2. Method

### 2.1 Configurations

| Configuration | Treatment |
|---|---|
| **Full** | All four inputs as-is (`l1_flags`, `l2_assignments`, `l3_findings`, `l3_assessment`). Equivalent to current production output. |
| **No-L1** | `l1_flags` replaced by an empty DataFrame; everything else unchanged. |
| **No-L2** | `l2_assignments` replaced by an empty DataFrame; everything else unchanged. |
| **No-L3** | `l3_findings` replaced by an empty DataFrame; `l3_assessment` replaced by a neutral default `{narration_quality: rich, recording_quality: good, coaching_evidence: none}`. |

### 2.2 Metrics

For each configuration, the following per-video aggregates were computed across the dev55 official development set:

- Final `quality_tier` distribution (`good` / `acceptable` / `poor`).
- Distribution of `reasoning` strings emitted by `_compute_overall_quality()` in `src/pipeline/fusion.py`.
- Mean L1 flag count and mean L3 finding count per video.
- Number of videos whose tier differs from the Full baseline.

### 2.3 Implementation

`scripts/ablation_study.py` reuses `load_inputs()`, `filter_l1_flags()`, `filter_by_video()`, and `get_assessment_row()` from `scripts/run_pipeline.py` (R7 orchestrator) to keep the input-loading semantics identical to the production pipeline. Per-video raw output is written to `data/processed/ablation_summary.csv` (220 rows = 55 videos × 4 configurations).

## 3. Results

### 3.1 Tier distribution

| Configuration | good | acceptable | poor |
|---|---:|---:|---:|
| Full | 0 | 15 | 40 |
| No-L1 | 0 | 15 | 40 |
| No-L2 | 0 | 15 | 40 |
| No-L3 | 55 | 0 | 0 |

### 3.2 Mean signal volume per video

| Configuration | mean L1 flags | mean L3 findings |
|---|---:|---:|
| Full | 5.05 | 38.78 |
| No-L1 | 0.00 | 38.78 |
| No-L2 | 5.05 | 38.78 |
| No-L3 | 5.05 | 0.00 |

### 3.3 Tier change relative to Full

| Configuration | Videos with tier change | % of dev set |
|---|---:|---:|
| No-L1 | 0 / 55 | 0.0% |
| No-L2 | 0 / 55 | 0.0% |
| No-L3 | 55 / 55 | 100.0% |

### 3.4 Reason distribution

| Configuration | Reason | Count |
|---|---|---:|
| Full / No-L1 / No-L2 | task-blocking friction: S1/S2 present | 37 |
| Full / No-L1 / No-L2 | multiple medium-severity findings | 15 |
| Full / No-L1 / No-L2 | recording unusable | 3 |
| No-L3 | no major quality concerns detected | 55 |

## 4. Findings

### 4.1 L1 and L2 currently make zero contribution to the final tier

Removing Layer 1 or Layer 2 produces **identical tier distributions** to the Full baseline (0 / 15 / 40), and **no individual video changes tier** under either ablation. This is consistent with the design recorded in commit `dfe1b0b` (2026-04-23), which describes the fusion as "L1/L2 passthrough + L3 aggregation". `_compute_overall_quality()` in `src/pipeline/fusion.py` consults only `l3_findings` and `l3_assessment`; the L1 and L2 summaries are emitted into the report JSON purely as audit signals.

### 4.2 Current fusion tier decision is L3-dependent under this counterfactual

Removing Layer 3 collapses every video to the `good` default branch of `_compute_overall_quality()`. All 55 videos change tier under this counterfactual, indicating that the current pipeline tier logic depends solely on Layer 3 inputs: any failure in Layer 3 (model regression, prompt drift, transcript starvation) would propagate directly into the final report without a deterministic fallback. The magnitude of this effect should be read jointly with §7, since the No-L3 result is produced under a synthetic neutral assessment rather than a graceful-degradation path.

### 4.3 Layer 1 captures information not exercised by the tier logic

Although L1 has no measurable effect on tier outcomes in the current configuration, the underlying flags do contain signals that the tier logic does not currently consider. The most concrete example within the dev55 scope is `carlpatrickrobinson_suncorp`: its `duration_ratio` is 0.144 (only 14% of the project Timeguide), triggering a `DURATION_ANOMALY` flag in L1, but the final tier under Full is `acceptable` because L3 produced six medium-severity findings without any S1/S2 instances. A structurally invalid recording session is therefore evaluated as a usable artifact under the current fusion logic.

A related pattern is observable in the two excluded edge-case videos (`troyparnell_suncorp`, `thanoptions_wa`, see §7): under the full-57 sensitivity run they are correctly downgraded to `poor` only because L3's `recording_quality` assessment is `poor`. If `recording_quality` were ever wrongly classified as `good` for such a video, neither L1 nor any other layer would intervene.

## 5. Implications

The ablation result is decisive and points to two distinct interpretations, neither of which can be resolved by R4 alone:

1. **Confirm passthrough as final design**. L1 and L2 are accepted as audit-only layers; the team treats Layer 3 as the sole tier signal source. In this reading, the ablation is itself the documentation: it is the empirical evidence that L1/L2 are *intentionally* dormant, and a future report should explain why this redundancy is desirable (cost of LLM evaluation, deterministic re-runs, etc.).

2. **Revise fusion to make L1 a hard gate**. At minimum, `DURATION_ANOMALY` could short-circuit `_compute_overall_quality()` so that any session with `duration_ratio < 0.3` is automatically classified as `poor`. This is a small, well-scoped change and would correct the `carlpatrickrobinson_suncorp` mis-classification highlighted in §4.3. Re-running the ablation under the revised fusion would then quantify the marginal contribution of L1 directly.

Either interpretation is defensible; the choice is a project-level decision that affects the W9 Progress Report narrative. This document is the input to that decision, not the resolution of it.

## 6. Reproducibility

```bash
# Default: dev55 official scope (55 videos)
python scripts/ablation_study.py
# Output: data/processed/ablation_summary.csv (220 rows = 55 x 4)

# Optional sensitivity run on the full 57 videos including the two
# transcript-failure edge cases excluded from the official scope
python scripts/ablation_study.py --full-57
```

The script is deterministic given the inputs in `data/processed/`. A re-run after any change to `fuse_video()` will regenerate `ablation_summary.csv` and the tables in §3.

## 7. Limitations

- The "No-L3" configuration uses a synthetic neutral `l3_assessment`. A more realistic counterfactual would require a non-LLM fallback for `recording_quality`, which does not currently exist. The current No-L3 result therefore represents a worst-case scenario rather than a graceful degradation path. The §4.2 conclusion should be read with this caveat in mind.
- The dev55 development set is dominated by a small number of high-volume testers (notably `terryaflint17`, who alone accounts for the majority of L1 flags). The ablation conclusions about L1's marginal contribution may not generalise to a broader dataset where L1 fires across more independent testers.
- The study evaluates only the final tier; other downstream consumers (e.g. Step 6.2 coaching engine) are unaffected because they read directly from the L3 assessment fields.
- Sensitivity check (`--full-57`): adding the two edge-case videos `troyparnell_suncorp` and `thanoptions_wa` produces an identical qualitative pattern (L1 / L2 still 0 tier changes; No-L3 collapses all videos to `good`); the only quantitative difference is that the Full / No-L1 / No-L2 `poor` count rises from 40 to 42 because both edge cases are flagged as `recording unusable` by L3.

---

**End of draft v2.**
