# Coaching Limitations Summary

This summary consolidates the report-facing points from the R5 supporting
reviews now stored under `need/01_final_report/report_support/` and the final
project-facing design in `docs/coaching_templates.md`.

## What the Current Engine Supports

- Stable schema-compatible coaching recommendations inside each QualityReport.
- High-level categories for severity, friction aggregation, recording, and
  narration.
- Severity-aware recommendations grounded in Layer 3 findings.
- Controlled V3.1 friction-aggregation triggering, which reduced over-broad
  recommendation behaviour.
- Deterministic template output that is reproducible and easy to inspect.

## Main Limitation

The engine is useful as reviewer support, but it is not a fully contextual human
coaching system. Its recommendations remain largely template-based and
session-level.

## Report-safe Caveats

- 5.1-B video-level fields are enough for high-level categories, but not enough
  for timestamp-level coaching.
- `coaching_evidence` is binary and does not distinguish light prompting,
  repeated guidance, or directive intervention.
- Recording recommendations are generally correct but can feel generic.
- Friction-aggregation recommendations are technically valid but sometimes less
  actionable than severity-based recommendations.
- Fine-grained coaching requires Layer 3 finding evidence, window IDs, and
  timestamps rather than video-level labels alone.

## Future Work

- Add timestamp-aware recommendation grounding.
- Add evidence snippets for coaching advice.
- Expand moderator intervention categories beyond binary explicit/none.
- Improve compression for dense sessions with many repeated findings.
- Explore LLM-assisted wording only after the deterministic evidence contract is
  preserved.

