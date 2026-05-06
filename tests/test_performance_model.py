
from __future__ import annotations

import copy

import pytest

from src.tracking.performance_model import (
    aggregate_tester,
    build_per_tester_table,
    score_submission,
    score_submissions_from_csv,
)


def _make_report(**overrides) -> dict:
    base = {
        "video_id": "tester1_proj-a",
        "project": "suncorp-insurance",
        "tester_name": "tester1",
        "total_windows": 60,
        "duration_sec": 3600.0,
        "l1": {
            "flag_counts": {},
            "total_flags": 0,
            "flagged_window_ids": [],
            "duration_anomaly": False,
        },
        "l2": {
            "coverage": 0.0,
            "dominant_cluster_id": None,
            "dominant_cluster_pct": None,
            "cluster_distribution": {},
        },
        "l3_findings": {
            "total_findings": 20,
            "by_friction_type": {"F1": 8, "F2": 6, "F6": 4, "F7": 2},
            "by_severity": {"S3": 5, "S4": 5, "S5": 8, "S6": 2},
            "by_sentiment": {"E3": 8, "E4": 12},
            "by_calibrator_score": {"L2": 14, "L3": 6},
            "signal_alignment_distribution": {"aligned": 19, "stated_missing": 1},
            "top_severity": "S3",
            "calibrator_aggregate": "L2",
        },
        "l3_assessment": {
            "narration_quality": "rich",
            "recording_quality": "acceptable",
            "coaching_evidence": "none",
        },
        "overall": {"quality_tier": "acceptable", "reasoning": []},
    }
    deep = copy.deepcopy(base)
    deep.update(overrides)
    return deep


# ---------------------------------------------------------------------------
# Per-submission scoring
# ---------------------------------------------------------------------------


def test_baseline_submission_lands_in_proficient_or_leading():
    record = score_submission(_make_report())
    assert record.tier in {"Proficient", "Leading"}
    assert 0 <= record.score <= 100
    assert record.cap_applied is None


def test_d1_matches_narration_quality_lookup():
    rich = score_submission(_make_report()).d1_narration
    sparse = score_submission(
        _make_report(
            l3_assessment={
                "narration_quality": "sparse",
                "recording_quality": "acceptable",
                "coaching_evidence": "none",
            }
        )
    ).d1_narration
    assert rich == 90.0
    assert sparse == 55.0


def test_s1_caps_at_55():
    """Any S1 finding caps the submission score at 55 — Foundational floor."""
    report = _make_report()
    report["l3_findings"]["by_severity"] = {"S1": 1, "S5": 19}
    record = score_submission(report)
    assert record.score <= 55.0
    assert any("S1" in r for r in record.cap_reasons)


def test_two_s2_findings_cap_at_65():
    report = _make_report()
    report["l3_findings"]["by_severity"] = {"S2": 2, "S5": 18}
    record = score_submission(report)
    assert record.score <= 65.0
    assert any("S2" in r for r in record.cap_reasons)


def test_one_s2_finding_does_not_trigger_cap():
    report = _make_report()
    report["l3_findings"]["by_severity"] = {"S2": 1, "S5": 19}
    record = score_submission(report)
    # raw is comfortably above 65, so no cap applies
    assert all("S2" not in r for r in record.cap_reasons)


def test_poor_recording_caps_at_70():
    report = _make_report(
        l3_assessment={
            "narration_quality": "rich",
            "recording_quality": "poor",
            "coaching_evidence": "none",
        }
    )
    record = score_submission(report)
    assert record.score <= 70.0
    assert any("poor" in r for r in record.cap_reasons)


def test_no_narration_no_findings_caps_at_40():
    report = _make_report(
        l3_assessment={
            "narration_quality": "none",
            "recording_quality": "acceptable",
            "coaching_evidence": "none",
        }
    )
    report["l3_findings"]["total_findings"] = 0
    report["l3_findings"]["by_severity"] = {}
    report["l3_findings"]["by_friction_type"] = {}
    report["l3_findings"]["by_sentiment"] = {}
    report["l3_findings"]["signal_alignment_distribution"] = {}
    record = score_submission(report)
    assert record.score <= 40.0


def test_low_evidence_flagged_for_short_videos():
    report = _make_report(total_windows=3)
    record = score_submission(report)
    assert record.low_evidence is True


def test_low_evidence_off_for_normal_videos():
    record = score_submission(_make_report(total_windows=20))
    assert record.low_evidence is False


def test_cross_check_lane_uq_is_raw_only():
    record = score_submission(
        _make_report(project="the-university-of-queensland")
    )
    assert record.cross_check_lane == "raw_only"


def test_cross_check_lane_aami_is_with_overrides():
    record = score_submission(_make_report(project="suncorp-insurance"))
    assert record.cross_check_lane == "with_overrides"


def test_top_friction_types_ordered_by_count():
    record = score_submission(_make_report())
    # baseline fixture: F1=8, F2=6, F6=4, F7=2 → top-3 should be F1,F2,F6
    assert record.top_friction_types == ["F1", "F2", "F6"]


def test_calibrator_aggregate_is_audit_only_label():
    record = score_submission(_make_report())
    # weighted mean of {L2: 14, L3: 6} = (2*14 + 3*6) / 20 = 2.3 → round → L2
    assert record.calibrator_aggregate == "L2"


def test_calibrator_aggregate_mismatch_flag_off_for_baseline():
    """Baseline lands Leading with calibrator aggregate L2 (implied Proficient).
    Tier-rank gap = 1 < 2 → no mismatch."""
    record = score_submission(_make_report())
    assert record.tier in {"Proficient", "Leading"}
    assert record.calibrator_aggregate == "L2"
    assert record.calibrator_aggregate_mismatch_flag is False


def test_calibrator_aggregate_mismatch_flag_triggers_when_tier_gap_ge_2():
    """Composite Leading + calibrator L4 (implied Foundational) → gap=3 → flag."""
    report = _make_report()
    report["l3_findings"]["by_calibrator_score"] = {"L4": 14, "L5": 6}
    record = score_submission(report)
    assert record.tier == "Leading"
    assert record.calibrator_aggregate == "L4"
    assert record.calibrator_aggregate_mismatch_flag is True


def test_calibrator_aggregate_mismatch_flag_false_when_aggregate_missing():
    """No calibrator findings → aggregate is None → flag is False (cross-check
    unavailable, not a mismatch)."""
    report = _make_report()
    report["l3_findings"]["by_calibrator_score"] = {}
    record = score_submission(report)
    assert record.calibrator_aggregate is None
    assert record.calibrator_aggregate_mismatch_flag is False


def test_calibrator_aggregate_mismatch_flag_off_at_one_tier_gap():
    """Composite Leading + calibrator L3 (implied Developing) → gap=2 → flag.
    Composite Leading + calibrator L2 (implied Proficient) → gap=1 → no flag."""
    edge_report = _make_report()
    edge_report["l3_findings"]["by_calibrator_score"] = {"L3": 20}
    edge_record = score_submission(edge_report)
    assert edge_record.tier == "Leading"
    assert edge_record.calibrator_aggregate == "L3"
    assert edge_record.calibrator_aggregate_mismatch_flag is True

    safe_report = _make_report()
    safe_report["l3_findings"]["by_calibrator_score"] = {"L2": 20}
    safe_record = score_submission(safe_report)
    assert safe_record.calibrator_aggregate == "L2"
    assert safe_record.calibrator_aggregate_mismatch_flag is False


def test_zero_findings_with_rich_narration_gives_neutral_d2():
    report = _make_report()
    report["l3_findings"]["total_findings"] = 0
    report["l3_findings"]["by_severity"] = {}
    report["l3_findings"]["by_friction_type"] = {}
    report["l3_findings"]["signal_alignment_distribution"] = {}
    record = score_submission(report)
    # §4.2: rich narration + 0 findings → D2 = 50 (neutral)
    assert record.d2_friction_surfacing == 50.0


# ---------------------------------------------------------------------------
# Worked example — guards against silent rule drift
# ---------------------------------------------------------------------------


def test_design_doc_worked_example_sharelinsonny_suncorp():

    report = _make_report(
        video_id="Sharelinsonny_suncorp",
        tester_name="Sharelinsonny",
        project="suncorp-insurance",
        total_windows=81,
    )
    report["l3_findings"]["total_findings"] = 27
    report["l3_findings"]["by_severity"] = {"S2": 2, "S3": 4, "S4": 2, "S5": 19}
    report["l3_findings"]["by_friction_type"] = {
        "F1": 9, "F2": 5, "F3": 1, "F5": 3, "F6": 6, "F7": 3,
    }
    report["l3_findings"]["signal_alignment_distribution"] = {
        "aligned": 26, "stated_missing": 1,
    }
    record = score_submission(report)
    assert record.d1_narration == 90.0
    assert record.d3_recording == 70.0
    assert 83.0 <= record.d2_friction_surfacing <= 85.0
    assert 84.0 <= record.raw_score <= 86.0
    assert record.score == 65.0
    assert record.tier == "Developing"
    assert record.cap_reasons == [">=2 S2 task-blockers"]


# ---------------------------------------------------------------------------
# Per-tester aggregation
# ---------------------------------------------------------------------------


def _three_records_for(tester: str, scores: list[float]):

    records = []
    for i, target_score in enumerate(scores):

        report = _make_report(
            video_id=f"{tester}_proj{i}",
            tester_name=tester,
            project=("suncorp-insurance" if i % 2 == 0 else "the-university-of-queensland"),
        )
        if target_score >= 85:
            report["l3_assessment"]["narration_quality"] = "rich"
        elif target_score >= 70:
            report["l3_assessment"]["narration_quality"] = "rich"
            report["l3_findings"]["total_findings"] = 5
            report["l3_findings"]["by_severity"] = {"S5": 5}
            report["l3_findings"]["signal_alignment_distribution"] = {"aligned": 5}
        elif target_score >= 55:
            report["l3_assessment"]["narration_quality"] = "sparse"
        else:
            report["l3_assessment"]["narration_quality"] = "none"
        records.append(score_submission(report))
    return records


def test_aggregate_tester_requires_consistent_tester_name():
    r1 = score_submission(_make_report(video_id="v1", tester_name="a"))
    r2 = score_submission(_make_report(video_id="v2", tester_name="b"))
    with pytest.raises(ValueError):
        aggregate_tester([r1, r2])


def test_aggregate_tester_single_submission_has_no_direction():
    r1 = score_submission(_make_report(video_id="v1", tester_name="solo"))
    traj = aggregate_tester([r1])
    assert traj.direction is None
    assert traj.delta_first_to_last is None
    assert traj.submission_count == 1


def test_persistent_friction_appears_when_top_friction_recurs():

    r1 = score_submission(_make_report(video_id="v1", tester_name="t"))
    r2 = score_submission(_make_report(video_id="v2", tester_name="t"))
    traj = aggregate_tester([r1, r2])
    assert "F1" in traj.persistent_friction_types


def test_low_evidence_records_excluded_from_trajectory_slope():
    full = score_submission(_make_report(video_id="v1", tester_name="t"))
    short = score_submission(
        _make_report(video_id="v2", tester_name="t", total_windows=2)
    )
    traj = aggregate_tester([full, short])
    # Only one record is "scored"; trajectory direction is undefined.
    assert traj.direction is None
    assert traj.submission_count == 2
    assert traj.submission_count_scored == 1


def test_per_tester_calibrator_aggregate_mismatch_count_rolls_up():
    matched = score_submission(_make_report(video_id="v1", tester_name="t"))
    flagged_report = _make_report(video_id="v2", tester_name="t")
    flagged_report["l3_findings"]["by_calibrator_score"] = {"L4": 14, "L5": 6}
    flagged = score_submission(flagged_report)

    assert matched.calibrator_aggregate_mismatch_flag is False
    assert flagged.calibrator_aggregate_mismatch_flag is True

    traj = aggregate_tester([matched, flagged])
    assert traj.calibrator_aggregate_mismatch_count == 1
    # Ordering basis is the (project, video_id) proxy — surfaced as such on
    # the per-tester CSV so consumers don't read it as a real time series.
    assert traj.ordering_basis == "project_video_id_proxy"


def test_build_per_tester_table_groups_by_tester():
    records = [
        score_submission(_make_report(video_id="a1", tester_name="alice")),
        score_submission(_make_report(video_id="a2", tester_name="alice")),
        score_submission(_make_report(video_id="b1", tester_name="bob")),
    ]
    table = build_per_tester_table(records)
    by_name = {t.tester_name: t for t in table}
    assert set(by_name) == {"alice", "bob"}
    assert by_name["alice"].submission_count == 2
    assert by_name["bob"].submission_count == 1


def test_tier_boundaries_are_inclusive_at_85_70_55():
    # Direct boundary check via a score that resolves to exact thresholds.

    from src.tracking.performance_model import _tier_for
    assert _tier_for(85.0) == "Leading"
    assert _tier_for(84.9) == "Proficient"
    assert _tier_for(70.0) == "Proficient"
    assert _tier_for(69.9) == "Developing"
    assert _tier_for(55.0) == "Developing"
    assert _tier_for(54.9) == "Foundational"


# ---------------------------------------------------------------------------
# CSV input path
# ---------------------------------------------------------------------------


def _write_csv(tmp_path, name, header, rows):
    path = tmp_path / name
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(str(cell) for cell in row) + "\n")
    return path


def test_score_submissions_from_csv_reproduces_design_doc_example(tmp_path):
    findings_header = [
        "window_id", "video_id", "project", "tester_name",
        "friction_type", "severity_s", "sentiment_e", "calibrator_score_l",
        "signal_alignment",
    ]
    # 27 findings: F1×9, F2×5, F3×1, F5×3, F6×6, F7×3
    # severity:    S2×2, S3×4, S4×2, S5×19
    # alignment:   aligned×26, stated_missing×1
    rows = []
    severity_seq = ["S2"] * 2 + ["S3"] * 4 + ["S4"] * 2 + ["S5"] * 19
    friction_seq = ["F1"] * 9 + ["F2"] * 5 + ["F3"] * 1 + ["F5"] * 3 + ["F6"] * 6 + ["F7"] * 3
    align_seq = ["aligned"] * 26 + ["stated_missing"] * 1
    for i, (fr, sv, al) in enumerate(zip(friction_seq, severity_seq, align_seq)):
        rows.append([
            f"Sharelinsonny_suncorp_w{i:03d}", "Sharelinsonny_suncorp",
            "suncorp-insurance", "Sharelinsonny",
            fr, sv, "E4", "L2", al,
        ])
    findings_csv = _write_csv(tmp_path, "findings.csv", findings_header, rows)

    assessments_csv = _write_csv(
        tmp_path,
        "assessments.csv",
        ["video_id", "project", "tester_name",
         "narration_quality", "recording_quality", "coaching_evidence"],
        [["Sharelinsonny_suncorp", "suncorp-insurance", "Sharelinsonny",
          "rich", "acceptable", "none"]],
    )

    records = score_submissions_from_csv(findings_csv, assessments_csv)
    assert len(records) == 1
    record = records[0]
    assert record.video_id == "Sharelinsonny_suncorp"
    assert record.tester_name == "Sharelinsonny"
    assert record.d1_narration == 90.0
    assert record.d3_recording == 70.0
    assert record.score == 65.0
    assert record.tier == "Developing"
    assert record.cap_reasons == [">=2 S2 task-blockers"]


def test_score_submissions_from_csv_uses_windows_csv_when_provided(tmp_path):
    findings_csv = _write_csv(
        tmp_path,
        "findings.csv",
        ["window_id", "video_id", "project", "tester_name",
         "friction_type", "severity_s", "sentiment_e", "calibrator_score_l",
         "signal_alignment"],
        [
            ["v1_w000", "v1", "suncorp-insurance", "alice",
             "F1", "S5", "E3", "L2", "aligned"],
        ],
    )
    assessments_csv = _write_csv(
        tmp_path,
        "assessments.csv",
        ["video_id", "project", "tester_name",
         "narration_quality", "recording_quality", "coaching_evidence"],
        [["v1", "suncorp-insurance", "alice", "rich", "acceptable", "none"]],
    )
    # 50 windows in windows.csv but only 1 finding → very sparse, low density.
    windows_rows = [[f"v1_w{i:03d}", "v1"] for i in range(50)]
    windows_csv = _write_csv(
        tmp_path, "windows.csv", ["window_id", "video_id"], windows_rows
    )

    records = score_submissions_from_csv(
        findings_csv, assessments_csv, windows_csv=windows_csv
    )
    assert len(records) == 1
    assert records[0].total_windows == 50


# ---------------------------------------------------------------------------
# W10 P2 cleanup — boundary tests
# ---------------------------------------------------------------------------


def test_d3_duration_anomaly_caps_at_60():
    """Per §4.2: `l1.duration_anomaly == True` caps D3 at 60 (cap, not penalty
    stacking). Even with `recording_quality == 'good'` (D3 base = 90), the cap
    must bind at 60."""
    report = _make_report(
        l3_assessment={
            "narration_quality": "rich",
            "recording_quality": "good",
            "coaching_evidence": "none",
        }
    )
    report["l1"]["duration_anomaly"] = True
    record = score_submission(report)
    assert record.d3_recording == 60.0

    # Sanity: without the anomaly, the same input produces D3 = 90.
    report["l1"]["duration_anomaly"] = False
    assert score_submission(report).d3_recording == 90.0


def test_aggregate_tester_sentiment_distribution_sums_across_submissions():
    """Per §5.4: per-tester `sentiment_distribution` is the sum of E1..E5
    across all that tester's submissions. Verifies the aggregation accumulates
    rather than (e.g.) overwriting from the last submission."""
    r1_report = _make_report(video_id="v1", tester_name="t")
    r1_report["l3_findings"]["by_sentiment"] = {"E1": 3, "E4": 5}
    r2_report = _make_report(video_id="v2", tester_name="t")
    r2_report["l3_findings"]["by_sentiment"] = {"E1": 2, "E2": 4, "E4": 1}
    r1 = score_submission(r1_report)
    r2 = score_submission(r2_report)
    traj = aggregate_tester([r1, r2])
    assert traj.sentiment_distribution == {"E1": 5, "E2": 4, "E4": 6}


def test_calibrator_aggregate_invalid_label_is_ignored():
    """Per §4.7: an unknown calibrator label (e.g. 'L9') is not in the L1..L5
    rank table. It should be silently dropped from the weighted mean rather
    than crashing or producing a bogus tier."""
    from src.tracking.performance_model import _calibrator_aggregate
    # Only invalid labels → no aggregate at all.
    assert _calibrator_aggregate({"L9": 5}) is None
    # Mixed: invalid label dropped, valid labels still produce an aggregate.
    assert _calibrator_aggregate({"L9": 5, "L2": 4}) == "L2"


def test_calibrator_aggregate_uses_round_half_up_at_point_five():
    """Per W10 P2#4: weighted-mean .5 rounds *up* (ROUND_HALF_UP) rather than
    Python's default banker's rounding (which would map 2.5 → 2). This guards
    the .5 boundary so a tie between two L-labels resolves to the more-severe
    one, not silently to whichever is even."""
    from src.tracking.performance_model import _calibrator_aggregate
    # mean = 2.5 → must map to L3, not L2 (banker's would give L2).
    assert _calibrator_aggregate({"L2": 1, "L3": 1}) == "L3"
    # mean = 4.5 → must map to L5, not L4.
    assert _calibrator_aggregate({"L4": 1, "L5": 1}) == "L5"
    # mean = 1.5 → must map to L2, not L1.
    assert _calibrator_aggregate({"L1": 1, "L2": 1}) == "L2"


def test_score_submissions_from_csv_handles_missing_assessment_video(tmp_path):
    findings_csv = _write_csv(
        tmp_path,
        "findings.csv",
        ["window_id", "video_id", "project", "tester_name",
         "friction_type", "severity_s", "sentiment_e", "calibrator_score_l",
         "signal_alignment"],
        [
            ["orphan_w000", "orphan_video", "suncorp-insurance", "ghost",
             "F1", "S5", "E3", "L2", "aligned"],
            ["v1_w000", "v1", "suncorp-insurance", "alice",
             "F1", "S5", "E3", "L2", "aligned"],
        ],
    )
    assessments_csv = _write_csv(
        tmp_path,
        "assessments.csv",
        ["video_id", "project", "tester_name",
         "narration_quality", "recording_quality", "coaching_evidence"],
        [["v1", "suncorp-insurance", "alice", "rich", "acceptable", "none"]],
    )
    records = score_submissions_from_csv(findings_csv, assessments_csv)
    assert {r.video_id for r in records} == {"v1"}
