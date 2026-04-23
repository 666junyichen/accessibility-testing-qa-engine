from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.run_pipeline import collect_video_ids, run_one_video


class DummyReport:
    def model_dump(self, mode: str = "json"):
        return {
            "video_id": "vid1",
            "project": "proj",
            "tester_name": "tester",
            "total_windows": 1,
            "duration_sec": 10.0,
            "l1": {},
            "l2": {},
            "l3_findings": {"total_findings": 1},
            "l3_assessment": {
                "recording_quality": "good",
                "narration_quality": "good",
                "coaching_evidence": "none",
            },
            "overall": {
                "quality_tier": "good",
                "reasoning": ["no major quality concerns detected"],
            },
            "coaching_recommendations": [],
        }


def test_collect_video_ids_deduplicates_and_sorts():
    data = {
        "windows": pd.DataFrame({"video_id": ["vid2", "vid1"]}),
        "l1_flags": pd.DataFrame({"video_id": ["vid2", "vid3"]}),
        "l2_assignments": pd.DataFrame({"video_id": ["vid1"]}),
        "l3_findings": pd.DataFrame({"video_id": ["vid3"]}),
        "l3_assessments": pd.DataFrame({"video_id": ["vid2", "vid1"]}),
    }

    result = collect_video_ids(data)

    assert result == ["vid1", "vid2", "vid3"]


def test_run_one_video_success(tmp_path, monkeypatch):
    data = {
        "windows": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "project": ["proj"],
                "tester_name": ["tester"],
                "duration": [10.0],
            }
        ),
        "l1_flags": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "flag": ["DURATION_ANOMALY"],
                "window_id": ["w1"],
            }
        ),
        "l2_assignments": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "primary_cluster_id": [1],
                "window_id": ["w1"],
            }
        ),
        "l3_findings": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "severity_s": ["S3"],
                "calibrator_score_l": ["L2"],
            }
        ),
        "l3_assessments": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "project": ["proj"],
                "tester_name": ["tester"],
                "recording_quality": ["good"],
                "narration_quality": ["good"],
                "coaching_evidence": ["none"],
            }
        ),
    }

    def fake_fuse_video(**kwargs):
        return DummyReport()

    monkeypatch.setattr("scripts.run_pipeline.fuse_video", fake_fuse_video)

    ok = run_one_video("vid1", data, tmp_path)

    assert ok is True
    output_file = tmp_path / "vid1.json"
    assert output_file.exists()

    payload = json.loads(output_file.read_text())
    assert payload["video_id"] == "vid1"
    assert payload["overall"]["quality_tier"] == "good"


def test_run_one_video_skips_when_windows_missing(tmp_path):
    data = {
        "windows": pd.DataFrame(columns=["video_id", "project", "tester_name", "duration"]),
        "l1_flags": pd.DataFrame(),
        "l2_assignments": pd.DataFrame(),
        "l3_findings": pd.DataFrame(),
        "l3_assessments": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "recording_quality": ["good"],
                "narration_quality": ["good"],
                "coaching_evidence": ["none"],
            }
        ),
    }

    ok = run_one_video("vid1", data, tmp_path)

    assert ok is False
    assert not (tmp_path / "vid1.json").exists()


def test_run_one_video_skips_when_assessment_missing(tmp_path):
    data = {
        "windows": pd.DataFrame(
            {
                "video_id": ["vid1"],
                "project": ["proj"],
                "tester_name": ["tester"],
                "duration": [10.0],
            }
        ),
        "l1_flags": pd.DataFrame(),
        "l2_assignments": pd.DataFrame(),
        "l3_findings": pd.DataFrame(),
        "l3_assessments": pd.DataFrame(columns=["video_id"]),
    }

    ok = run_one_video("vid1", data, tmp_path)

    assert ok is False
    assert not (tmp_path / "vid1.json").exists()