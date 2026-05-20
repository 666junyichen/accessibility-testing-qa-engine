# Layer 1 Design — Audio/Video Features and Rule Detector

**Scope.** This document specifies the Layer 1 (L1) pipeline of the Intelligent Tester
Quality Assessment system: per-window audio feature extraction, per-video metadata
derivation, and the four hard-threshold rules that emit `layer1_flags.csv`. It
complements [README §3.1](../README.md) (interface and usage) by recording the *why*
— feature provenance, threshold derivation, and the contract with downstream fusion.

**Audience.** New contributors who need to understand L1 logic without
reading source, and Final Report reviewers cross-checking design against
measurements. Cross-reference: W9 Progress Report §1.2.

---

## 1. Audio Features (Window-Level)

[`src/preprocessing/audio_features.py`](../src/preprocessing/audio_features.py)
operates on each 60-second window emitted by the splitter. MP4 is extracted
to 16 kHz mono WAV via ffmpeg; Librosa then computes short-term frame energy
(2048-sample frame, 512-sample hop). The output `data/processed/audio_features.csv`
contains **five** features per window:

| Feature | Definition | Source |
|---|---|---|
| `silence_ratio` | Fraction of frames with energy below `SILENCE_ENERGY_THRESHOLD` | Librosa frame energy |
| `narration_density` | `1 − silence_ratio` | Derived |
| `avg_silence_duration` | Mean run-length (seconds) of consecutive silent frames | Librosa frame energy |
| `words_per_minute` | `pronunciation_token_count / (window_duration / 60)` | Window splitter + items.csv |
| `avg_confidence` | Mean of `confidence` over `pronunciation`-type items within `[start_time, end_time]` | AWS Transcribe items.csv |

`SILENCE_ENERGY_THRESHOLD` is exposed as a module constant (currently `0.001`),
intentionally tunable because some testers record at unusually low input
gain and the silence detector must adapt without rewriting the function body.

**Note on Layer 2 features.** `unique_words_ratio` and `avg_sentence_length`
are L2 text features computed by
[`src/layer2/feature_engineering.py`](../src/layer2/feature_engineering.py)
from transcript tokens; together with the five audio features above they
form L2's seven-dimensional clustering matrix. Out of scope here.

---

## 2. Video Metadata (Video-Level)

[`src/preprocessing/video_metadata.py`](../src/preprocessing/video_metadata.py)
extracts video-level metadata via ffprobe (duration, resolution, file size) and,
importantly, computes a single comparative quantity used by the L1 detector:

```
duration_ratio = actual_video_duration / Σ (task Timeguide minutes for the project)
```

Tasks are matched to the video by project (directory name). Each `Timeguide`
field is parsed for an integer plus a unit token; values containing `'second'`
are divided by 60, otherwise treated as minutes. Null and zero denominators
are guarded (`pd.notna` + `total_minutes > 0`); when the guard trips,
`duration_ratio` stays `None` and the row is skipped rather than flagged.

**Why a ratio rather than absolute duration.** Task length varies across
the three dev projects (AAMI, UQ, DPC-WA), so an absolute "video too short"
threshold cannot be project-agnostic; a ratio normalises against expected
workload and lets a single threshold pair generalise.

**Why the sum of all tasks rather than a per-task denominator.** An early
implementation used the Timeguide of a single matched task as the denominator.
This produced 12 false positives in the 15 development samples — most testers
complete several tasks in one recording, so dividing by one task understates
expected duration. Switching to the project-wide Timeguide sum reduced false
positives to 3, all genuine partial-completion sessions
(W9 Progress Report §1.2.1).

---

## 3. Layer 1 Rule Detector

[`src/layer1/rule_detector.py`](../src/layer1/rule_detector.py) applies four
hard-threshold rules and writes one row per triggered flag to
`data/processed/layer1_flags.csv`. Thresholds live in the module-level
`THRESHOLDS` dict; the values below reflect the current (v2) calibration.

| Rule | Granularity | Trigger | L3 fusion impact |
|---|---|---|---|
| `DURATION_ANOMALY` | Video | `duration_ratio < 0.3` or `> 3.0` | Caps `quality_tier` (good → acceptable; see §5) |
| `EXCESSIVE_SILENCE` | Window | `silence_ratio > 0.6` | Audit-only |
| `LOW_AUDIO_QUALITY` | Window | `avg_confidence < 0.75` | Audit-only |
| `SPARSE_NARRATION` | Window | `narration_density < 0.3` | Audit-only |

Each row in `layer1_flags.csv` records `video_filename`, `tester_name`,
`project`, `flag`, `detail` (the triggering value plus its threshold as a
human-readable string), `window_id`, `start_time`, `end_time`, and `value`.
Video-level `DURATION_ANOMALY` rows leave the three window fields null.

**Only `DURATION_ANOMALY` can change `quality_tier`, and only by capping a
good-base session to acceptable.** The other three rules are audit signals:
they appear in QualityReport JSON for manual review but do not gate any
session-level decision. The cap mechanism is detailed in §5.

---

## 4. Threshold Evolution

| Version | Commit | Date | Change | Total flags |
|---|---|---|---|---|
| v1 | `653b239` | 2026-04-12 | Initial calibration from manual inspection of 6 dev samples | 214 |
| v2 | `ae92fb2` | 2026-04-22 | `LOW_AUDIO_QUALITY` 0.7 → 0.75; `SPARSE_NARRATION` 0.2 → 0.3; other two thresholds unchanged | 278 |

Decision rationale for v2 is documented through the 876-window p10 percentile
reasoning and six-sample precision/recall validation summary. v2 has been
retained; no rollback is recommended.

The v2 flag distribution across the 55-video dev set:

| Flag | Count |
|---|---:|
| `EXCESSIVE_SILENCE` | 132 |
| `SPARSE_NARRATION` | 78 |
| `LOW_AUDIO_QUALITY` | 65 |
| `DURATION_ANOMALY` | 3 |

The lopsided `EXCESSIVE_SILENCE` count comes entirely from `terryaflint17`,
an already-confirmed sparse-speech case. `DURATION_ANOMALY`'s three flags are
all genuine partial-completion sessions — see §5.

---

## 5. Fusion Downstream (P2#7)

The fusion module
([`src/pipeline/fusion.py`](../src/pipeline/fusion.py), lines 218–222)
consumes the L1 flag table together with Layer 3 outputs to compute a
per-video `quality_tier`. Of the four L1 flags, only `DURATION_ANOMALY`
participates in tier determination:

```
if base_tier == "good" and any(flag == "DURATION_ANOMALY"):
    quality_tier = "acceptable"
    reasoning += ["duration anomaly caps session confidence"]
```

This is a confidence cap, not a hard gate. From a good base, a
duration-anomalous session is downgraded to acceptable; from acceptable or
poor bases, the cap is a no-op. Sessions with both duration anomaly and
substantial Layer 3 evidence remain visible to reviewers rather than being
silently demoted.

**Why a cap rather than a gate.** Short partial-completion videos can still
surface genuine friction findings; suppressing them entirely would discard
evidence.

**Empirical cap activations.** Three sessions in dev55 trigger the cap:
`carlpatrickrobinson_suncorp` (`duration_ratio = 0.144`),
`carlpatrickrobinson_uq` (0.146), and `jenniferparry7_uq` (0.159) — all
partial-completion recordings.

**Ablation evidence.** Removing L1 entirely did not change tier distribution
on dev55 (matches the Full baseline of 0 good / 15 acceptable / 40 poor),
since L3 evidence already determined those tiers and the cap was redundant.
In the No-L3 ablation, however — where 52 videos default to `good` — the cap
pulls 3 of them to `acceptable`, isolating where DURATION_ANOMALY actually
matters (W9 PR §1.2.3).

**Future direction.** With friction-type Cohen's κ = 0.7407 reached at W8
(W9 PR §1.6.2), upgrading `DURATION_ANOMALY` from soft cap to hard gate
may be evaluated once L3 evidence stability is confirmed by the dev55
ablation rerun and third-round full-sample clustering. No change is planned
within the current freeze protocol.

---

*Source of truth for thresholds and formulas:
[`src/layer1/rule_detector.py`](../src/layer1/rule_detector.py) and
[`src/preprocessing/audio_features.py`](../src/preprocessing/audio_features.py).*
