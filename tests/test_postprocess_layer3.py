import json

import pandas as pd

from src.layer3.postprocess import (
    filter_failed_rows,
    unpack_level_a,
    unpack_level_b,
)


def _windows():
    return pd.DataFrame(
        {
            "window_id": ["v1_w000", "v1_w001", "v2_w000"],
            "video_id": ["v1", "v1", "v2"],
            "project": ["project-a", "project-a", "project-b"],
            "tester_name": ["tester-a", "tester-a", "tester-b"],
        }
    )


def _finding(friction_type="F6", severity_s="S3", sentiment_e="E3"):
    return {
        "finding": "Participant encountered a navigation issue.",
        "observed_signal": "Participant hesitated on the page.",
        "stated_signal": "I cannot find it.",
        "signal_alignment": "aligned",
        "friction_type": friction_type,
        "severity_s": severity_s,
        "sentiment_e": sentiment_e,
        "calibrator_score_l": "L4",
        "rationale": "Observed and stated signals indicate friction.",
        "structural_amplification_note": None,
    }


def _raw_row(item_id, output_json, flag="ok"):
    return {
        "window_id": item_id,
        "flag": flag,
        "output_json": json.dumps(output_json),
        "input_tokens": 1,
        "output_tokens": 1,
        "latency_ms": 1,
        "error": None,
        "timestamp_utc": "2026-04-23T00:00:00Z",
    }


def test_unpack_level_a_flattens_findings():
    raw = pd.DataFrame(
        [
            _raw_row("v1_w000", {"findings": [_finding("F1"), _finding("F2")]}),
            _raw_row("v1_w001", {"findings": []}),
        ]
    )

    result = unpack_level_a(raw, _windows())

    assert len(result) == 2
    assert result["friction_type"].tolist() == ["F1", "F2"]
    assert result.columns.tolist() == [
        "window_id",
        "video_id",
        "project",
        "tester_name",
        "friction_type",
        "severity_s",
        "sentiment_e",
        "calibrator_score_l",
        "signal_alignment",
        "finding",
        "observed_signal",
        "stated_signal",
        "rationale",
        "structural_amplification_note",
    ]


def test_unpack_level_a_joins_video_metadata():
    raw = pd.DataFrame([_raw_row("v2_w000", {"findings": [_finding()]})])

    result = unpack_level_a(raw, _windows())

    row = result.iloc[0]
    assert row["window_id"] == "v2_w000"
    assert row["video_id"] == "v2"
    assert row["project"] == "project-b"
    assert row["tester_name"] == "tester-b"


def test_unpack_level_b_renames_window_id_to_video_id():
    raw = pd.DataFrame(
        [
            _raw_row(
                "v1",
                {
                    "narration_quality": "rich",
                    "recording_quality": "good",
                    "coaching_evidence": "none",
                },
            )
        ]
    )

    result = unpack_level_b(raw, _windows())

    assert "video_id" in result.columns
    assert "window_id" not in result.columns
    assert result.iloc[0]["video_id"] == "v1"


def test_unpack_level_b_joins_metadata():
    raw = pd.DataFrame(
        [
            _raw_row(
                "v2",
                {
                    "narration_quality": "sparse",
                    "recording_quality": "acceptable",
                    "coaching_evidence": "explicit",
                },
            )
        ]
    )

    result = unpack_level_b(raw, _windows())

    row = result.iloc[0]
    assert row["project"] == "project-b"
    assert row["tester_name"] == "tester-b"
    assert row["narration_quality"] == "sparse"
    assert row["recording_quality"] == "acceptable"
    assert row["coaching_evidence"] == "explicit"


def test_filter_failed_rows_excludes_non_ok():
    raw = pd.DataFrame(
        [
            _raw_row("v1_w000", {"findings": []}, flag="ok"),
            _raw_row("v1_w001", {}, flag="schema_violation"),
            _raw_row("v2_w000", {}, flag="api_error"),
        ]
    )

    ok_df, failed_df = filter_failed_rows(raw)

    assert ok_df["window_id"].tolist() == ["v1_w000"]
    assert failed_df["window_id"].tolist() == ["v1_w001", "v2_w000"]


def test_empty_findings_produce_no_rows():
    raw = pd.DataFrame(
        [
            _raw_row("v1_w000", {"findings": []}),
            _raw_row("v1_w001", {"findings": []}),
        ]
    )

    result = unpack_level_a(raw, _windows())

    assert result.empty
    assert result.columns.tolist() == [
        "window_id",
        "video_id",
        "project",
        "tester_name",
        "friction_type",
        "severity_s",
        "sentiment_e",
        "calibrator_score_l",
        "signal_alignment",
        "finding",
        "observed_signal",
        "stated_signal",
        "rationale",
        "structural_amplification_note",
    ]
