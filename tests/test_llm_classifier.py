import json
import os
import sys
from io import BytesIO
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from layer3.llm_classifier import (  # noqa: E402
    ClassificationResult,
    classify_finding_level,
    classify_video_level,
    invoke_bedrock,
)
from layer3.schemas_a import FindingsOutput  # noqa: E402
from layer3.schemas_b import VideoAssessment  # noqa: E402


def _bedrock_response(text, usage=None):
    body = {
        "content": [{"type": "text", "text": text}],
        "usage": usage or {"input_tokens": 10, "output_tokens": 5},
        "stop_reason": "end_turn",
    }
    return {"body": BytesIO(json.dumps(body).encode("utf-8"))}


def _valid_finding_json(extra_field=False):
    finding = {
        "finding": "Participant could not locate the feedback page.",
        "observed_signal": "Participant searched menus without finding the page.",
        "stated_signal": "I'm struggling to find the feedback page.",
        "signal_alignment": "aligned",
        "friction_type": "F6",
        "severity_s": "S4",
        "sentiment_e": "E4",
        "calibrator_score_l": "L3",
        "rationale": "Observed search and stated struggle align with high friction.",
        "structural_amplification_note": None,
    }
    if extra_field:
        finding["evidence_quote"] = "extra field must fail"
    return json.dumps({"findings": [finding]})


def _patch_boto(monkeypatch, client):
    session_cls = Mock()
    session = session_cls.return_value
    session.client.return_value = client
    monkeypatch.setattr("layer3.llm_classifier.boto3.Session", session_cls)
    return session_cls


def test_invoke_bedrock_returns_content_usage_and_stop_reason(monkeypatch):
    client = Mock()
    client.invoke_model.return_value = _bedrock_response('{"findings":[]}')
    session_cls = _patch_boto(monkeypatch, client)

    result = invoke_bedrock([{"role": "user", "content": "hello"}])

    assert result["content"][0]["text"] == '{"findings":[]}'
    assert result["usage"] == {"input_tokens": 10, "output_tokens": 5}
    assert result["stop_reason"] == "end_turn"
    session_cls.assert_called_once_with(profile_name="smp-cs20", region_name="us-east-1")
    client.invoke_model.assert_called_once()


def test_invoke_bedrock_retries_throttling_then_succeeds(monkeypatch):
    client = Mock()
    throttling = ClientError(
        {"Error": {"Code": "ThrottlingException", "Message": "slow down"}},
        "InvokeModel",
    )
    client.invoke_model.side_effect = [
        throttling,
        throttling,
        _bedrock_response('{"findings":[]}'),
    ]
    _patch_boto(monkeypatch, client)
    monkeypatch.setattr("layer3.llm_classifier.time.sleep", Mock())

    result = invoke_bedrock([{"role": "user", "content": "hello"}])

    assert result["content"][0]["text"] == '{"findings":[]}'
    assert client.invoke_model.call_count == 3


def test_classify_finding_level_success(monkeypatch):
    raw = {
        "content": [{"type": "text", "text": _valid_finding_json()}],
        "usage": {"input_tokens": 20, "output_tokens": 30},
    }
    monkeypatch.setattr("layer3.llm_classifier.invoke_bedrock", Mock(return_value=raw))

    result = classify_finding_level(
        window_id="w1",
        project="wa",
        video_id="v1",
        window_text="I cannot find the feedback page.",
        task_title="Feedback",
        task_instructions="Find feedback form.",
    )

    assert isinstance(result, ClassificationResult)
    assert result.flag == "ok"
    assert isinstance(result.output, FindingsOutput)
    assert result.output.findings[0].friction_type == "F6"
    assert result.usage == {"input_tokens": 20, "output_tokens": 30}


def test_classify_finding_level_json_parse_error(monkeypatch):
    raw = {
        "content": [{"type": "text", "text": "not json at all"}],
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    monkeypatch.setattr("layer3.llm_classifier.invoke_bedrock", Mock(return_value=raw))

    result = classify_finding_level("w1", "wa", "v1", "bad", "Task", "Instructions")

    assert result.flag == "json_parse_error"
    assert result.output is None
    assert result.raw_text == "not json at all"
    assert result.error


def test_classify_finding_level_schema_violation_for_extra_field(monkeypatch):
    raw = {
        "content": [{"type": "text", "text": _valid_finding_json(extra_field=True)}],
        "usage": {"input_tokens": 1, "output_tokens": 1},
    }
    monkeypatch.setattr("layer3.llm_classifier.invoke_bedrock", Mock(return_value=raw))

    result = classify_finding_level("w1", "wa", "v1", "text", "Task", "Instructions")

    assert result.flag == "schema_violation"
    assert result.output is None
    assert "evidence_quote" in result.error


def test_classify_video_level_success(monkeypatch):
    raw = {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {
                        "narration_quality": "adequate",
                        "recording_quality": "good",
                        "coaching_evidence": "none",
                    }
                ),
            }
        ],
        "usage": {"input_tokens": 9, "output_tokens": 4},
    }
    monkeypatch.setattr("layer3.llm_classifier.invoke_bedrock", Mock(return_value=raw))

    result = classify_video_level(
        video_id="v1",
        project="wa",
        task_title="Feedback",
        aggregated_transcript="Participant talks through the session.",
    )

    assert result.flag == "ok"
    assert isinstance(result.output, VideoAssessment)
    assert result.output.coaching_evidence == "none"


def test_markdown_fence_json_is_extracted(monkeypatch):
    raw = {
        "content": [{"type": "text", "text": '```json\n{"findings":[]}\n```'}],
        "usage": {"input_tokens": 3, "output_tokens": 3},
    }
    monkeypatch.setattr("layer3.llm_classifier.invoke_bedrock", Mock(return_value=raw))

    result = classify_finding_level("w1", "wa", "v1", "text", "Task", "Instructions")

    assert result.flag == "ok"
    assert result.output.findings == []
