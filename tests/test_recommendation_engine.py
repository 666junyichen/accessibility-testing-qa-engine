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
