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

    assessment = VideoAssessment(
        narration_quality="sparse",
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
