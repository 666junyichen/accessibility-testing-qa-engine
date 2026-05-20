from src.coaching.recommendation_engine import RecommendationEngine
from src.layer3.schemas_b import VideoAssessment


def test_narration_sparse_triggers_narration_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="sparse",
        recording_quality="good",
        coaching_evidence="none",
    )

    results = engine.generate(assessment)

    assert any(item.category == "narration" for item in results)


def test_narration_rich_does_not_trigger_narration_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="rich",
        recording_quality="good",
        coaching_evidence="none",
    )

    results = engine.generate(assessment)

    assert not any(item.category == "narration" for item in results)


def test_recording_good_does_not_trigger_recording_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="adequate",
        recording_quality="good",
        coaching_evidence="none",
    )

    results = engine.generate(assessment)

    assert not any(item.category == "recording" for item in results)


def test_recording_poor_triggers_recording_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="rich",
        recording_quality="poor",
        coaching_evidence="none",
    )

    results = engine.generate(assessment)

    assert any(item.category == "recording" for item in results)


def test_explicit_coaching_triggers_moderation_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="adequate",
        recording_quality="good",
        coaching_evidence="explicit",
    )

    results = engine.generate(assessment)

    assert any(item.category == "moderation" for item in results)


def test_none_coaching_does_not_trigger_moderation_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="adequate",
        recording_quality="good",
        coaching_evidence="none",
    )

    results = engine.generate(assessment)

    assert not any(item.category == "moderation" for item in results)


def test_results_are_sorted_by_priority_desc():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="none",          # priority 4
        recording_quality="poor",          # priority 5
        coaching_evidence="explicit",      # priority 4
    )

    results = engine.generate(assessment)

    priorities = [item.priority for item in results]
    assert priorities == sorted(priorities, reverse=True)


def test_output_contains_expected_trigger_fields():
    engine = RecommendationEngine()

    # Use narration_quality="adequate" so the meta builder does not fire and
    # the isolated narration / recording recommendations are still emitted.
    # The intent of this test is to verify trigger_field type coverage.
    assessment = VideoAssessment(
        narration_quality="adequate",
        recording_quality="acceptable",
        coaching_evidence="explicit",
    )

    results = engine.generate(assessment)

    trigger_fields = {item.trigger_field for item in results}
    assert "narration_quality" in trigger_fields
    assert "recording_quality" in trigger_fields
    assert "coaching_evidence" in trigger_fields

def test_high_severity_finding_generates_priority_five():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="rich",
        recording_quality="good",
        coaching_evidence="none",
    )

    findings = [
        {
            "finding": "Participant could not complete the task without help.",
            "friction_type": "F6",
            "severity_s": "S2",
            "rationale": "Task blocker.",
        }
    ]

    results = engine.generate(assessment, findings=findings)

    assert results[0].category == "severity"
    assert results[0].trigger_field == "severity_s"
    assert results[0].trigger_value == "S2"
    assert results[0].priority == 5


def test_mid_severity_finding_generates_priority_four():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="rich",
        recording_quality="good",
        coaching_evidence="none",
    )

    findings = [
        {
            "finding": "Participant had repeated difficulty but eventually recovered.",
            "friction_type": "F2",
            "severity_s": "S4",
            "rationale": "High friction but not blocking.",
        }
    ]

    results = engine.generate(assessment, findings=findings)

    assert any(item.category == "severity" for item in results)
    severity_rec = next(item for item in results if item.category == "severity")
    assert severity_rec.trigger_value == "S4"
    assert severity_rec.priority == 4


def test_many_low_severity_findings_generate_low_priority_summary():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="rich",
        recording_quality="good",
        coaching_evidence="none",
    )

    findings = [
        {
            "finding": f"Minor recoverable issue {idx}",
            "friction_type": "F7",
            "severity_s": "S6",
            "rationale": "Low friction.",
        }
        for idx in range(5)
    ]

    results = engine.generate(assessment, findings=findings)

    assert any(item.category == "severity" for item in results)
    severity_rec = next(item for item in results if item.category == "severity")
    assert severity_rec.trigger_value == "S5/S6"
    assert severity_rec.priority == 2


def test_few_low_severity_findings_do_not_generate_severity_recommendation():
    engine = RecommendationEngine()

    assessment = VideoAssessment(
        narration_quality="rich",
        recording_quality="good",
        coaching_evidence="none",
    )

    findings = [
        {
            "finding": "One minor issue occurred but was quickly resolved.",
            "friction_type": "F7",
            "severity_s": "S6",
            "rationale": "Low friction.",
        }
    ]

    results = engine.generate(assessment, findings=findings)

    assert not any(item.category == "severity" for item in results)


# ---------------------------------------------------------------------------
# V3 friction-aggregation builder
# ---------------------------------------------------------------------------

def _aggregation_assessment():
    """Neutral 5.1-B fixture so meta / narration / recording do not fire and
    the friction-aggregation builder can be tested in isolation."""
    return VideoAssessment(
        narration_quality="rich",
        recording_quality="good",
        coaching_evidence="none",
    )


def _make_finding(friction_type: str, severity: str, idx: int = 0) -> dict:
    return {
        "finding": f"Synthetic finding {idx}",
        "friction_type": friction_type,
        "severity_s": severity,
        "rationale": "synthetic",
    }


def test_friction_aggregation_fires_with_three_types_and_non_trivial_severity():
    """V3.1 guards: total>=8, 3 distinct types, >=2 types each have S1-S4,
    top share <=70%. F1=3, F2=3, F6=2 satisfies all four."""
    engine = RecommendationEngine()
    findings = [
        _make_finding("F1", "S2", 1),
        _make_finding("F1", "S3", 2),
        _make_finding("F1", "S4", 3),
        _make_finding("F2", "S2", 4),
        _make_finding("F2", "S3", 5),
        _make_finding("F2", "S5", 6),
        _make_finding("F6", "S3", 7),
        _make_finding("F6", "S5", 8),
    ]
    results = engine.generate(_aggregation_assessment(), findings=findings)

    agg = [r for r in results if r.category == "friction-aggregation"]
    assert len(agg) == 1
    rec = agg[0]
    assert rec.priority == 4
    assert rec.trigger_field == "friction_type_distribution"
    # Stable order: count desc then F-code asc → F1(3), F2(3), F6(2)
    assert rec.trigger_value == "F1,F2,F6"


def test_friction_aggregation_does_not_fire_with_only_two_types():
    engine = RecommendationEngine()
    findings = [
        _make_finding("F1", "S2", i) for i in range(3)
    ] + [_make_finding("F2", "S3", 9), _make_finding("F2", "S3", 10)]
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert not any(r.category == "friction-aggregation" for r in results)


def test_friction_aggregation_does_not_fire_below_total_threshold():
    engine = RecommendationEngine()
    # 4 findings with 3 distinct types — fails total >= 5
    findings = [
        _make_finding("F1", "S2", 1),
        _make_finding("F2", "S3", 2),
        _make_finding("F6", "S4", 3),
        _make_finding("F1", "S5", 4),
    ]
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert not any(r.category == "friction-aggregation" for r in results)


def test_friction_aggregation_does_not_fire_when_all_findings_low_severity():
    engine = RecommendationEngine()
    # 6 findings, 3 distinct types, but everything in S5/S6
    findings = [
        _make_finding("F1", "S5", 1),
        _make_finding("F2", "S5", 2),
        _make_finding("F2", "S6", 3),
        _make_finding("F7", "S6", 4),
        _make_finding("F7", "S6", 5),
        _make_finding("F1", "S6", 6),
    ]
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert not any(r.category == "friction-aggregation" for r in results)


def test_friction_aggregation_handles_missing_fields_without_crashing():
    """NaN / missing / unknown values in finding rows must be silently skipped
    and not crash the builder. With 8 valid rows that satisfy the V3.1 guards
    (3 distinct types, 3 non-trivial-severity types, max share 3/8 = 37.5%),
    aggregation should still fire."""
    engine = RecommendationEngine()
    findings = [
        {"finding": "missing severity"},  # no severity_s
        {"finding": "missing friction", "severity_s": "S2"},  # no friction_type
        {"friction_type": "F4", "severity_s": "??"},  # invalid severity
        _make_finding("F1", "S2", 1),
        _make_finding("F2", "S3", 2),
        _make_finding("F6", "S3", 3),
        _make_finding("F1", "S4", 4),
        _make_finding("F2", "S4", 5),
        _make_finding("F6", "S2", 6),
        _make_finding("F1", "S5", 7),
        _make_finding("F2", "S5", 8),
    ]
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert any(r.category == "friction-aggregation" for r in results)


# ---------------------------------------------------------------------------
# V3 meta builder + suppression behaviour
# ---------------------------------------------------------------------------

def test_meta_fires_and_suppresses_isolated_narration_and_recording():
    engine = RecommendationEngine()
    assessment = VideoAssessment(
        narration_quality="sparse",
        recording_quality="acceptable",
        coaching_evidence="explicit",
    )
    results = engine.generate(assessment)
    categories = {r.category for r in results}

    assert "meta" in categories
    assert "narration" not in categories
    assert "recording" not in categories
    # moderation must still fire — meta does not suppress it
    assert "moderation" in categories
    meta_rec = next(r for r in results if r.category == "meta")
    assert meta_rec.priority == 6
    assert meta_rec.trigger_value == "sparse+acceptable"


def test_meta_does_not_fire_when_recording_is_good():
    engine = RecommendationEngine()
    assessment = VideoAssessment(
        narration_quality="sparse",
        recording_quality="good",
        coaching_evidence="none",
    )
    results = engine.generate(assessment)
    categories = {r.category for r in results}

    # No meta, narration still emits as a standalone item.
    assert "meta" not in categories
    assert "narration" in categories


def test_meta_coexists_with_severity_and_friction_aggregation():
    """All three of meta / severity / friction-aggregation can coexist; meta
    only suppresses isolated narration + recording. Fixture is sized to
    satisfy V3.1 friction-aggregation guards (>=8 valid, 3 distinct types,
    >=2 non-trivial-severity types, top share <=70%)."""
    engine = RecommendationEngine()
    assessment = VideoAssessment(
        narration_quality="none",
        recording_quality="poor",
        coaching_evidence="none",
    )
    findings = [
        _make_finding("F1", "S1", 1),
        _make_finding("F1", "S4", 2),
        _make_finding("F1", "S5", 3),
        _make_finding("F2", "S2", 4),
        _make_finding("F2", "S3", 5),
        _make_finding("F2", "S5", 6),
        _make_finding("F6", "S3", 7),
        _make_finding("F6", "S5", 8),
    ]
    results = engine.generate(assessment, findings=findings)
    categories = {r.category for r in results}

    # Meta suppresses narration + recording but other builders are independent.
    assert "meta" in categories
    assert "severity" in categories
    assert "friction-aggregation" in categories
    assert "narration" not in categories
    assert "recording" not in categories


def test_legacy_single_argument_call_remains_backward_compatible():
    """Calling generate(assessment) without findings must behave exactly like
    the v1 MVP: only narration/recording/moderation builders run, and no
    severity / friction-aggregation items appear."""
    engine = RecommendationEngine()
    assessment = VideoAssessment(
        narration_quality="adequate",   # avoid meta trigger
        recording_quality="acceptable",
        coaching_evidence="explicit",
    )
    results = engine.generate(assessment)
    categories = {r.category for r in results}

    assert categories == {"narration", "recording", "moderation"}


# ---------------------------------------------------------------------------
# V3.1 follow-up tests (peer review convergence)
# ---------------------------------------------------------------------------

def test_friction_aggregation_dominance_guard_blocks_single_pattern():
    """top type share > 70% means single-pattern, even if other types exist."""
    engine = RecommendationEngine()
    findings = [_make_finding("F1", "S2", i) for i in range(8)] + [
        _make_finding("F2", "S2", 9),
        _make_finding("F6", "S3", 10),
    ]
    # 8/10 = 80% > 70% dominance → should NOT fire.
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert not any(r.category == "friction-aggregation" for r in results)


def test_friction_aggregation_fires_when_distribution_is_balanced():
    """Balanced distribution with non-trivial severity in 3 types → fires."""
    engine = RecommendationEngine()
    findings = [
        _make_finding("F1", "S2", 1), _make_finding("F1", "S3", 2),
        _make_finding("F1", "S4", 3), _make_finding("F1", "S5", 4),
        _make_finding("F2", "S2", 5), _make_finding("F2", "S3", 6),
        _make_finding("F2", "S5", 7),
        _make_finding("F6", "S2", 8),
        _make_finding("F6", "S5", 9),
    ]
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert any(r.category == "friction-aggregation" for r in results)


def test_friction_aggregation_blocked_when_only_one_type_has_non_trivial_severity():
    """3 types appear but only F1 carries S1-S4; the other two are pure S5/S6."""
    engine = RecommendationEngine()
    findings = [
        _make_finding("F1", "S2", 1), _make_finding("F1", "S3", 2),
        _make_finding("F1", "S4", 3), _make_finding("F1", "S2", 4),
        _make_finding("F2", "S5", 5), _make_finding("F2", "S6", 6),
        _make_finding("F6", "S5", 7), _make_finding("F6", "S6", 8),
    ]
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert not any(r.category == "friction-aggregation" for r in results)


def test_nan_in_friction_type_and_severity_does_not_crash_or_count():
    """NaN / None in either field → row is silently skipped, not counted."""
    import math
    findings = [
        {"friction_type": math.nan, "severity_s": math.nan, "finding": "x"},
        {"friction_type": None, "severity_s": None, "finding": "y"},
        {"friction_type": "F1", "severity_s": math.nan, "finding": "z"},
        {"friction_type": math.nan, "severity_s": "S2", "finding": "w"},
    ] + [_make_finding("F1", "S2", i) for i in range(8)]  # 8 valid F1
    engine = RecommendationEngine()
    # Should not raise. With 8 valid F1 only (1 distinct type), no aggregation.
    results = engine.generate(_aggregation_assessment(), findings=findings)
    assert not any(r.category == "friction-aggregation" for r in results)


def test_meta_priority_orders_above_moderation_and_coexists():
    """Meta priority 6 must sort above explicit moderation priority 4."""
    engine = RecommendationEngine()
    assessment = VideoAssessment(
        narration_quality="sparse",
        recording_quality="acceptable",
        coaching_evidence="explicit",
    )
    results = engine.generate(assessment)

    # Meta exists, moderation still exists (not suppressed), priorities sorted desc.
    cats = [r.category for r in results]
    assert cats.index("meta") < cats.index("moderation"), (
        "meta priority 6 must precede moderation priority 4"
    )
    priorities = [r.priority for r in results]
    assert priorities == sorted(priorities, reverse=True)
