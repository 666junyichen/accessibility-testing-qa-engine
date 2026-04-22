import csv
import os
import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from layer3.llm_classifier import (  # noqa: E402
    BatchSummary,
    ClassificationResult,
    VideoInput,
    WindowInput,
    batch_classify_videos,
    batch_classify_windows,
)
from layer3.schemas_a import FindingsOutput  # noqa: E402
from layer3.schemas_b import VideoAssessment  # noqa: E402


def _window(window_id):
    return WindowInput(
        window_id=window_id,
        project="department-of-premier-and-cabinet-wa",
        video_id="video-1",
        window_text="window text",
        task_title="Task",
        task_instructions="Instructions",
    )


def _ok_finding_result(input_tokens=100, output_tokens=50):
    return ClassificationResult(
        output=FindingsOutput(findings=[]),
        flag="ok",
        raw_text='{"findings":[]}',
        usage={"input_tokens": input_tokens, "output_tokens": output_tokens},
        error=None,
        latency_ms=12,
    )


def _result(flag):
    output = FindingsOutput(findings=[]) if flag == "ok" else None
    return ClassificationResult(
        output=output,
        flag=flag,
        raw_text="{}",
        usage={"input_tokens": 100, "output_tokens": 50},
        error=None if flag == "ok" else flag,
        latency_ms=5,
    )


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_batch_classify_windows_dry_run_writes_mock_outputs(tmp_path, monkeypatch):
    mock_classify = Mock()
    monkeypatch.setattr("layer3.llm_classifier.classify_finding_level", mock_classify)
    output_csv = tmp_path / "out.csv"
    checkpoint_csv = tmp_path / "checkpoint.csv"

    summary = batch_classify_windows(
        [_window("w1"), _window("w2"), _window("w3")],
        output_csv=str(output_csv),
        checkpoint_csv=str(checkpoint_csv),
        dry_run=True,
        max_concurrency=1,
    )

    assert isinstance(summary, BatchSummary)
    assert summary.total == 3
    assert summary.succeeded == 3
    assert len(_read_csv(output_csv)) == 3
    assert mock_classify.call_count == 0


def test_batch_classify_windows_skips_checkpointed_ids(tmp_path, monkeypatch):
    mock_classify = Mock(return_value=_ok_finding_result())
    monkeypatch.setattr("layer3.llm_classifier.classify_finding_level", mock_classify)
    output_csv = tmp_path / "out.csv"
    checkpoint_csv = tmp_path / "checkpoint.csv"
    checkpoint_csv.write_text(
        "window_id,flag,timestamp_utc\nw1,ok,2026-04-22T00:00:00Z\n"
        "w2,schema_violation,2026-04-22T00:00:01Z\n",
        encoding="utf-8",
    )

    summary = batch_classify_windows(
        [_window("w1"), _window("w2"), _window("w3")],
        output_csv=str(output_csv),
        checkpoint_csv=str(checkpoint_csv),
        max_concurrency=1,
    )

    assert summary.total == 1
    assert mock_classify.call_count == 1
    assert _read_csv(output_csv)[0]["window_id"] == "w3"


def test_batch_classify_windows_cost_tracking(tmp_path, monkeypatch):
    mock_classify = Mock(return_value=_ok_finding_result(100, 50))
    monkeypatch.setattr("layer3.llm_classifier.classify_finding_level", mock_classify)

    summary = batch_classify_windows(
        [_window(f"w{i}") for i in range(4)],
        output_csv=str(tmp_path / "out.csv"),
        checkpoint_csv=str(tmp_path / "checkpoint.csv"),
        max_concurrency=1,
    )

    assert summary.total_input_tokens == 400
    assert summary.total_output_tokens == 200
    assert summary.estimated_cost_usd == pytest.approx(0.00035)


def test_batch_classify_windows_counts_flags_and_excludes_api_error_checkpoint(
    tmp_path, monkeypatch
):
    mock_classify = Mock(
        side_effect=[
            _result("ok"),
            _result("ok"),
            _result("ok"),
            _result("schema_violation"),
            _result("api_error"),
        ]
    )
    monkeypatch.setattr("layer3.llm_classifier.classify_finding_level", mock_classify)

    summary = batch_classify_windows(
        [_window(f"w{i}") for i in range(5)],
        output_csv=str(tmp_path / "out.csv"),
        checkpoint_csv=str(tmp_path / "checkpoint.csv"),
        max_concurrency=1,
    )

    assert summary.succeeded == 3
    assert summary.schema_violation == 1
    assert summary.api_error == 1
    checkpoint_rows = _read_csv(tmp_path / "checkpoint.csv")
    assert len(checkpoint_rows) == 4
    assert {row["flag"] for row in checkpoint_rows} == {"ok", "schema_violation"}


def test_batch_classify_windows_max_concurrency_one_calls_each_window(tmp_path, monkeypatch):
    mock_classify = Mock(return_value=_ok_finding_result())
    monkeypatch.setattr("layer3.llm_classifier.classify_finding_level", mock_classify)

    summary = batch_classify_windows(
        [_window("w1"), _window("w2")],
        output_csv=str(tmp_path / "out.csv"),
        checkpoint_csv=str(tmp_path / "checkpoint.csv"),
        max_concurrency=1,
    )

    assert summary.total == 2
    assert mock_classify.call_count == 2
    assert [call.kwargs["window_id"] for call in mock_classify.call_args_list] == [
        "w1",
        "w2",
    ]


def test_batch_classify_videos_basic_path(tmp_path, monkeypatch):
    video_output = VideoAssessment(
        narration_quality="adequate",
        recording_quality="good",
        coaching_evidence="none",
    )
    mock_classify = Mock(
        return_value=ClassificationResult(
            output=video_output,
            flag="ok",
            raw_text=video_output.model_dump_json(),
            usage={"input_tokens": 100, "output_tokens": 50},
            error=None,
            latency_ms=8,
        )
    )
    monkeypatch.setattr("layer3.llm_classifier.classify_video_level", mock_classify)

    summary = batch_classify_videos(
        [
            VideoInput(
                video_id="v1",
                project="wa",
                task_title="Task",
                aggregated_transcript="full transcript",
            )
        ],
        output_csv=str(tmp_path / "out.csv"),
        checkpoint_csv=str(tmp_path / "checkpoint.csv"),
        max_concurrency=1,
    )

    assert summary.succeeded == 1
    rows = _read_csv(tmp_path / "out.csv")
    assert len(rows) == 1
    assert rows[0]["window_id"] == "v1"
