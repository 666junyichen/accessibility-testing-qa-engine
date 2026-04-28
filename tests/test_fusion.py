import pandas as pd

from src.pipeline.fusion import fuse_video


def _windows(n=6):
    return pd.DataFrame(
        {
            "window_id": [f"video1_w{i:03d}" for i in range(n)],
            "video_id": ["video1"] * n,
            "start_time": [i * 60.0 for i in range(n)],
            "end_time": [(i + 1) * 60.0 for i in range(n)],
            "duration": [60.0] * n,
            "text": ["sample text"] * n,
            "word_count": [20] * n,
            "segment_ids": ["0"] * n,
            "project": ["project-a"] * n,
            "video_filename": ["video1.mp4"] * n,
            "tester_name": ["tester-a"] * n,
        }
    )


def _l1_flags(include_duration_anomaly=True):
    rows = [
        {
            "video_filename": "video1.mp4",
            "tester_name": "tester-a",
            "project": "project-a",
            "flag": "LOW_AUDIO_QUALITY",
            "detail": "avg_confidence=0.5",
            "window_id": "video1_w001",
            "start_time": 60.0,
            "end_time": 120.0,
            "value": 0.5,
        },
    ]
    if include_duration_anomaly:
        rows.append(
            {
                "video_filename": "video1.mp4",
                "tester_name": "tester-a",
                "project": "project-a",
                "flag": "DURATION_ANOMALY",
                "detail": "duration_ratio=0.2",
                "window_id": None,
                "start_time": None,
                "end_time": None,
                "value": 0.2,
            }
        )
    return pd.DataFrame(rows)


def _l2_assignments():
    return pd.DataFrame(
        {
            "window_id": ["video1_w000", "video1_w001", "video1_w002", "video1_w003"],
            "video_id": ["video1"] * 4,
            "tester_name": ["tester-a"] * 4,
            "project": ["project-a"] * 4,
            "kmeans_cluster_id": [2, 2, 1, 2],
            "dbscan_cluster_id": [0, 0, 1, 0],
            "primary_cluster_id": [2, 2, 1, 2],
        }
    )


def _finding(
    window_id="video1_w000",
    severity_s="S4",
    calibrator_score_l="L3",
    friction_type="F6",
    sentiment_e="E3",
):
    return {
        "window_id": window_id,
        "friction_type": friction_type,
        "severity_s": severity_s,
        "sentiment_e": sentiment_e,
        "calibrator_score_l": calibrator_score_l,
        "signal_alignment": "aligned",
        "finding": f"{severity_s} finding",
        "observed_signal": "participant hesitated",
        "stated_signal": "this is confusing",
        "rationale": "Observed and stated signals align.",
        "structural_amplification_note": None,
    }


def _assessment(**overrides):
    data = {
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    }
    data.update(overrides)
    return data


def test_fuse_video_happy_path():
    findings = pd.DataFrame(
        [
            _finding("video1_w000", severity_s="S4", calibrator_score_l="L3"),
            _finding("video1_w002", severity_s="S3", calibrator_score_l="L5"),
        ]
    )

    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=_l1_flags(include_duration_anomaly=False),
        l2_assignments=_l2_assignments(),
        l3_findings=findings,
        l3_assessment=_assessment(),
    )

    assert report.video_id == "video1"
    assert report.project == "project-a"
    assert report.tester_name == "tester-a"
    assert report.total_windows == 6
    assert report.duration_sec == 360.0
    assert report.l1.flag_counts == {"LOW_AUDIO_QUALITY": 1}
    assert report.l1.duration_anomaly is False
    assert report.l2.coverage == 4 / 6
    assert report.l2.dominant_cluster_id == 2
    assert report.l2.dominant_cluster_pct == 3 / 4
    assert report.l2.cluster_distribution == {"1": 1, "2": 3}
    assert report.l3_findings.total_findings == 2
    assert report.l3_findings.top_severity == "S3"
    assert report.l3_findings.calibrator_aggregate == "L5"
    assert [item["severity_s"] for item in report.l3_findings.top_findings] == ["S3", "S4"]
    assert report.overall.quality_tier == "good"


def test_duration_anomaly_caps_base_good_to_acceptable():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=_l1_flags(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame(),
        l3_assessment=_assessment(),
    )

    assert report.l1.duration_anomaly is True
    assert report.overall.quality_tier == "acceptable"
    assert report.overall.reasoning == [
        "no major quality concerns detected",
        "duration anomaly caps session confidence",
    ]


def test_duration_anomaly_does_not_override_base_poor():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=_l1_flags(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame([_finding(severity_s="S2")]),
        l3_assessment=_assessment(),
    )

    assert report.l1.duration_anomaly is True
    assert report.overall.quality_tier == "poor"
    assert report.overall.reasoning == ["task-blocking friction: S1/S2 present"]


def test_recording_poor_downgrades_to_poor():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame(),
        l3_assessment=_assessment(recording_quality="poor"),
    )

    assert report.overall.quality_tier == "poor"
    assert report.overall.reasoning == ["recording unusable"]


def test_s1_or_s2_finding_downgrades_to_poor():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame([_finding(severity_s="S2")]),
        l3_assessment=_assessment(),
    )

    assert report.overall.quality_tier == "poor"
    assert report.overall.reasoning == ["task-blocking friction: S1/S2 present"]


def test_many_findings_downgrades_to_acceptable():
    findings = pd.DataFrame(
        [_finding(window_id=f"video1_w{i:03d}", severity_s="S4") for i in range(5)]
    )

    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=findings,
        l3_assessment=_assessment(),
    )

    assert report.overall.quality_tier == "acceptable"
    assert report.overall.reasoning == ["multiple medium-severity findings"]


def test_l2_missing_produces_empty_summary_no_crash():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame([_finding()]),
        l3_assessment=_assessment(),
    )

    assert report.l2.coverage == 0.0
    assert report.l2.dominant_cluster_id is None
    assert report.l2.dominant_cluster_pct is None
    assert report.l2.cluster_distribution == {}


def test_no_l3_findings_yields_none_aggregates():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame(),
        l3_assessment=_assessment(),
    )

    assert report.l3_findings.total_findings == 0
    assert report.l3_findings.by_friction_type == {}
    assert report.l3_findings.by_severity == {}
    assert report.l3_findings.by_sentiment == {}
    assert report.l3_findings.by_calibrator_score == {}
    assert report.l3_findings.top_severity is None
    assert report.l3_findings.calibrator_aggregate is None
    assert report.l3_findings.top_findings == []


def test_l3_findings_with_null_optional_enums_are_ignored_in_ranked_counts():
    findings = pd.DataFrame(
        [
            _finding("video1_w000", severity_s="S4", calibrator_score_l="L3"),
            _finding(
                "video1_w001",
                severity_s=None,
                calibrator_score_l=None,
                friction_type=None,
                sentiment_e="E2",
            ),
        ]
    )

    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=findings,
        l3_assessment=_assessment(),
    )

    assert report.l3_findings.total_findings == 2
    assert report.l3_findings.by_friction_type == {"F6": 1}
    assert report.l3_findings.by_severity == {"S4": 1}
    assert report.l3_findings.by_calibrator_score == {"L3": 1}
    assert report.l3_findings.top_severity == "S4"
    assert report.l3_findings.calibrator_aggregate == "L3"


def test_coaching_recommendations_integrated():
    report = fuse_video(
        video_id="video1",
        windows=_windows(),
        l1_flags=pd.DataFrame(),
        l2_assignments=pd.DataFrame(),
        l3_findings=pd.DataFrame(),
        l3_assessment=_assessment(narration_quality="sparse", coaching_evidence="explicit"),
    )

    triggers = {
        (item["trigger_field"], item["trigger_value"])
        for item in report.coaching_recommendations
    }
    assert ("narration_quality", "sparse") in triggers
    assert ("coaching_evidence", "explicit") in triggers
