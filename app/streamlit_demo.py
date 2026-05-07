"""SMP Quality Report Demo — Streamlit UI.

Three views:
  - Single Video: hero + tabbed detail (Overview / Findings / Coaching / Layer details / JSON)
  - Tester Trajectory: per-tester score trajectory + persistent friction
  - Cohort Overview: dev55 distribution KPIs + tier / project breakdown

Read-only consumer of:
  - data/processed/reports/dev55/*.json            (per-video QualityReport)
  - data/processed/reports/_summary_dev55.csv      (one row per video, lightweight)
  - data/processed/performance/per_submission.csv  (R6 score / cap reasons)
  - data/processed/performance/per_tester.csv      (R6 trajectory / persistent friction)

Run:  streamlit run app/streamlit_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import streamlit as st


# Allow `python -m streamlit run app/streamlit_demo.py` from repo root by
# making the app/ folder importable as a package.
APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR.parent) not in sys.path:
    sys.path.insert(0, str(APP_DIR.parent))

from app import components as C  # noqa: E402
from app import styles as S  # noqa: E402


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPORT_DIR = Path("data/processed/reports/dev55")
SUMMARY_PATH = Path("data/processed/reports/_summary_dev55.csv")
PER_SUBMISSION_PATH = Path("data/processed/performance/per_submission.csv")
PER_TESTER_PATH = Path("data/processed/performance/per_tester.csv")


# ---------------------------------------------------------------------------
# Cached loaders
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _load_report_files(report_dir_str: str) -> list[str]:
    p = Path(report_dir_str)
    if not p.exists():
        return []
    return sorted(str(x) for x in p.glob("*.json") if not x.name.startswith("_"))


@st.cache_data(show_spinner=False)
def _load_csv(path_str: str) -> Optional[pd.DataFrame]:
    p = Path(path_str)
    if not p.exists():
        return None
    return pd.read_csv(p)


@st.cache_data(show_spinner=False)
def _load_report(path_str: str) -> dict[str, Any]:
    with open(path_str, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Sidebar: filters + video select + view switch
# ---------------------------------------------------------------------------

def _sidebar(
    *,
    summary_df: Optional[pd.DataFrame],
    report_files: list[str],
) -> tuple[str, Optional[str]]:
    """Render sidebar; return (view_name, selected_video_or_None)."""
    st.sidebar.markdown("## SMP Demo")
    st.sidebar.caption("Tester quality assessment & coaching prototype")

    view = st.sidebar.radio(
        "View",
        options=["Single Video", "Tester Trajectory", "Cohort Overview"],
        index=0,
    )
    st.sidebar.divider()

    if view != "Single Video":
        return view, None

    # Build filter pool from summary_df (preferred) or filenames
    options_df: pd.DataFrame
    if summary_df is not None and "video_id" in summary_df.columns:
        options_df = summary_df.copy()
    else:
        options_df = pd.DataFrame(
            {"video_id": [Path(f).stem for f in report_files]}
        )
        options_df["project"] = "?"
        options_df["tier"] = "?"

    # Project filter
    projects = sorted({p for p in options_df["project"].dropna().unique()})
    project_sel = st.sidebar.multiselect(
        "Project filter",
        options=projects,
        default=projects,
    )
    options_df = options_df[options_df["project"].isin(project_sel)]

    # Tier filter
    tiers = ["good", "acceptable", "poor"]
    tier_sel = st.sidebar.multiselect(
        "Tier filter",
        options=tiers,
        default=tiers,
    )
    if "tier" in options_df.columns:
        options_df = options_df[options_df["tier"].isin(tier_sel)]

    if options_df.empty:
        st.sidebar.warning("No videos match the current filters.")
        return view, None

    # Build options ordered by tier severity (poor -> acceptable -> good) for demo flow
    tier_rank = {"poor": 0, "acceptable": 1, "good": 2}
    if "tier" in options_df.columns:
        options_df = options_df.assign(
            _tier_rank=options_df["tier"].map(lambda t: tier_rank.get(t, 99))
        ).sort_values(["_tier_rank", "video_id"])

    label_map = {
        row["video_id"]: C.video_option_label(row["video_id"], row.get("tier"))
        for _, row in options_df.iterrows()
    }

    selected_video = st.sidebar.selectbox(
        f"Select video ({len(label_map)} matching)",
        options=list(label_map.keys()),
        format_func=lambda v: label_map.get(v, v),
    )

    st.sidebar.divider()
    st.sidebar.caption(
        f"📁  `{REPORT_DIR}/{selected_video}.json`"
    )

    return view, selected_video


# ---------------------------------------------------------------------------
# View: Single Video
# ---------------------------------------------------------------------------

def _view_single_video(
    video_id: str,
    *,
    report: dict[str, Any],
    submission_row: Optional[pd.Series],
) -> None:
    overall = report.get("overall") or {}
    l3_assessment = report.get("l3_assessment") or {}
    l3_findings_summary = report.get("l3_findings") or {}
    coaching = report.get("coaching_recommendations") or []

    cap_reasons: list[str] = []
    score: Optional[float] = None
    if submission_row is not None:
        cap_raw = submission_row.get("cap_reasons")
        if isinstance(cap_raw, str) and cap_raw.strip():
            cap_reasons = [c.strip() for c in cap_raw.split("|") if c.strip()]
        try:
            score = float(submission_row.get("score"))
        except (TypeError, ValueError):
            score = None

    C.hero_card(
        title=video_id,
        tester=str(report.get("tester_name") or "?"),
        project=str(report.get("project") or "?"),
        tier=str(overall.get("quality_tier") or "?"),
        score=score,
        duration_sec=report.get("duration_sec"),
        total_windows=report.get("total_windows"),
        total_findings=l3_findings_summary.get("total_findings"),
        cap_reasons=cap_reasons,
    )

    tab_overview, tab_findings, tab_coaching, tab_layers, tab_raw = st.tabs(
        ["📊 Overview", "🔍 Findings", "🧭 Coaching", "🧱 Layer details", "{ } JSON"]
    )

    with tab_overview:
        _render_overview_tab(report, l3_findings_summary, l3_assessment, submission_row)

    with tab_findings:
        _render_findings_tab(l3_findings_summary)

    with tab_coaching:
        _render_coaching_tab(coaching, l3_assessment)

    with tab_layers:
        _render_layers_tab(report)

    with tab_raw:
        st.json(report)


def _render_overview_tab(
    report: dict[str, Any],
    findings_summary: dict[str, Any],
    assessment: dict[str, Any],
    submission_row: Optional[pd.Series],
) -> None:
    overall = report.get("overall") or {}

    # Reasoning
    reasoning = overall.get("reasoning") or []
    if reasoning:
        st.markdown("##### Tier reasoning")
        for r in reasoning:
            st.markdown(f"- {r}")

    st.markdown("##### Session-level assessment (5.1-B)")
    cols = st.columns(3)
    cols[0].metric("Narration", str(assessment.get("narration_quality") or "—"))
    cols[1].metric("Recording", str(assessment.get("recording_quality") or "—"))
    cols[2].metric("Coaching evidence", str(assessment.get("coaching_evidence") or "—"))

    # R6 score breakdown if available
    if submission_row is not None:
        st.markdown("##### R6 score breakdown")
        cols = st.columns(4)
        cols[0].metric("Raw composite", _fmt_num(submission_row.get("raw_score")))
        cols[1].metric("D1 Narration · 0.50", _fmt_num(submission_row.get("d1_narration")))
        cols[2].metric("D2 Friction · 0.35", _fmt_num(submission_row.get("d2_friction_surfacing")))
        cols[3].metric("D3 Recording · 0.15", _fmt_num(submission_row.get("d3_recording")))

        cap_applied = submission_row.get("cap_applied")
        cal_agg = submission_row.get("calibrator_aggregate")
        cal_mismatch = submission_row.get("calibrator_aggregate_mismatch_flag")
        low_evidence = submission_row.get("low_evidence")

        chips = []
        if cap_applied:
            chips.append(f"Cap binding: **{cap_applied}**")
        if isinstance(cal_agg, str) and cal_agg:
            chips.append(f"Calibrator aggregate: {cal_agg}")
        if str(cal_mismatch).lower() in {"true", "1"}:
            chips.append("⚠️ Calibrator mismatch flag")
        if str(low_evidence).lower() in {"true", "1"}:
            chips.append("ℹ️ low_evidence (windows < 5)")
        if chips:
            st.markdown(" · ".join(chips))

    # Distribution snapshots
    if findings_summary.get("total_findings", 0) > 0:
        st.markdown("##### Friction distribution")
        C.distribution_bar(
            findings_summary.get("by_friction_type") or {},
            S.FRICTION_COLORS,
        )
        st.markdown("##### Severity distribution")
        C.distribution_bar(
            findings_summary.get("by_severity") or {},
            S.SEVERITY_COLORS,
        )
        st.markdown("##### Sentiment distribution")
        C.distribution_bar(
            findings_summary.get("by_sentiment") or {},
            S.SENTIMENT_COLORS,
        )


def _render_findings_tab(findings_summary: dict[str, Any]) -> None:
    total = findings_summary.get("total_findings", 0)
    if not total:
        st.info("No L3 findings in this report.")
        return

    # KPI strip
    by_sev = findings_summary.get("by_severity") or {}
    by_ft = findings_summary.get("by_friction_type") or {}
    top_ft = max(by_ft.items(), key=lambda kv: kv[1])[0] if by_ft else "—"

    cols = st.columns(4)
    cols[0].metric("Total findings", total)
    cols[1].metric("S1 task-blocking", by_sev.get("S1", 0))
    cols[2].metric("S2 component-blocking", by_sev.get("S2", 0))
    cols[3].metric("Dominant friction", top_ft)

    top_findings = findings_summary.get("top_findings") or []
    if not top_findings:
        st.caption("(no top_findings array in report)")
        return

    # Filters
    sev_options = sorted({f.get("severity_s") for f in top_findings if f.get("severity_s")})
    ft_options = sorted({f.get("friction_type") for f in top_findings if f.get("friction_type")})

    with st.expander("Filter findings", expanded=False):
        sev_pick = st.multiselect("Severity", options=sev_options, default=sev_options)
        ft_pick = st.multiselect("Friction type", options=ft_options, default=ft_options)

    # Severity sort key (S1 first)
    sev_rank = {f"S{i}": i for i in range(1, 7)}
    filtered = [
        f for f in top_findings
        if f.get("severity_s") in sev_pick and f.get("friction_type") in ft_pick
    ]
    filtered.sort(key=lambda f: sev_rank.get(f.get("severity_s") or "S6", 99))

    st.caption(f"Showing {len(filtered)} of {len(top_findings)} top findings (sorted by severity).")
    for f in filtered:
        C.finding_row(f)


def _render_coaching_tab(
    coaching: list[dict[str, Any]],
    assessment: dict[str, Any],
) -> None:
    if not coaching:
        st.info(
            "No coaching recommendations were generated for this session. "
            "This usually means narration / recording / coaching_evidence are all in their "
            "neutral default — review the Overview tab for the session-level assessment."
        )
        return

    st.caption(
        f"{len(coaching)} session-level recommendation(s) generated by Step 6.2 (template-based MVP). "
        "Recommendations are ordered by priority."
    )
    sorted_recs = sorted(coaching, key=lambda r: r.get("priority", 99))
    for rec in sorted_recs:
        C.coaching_card(rec)


def _render_layers_tab(report: dict[str, Any]) -> None:
    l1 = report.get("l1") or {}
    l2 = report.get("l2") or {}

    st.markdown("##### Layer 1 — rule-based flags")
    cols = st.columns(3)
    cols[0].metric("Total flags", l1.get("total_flags", 0))
    cols[1].metric(
        "Duration anomaly",
        "Yes" if l1.get("duration_anomaly") else "No",
    )
    cols[2].metric("Flagged windows", len(l1.get("flagged_window_ids") or []))
    if l1.get("flag_counts"):
        st.markdown("Flag breakdown:")
        df = pd.DataFrame(
            [{"Flag": k, "Count": v} for k, v in l1["flag_counts"].items()]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("##### Layer 2 — clustering coverage")
    cols = st.columns(3)
    cols[0].metric("Coverage", _fmt_num(l2.get("coverage")))
    cols[1].metric("Dominant cluster", str(l2.get("dominant_cluster_id") or "—"))
    cols[2].metric("Dominance %", _fmt_num(l2.get("dominant_cluster_pct")))
    if l2.get("caveat"):
        st.caption(f"⚠️ {l2['caveat']}")


# ---------------------------------------------------------------------------
# View: Tester Trajectory
# ---------------------------------------------------------------------------

def _view_tester_trajectory(per_tester_df: Optional[pd.DataFrame]) -> None:
    st.markdown("## Tester Trajectory")
    st.caption(
        "Per-tester aggregate score, direction, and persistent friction across submissions. "
        "Source: R6 `data/processed/performance/per_tester.csv`."
    )

    if per_tester_df is None or per_tester_df.empty:
        st.warning("`per_tester.csv` is unavailable; ensure R6 build script has been run.")
        return

    df = per_tester_df.copy()
    df["display"] = df.apply(
        lambda r: f"{C.S.TIER_EMOJI.get(str(r['tier']).lower(), '⚪')}  {r['tester_name']} "
        f"({int(r.get('submission_count', 0))} submissions)",
        axis=1,
    )
    df = df.sort_values(["tier", "tester_name"])

    selected_label = st.selectbox(
        f"Select tester ({len(df)} dev testers)",
        options=df["display"].tolist(),
    )
    row = df[df["display"] == selected_label].iloc[0]

    # Top stats
    cols = st.columns(4)
    cols[0].metric("Aggregate score", _fmt_num(row.get("score")))
    cols[1].metric("Tier", "")
    cols[1].markdown(C.tier_badge(str(row.get("tier") or "—"), large=True), unsafe_allow_html=True)
    cols[2].metric("Direction", str(row.get("direction") or "—"))
    cols[3].metric(
        "Δ first → last",
        _fmt_num(row.get("delta_first_to_last"), signed=True),
    )

    st.markdown("##### Submission scores")
    sub_ids = _safe_split(row.get("submission_video_ids"))
    sub_scores = _safe_split(row.get("submission_scores"))
    sub_tiers = _safe_split(row.get("submission_tiers"))

    if sub_ids and sub_scores and len(sub_ids) == len(sub_scores):
        traj_df = pd.DataFrame(
            {
                "submission": sub_ids,
                "score": [_safe_float(s) for s in sub_scores],
                "tier": sub_tiers + [""] * (len(sub_ids) - len(sub_tiers)),
            }
        ).set_index("submission")
        st.line_chart(traj_df["score"], height=280)
        st.dataframe(
            traj_df.reset_index(),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("(no scored submissions in trajectory layer)")

    st.markdown("##### Persistent friction & sentiment")
    persistent = _safe_split(row.get("persistent_friction_types"))
    if persistent:
        chips = "".join(C.friction_chip(p) for p in persistent)
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.caption("No friction type recurs in top-3 across multiple submissions.")

    sent_dist = row.get("sentiment_distribution")
    if isinstance(sent_dist, str) and sent_dist.strip():
        try:
            parsed = json.loads(sent_dist.replace("'", '"'))
            if isinstance(parsed, dict) and parsed:
                st.markdown("Sentiment roll-up:")
                C.distribution_bar(
                    {k: int(v) for k, v in parsed.items()},
                    S.SENTIMENT_COLORS,
                )
        except (ValueError, json.JSONDecodeError):
            st.caption(f"Raw: {sent_dist}")

    # Cross-check + calibrator audit
    lane = row.get("cross_check_lanes")
    cal_mm = row.get("calibrator_aggregate_mismatch_count")
    meta_parts = []
    if lane:
        meta_parts.append(f"Cross-check lane: `{lane}`")
    if cal_mm not in (None, "", float("nan")):
        try:
            n = int(float(cal_mm))
            if n > 0:
                meta_parts.append(f"⚠️ Calibrator mismatch flagged in {n} submission(s)")
        except (TypeError, ValueError):
            pass
    projects = row.get("projects")
    if projects:
        meta_parts.append(f"Projects: {projects}")
    if meta_parts:
        st.caption(" · ".join(meta_parts))


# ---------------------------------------------------------------------------
# View: Cohort Overview
# ---------------------------------------------------------------------------

def _view_cohort_overview(
    summary_df: Optional[pd.DataFrame],
    per_submission_df: Optional[pd.DataFrame],
    per_tester_df: Optional[pd.DataFrame],
) -> None:
    st.markdown("## Cohort Overview")
    st.caption(
        "Aggregate view of dev55 (the 55 official development videos). "
        "Use this to demo system behaviour at the cohort level before drilling into a single submission."
    )

    if summary_df is None:
        st.warning("`_summary_dev55.csv` is unavailable.")
        return

    # Top KPIs
    n_videos = len(summary_df)
    n_testers = (
        per_tester_df["tester_name"].nunique() if per_tester_df is not None else summary_df["tester"].nunique()
    )
    cap_rate = "—"
    median_score = "—"
    if per_submission_df is not None and not per_submission_df.empty:
        try:
            cap_count = per_submission_df["cap_applied"].notna().sum()
            cap_count -= (per_submission_df["cap_applied"] == "").sum()
            cap_rate = f"{cap_count} / {len(per_submission_df)} ({100.0 * cap_count / len(per_submission_df):.0f}%)"
        except KeyError:
            pass
        try:
            median_score = f"{per_submission_df['score'].median():.0f}"
        except (KeyError, TypeError):
            pass

    cols = st.columns(4)
    cols[0].metric("Videos", n_videos)
    cols[1].metric("Testers", n_testers)
    cols[2].metric("Median score", median_score)
    cols[3].metric("Cap binding rate", cap_rate)

    st.divider()

    # Tier distribution
    st.markdown("##### Per-video tier distribution (fusion output)")
    tier_counts = summary_df["tier"].value_counts().reindex(["good", "acceptable", "poor"]).fillna(0).astype(int)
    C.distribution_bar(tier_counts.to_dict(), S.TIER_COLORS)

    # Per-submission R6 tier distribution
    if per_submission_df is not None and "tier" in per_submission_df.columns:
        st.markdown("##### R6 per-submission tier (post-cap score)")
        r6_counts = per_submission_df["tier"].value_counts()
        ordered = ["Leading", "Proficient", "Developing", "Foundational"]
        r6_dict = {
            t: int(r6_counts.get(t, 0)) for t in ordered if t in r6_counts.index or True
        }
        C.distribution_bar(
            {k.lower(): v for k, v in r6_dict.items() if v > 0},
            S.TIER_COLORS,
        )

    # Project breakdown
    st.markdown("##### Per-project breakdown")
    if "project" in summary_df.columns:
        proj_tier = (
            summary_df.groupby(["project", "tier"]).size().unstack(fill_value=0)
        )
        st.bar_chart(proj_tier, height=260)

    # Top friction per project
    if per_submission_df is not None and "top_friction_types" in per_submission_df.columns:
        st.markdown("##### Top friction types — frequency across submissions")
        all_ft: list[str] = []
        for v in per_submission_df["top_friction_types"].dropna():
            all_ft.extend(_safe_split(v))
        if all_ft:
            ft_counts = pd.Series(all_ft).value_counts()
            chips_html = "".join(
                f"{C.friction_chip(ft)}<span style='color:{S.SLATE_500}; font-size:0.85rem; margin-right:14px;'>×{n}</span> "
                for ft, n in ft_counts.items()
            )
            st.markdown(chips_html, unsafe_allow_html=True)

    # Trajectory direction (if per_tester available)
    if per_tester_df is not None and "direction" in per_tester_df.columns:
        st.markdown("##### Trajectory direction (testers with ≥2 scored submissions)")
        scored = per_tester_df[per_tester_df["submission_count_scored"].fillna(0) >= 2]
        if not scored.empty:
            dir_counts = scored["direction"].value_counts().to_dict()
            cols = st.columns(len(dir_counts))
            arrow_map = {"improving": "↗", "stable": "→", "declining": "↘"}
            for i, (d, n) in enumerate(dir_counts.items()):
                cols[i].metric(f"{arrow_map.get(d, '·')} {d}", n)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt_num(v: Any, *, signed: bool = False) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "—"
    if pd.isna(f):
        return "—"
    if signed:
        return f"{f:+.1f}" if abs(f) < 100 else f"{f:+.0f}"
    return f"{f:.1f}" if abs(f) < 100 else f"{f:.0f}"


def _safe_float(v: Any) -> Optional[float]:
    try:
        f = float(v)
        return None if pd.isna(f) else f
    except (TypeError, ValueError):
        return None


def _safe_split(v: Any, sep: str = "|") -> list[str]:
    """Split a pipe-delimited string column. Returns [] on missing."""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    s = str(v).strip()
    if not s or s.lower() in {"nan", "none"}:
        return []
    return [x.strip() for x in s.split(sep) if x.strip()]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="SMP Quality Report Demo",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(S.GLOBAL_CSS, unsafe_allow_html=True)

    # Top ribbon
    st.markdown(
        f"""
        <div style="border-top: 4px solid {S.USYD_RED}; margin: -16px -16px 16px -16px;"></div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h1 style='margin-bottom:0;'>Intelligent Tester Quality Assessment</h1>"
        f"<div style='color:{S.SLATE_500}; font-size:0.95rem; margin-bottom:18px;'>"
        f"USyd CS20 · See Me Please · decision-support prototype</div>",
        unsafe_allow_html=True,
    )

    report_files = _load_report_files(str(REPORT_DIR))
    if not report_files:
        st.error(f"No JSON reports in {REPORT_DIR}. Run `python scripts/run_pipeline.py --all` first.")
        st.stop()

    summary_df = _load_csv(str(SUMMARY_PATH))
    per_submission_df = _load_csv(str(PER_SUBMISSION_PATH))
    per_tester_df = _load_csv(str(PER_TESTER_PATH))

    view, selected_video = _sidebar(summary_df=summary_df, report_files=report_files)

    if view == "Single Video":
        if not selected_video:
            st.info("Select a video from the sidebar to view its quality report.")
        else:
            video_path = REPORT_DIR / f"{selected_video}.json"
            if not video_path.exists():
                st.error(f"Report file missing: {video_path}")
                st.stop()
            report = _load_report(str(video_path))
            sub_row = None
            if per_submission_df is not None and "video_id" in per_submission_df.columns:
                m = per_submission_df[per_submission_df["video_id"] == selected_video]
                if not m.empty:
                    sub_row = m.iloc[0]
            _view_single_video(selected_video, report=report, submission_row=sub_row)

    elif view == "Tester Trajectory":
        _view_tester_trajectory(per_tester_df)

    elif view == "Cohort Overview":
        _view_cohort_overview(summary_df, per_submission_df, per_tester_df)

    # Footer
    C.footer(commit="b34cac9", data_date="2026-05-07 · dev55 official")


if __name__ == "__main__":
    main()
