"""SMP Quality Report Demo — Streamlit UI.

Three views (segmented switcher in sidebar):
  - Single Video: hero + 4 tabs (Overview / Findings / Coaching / Layer details)
  - Tester Trajectory: hero + score line + persistent friction + metadata
  - Cohort Overview: dev55 KPIs + R6 tier distribution + per-project breakdown

Read-only consumer of:
  - data/processed/reports/dev55/*.json            per-video QualityReport
  - data/processed/reports/_summary_dev55.csv      one row per video
  - data/processed/layer3_findings_filtered.csv    full finding set (2,133 rows)
  - data/processed/performance/per_submission.csv  R6 score & cap reasons
  - data/processed/performance/per_tester.csv      R6 trajectory

Run:  streamlit run app/streamlit_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Optional

import altair as alt
import pandas as pd
import streamlit as st

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
FINDINGS_PATH = Path("data/processed/layer3_findings_filtered.csv")
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
# Multiselect with quick All / Clear buttons
# ---------------------------------------------------------------------------

def _multiselect_all(
    container: Any,
    label: str,
    options: list,
    key: str,
) -> list:
    """Popover-style multiselect with per-option checkboxes + Select all toggle.

    The popover button shows `<label> · <n>/<total>` (or `· all` / `· none`).
    Inside the popover: a single Select all / Clear all toggle, a divider,
    then one checkbox per option.

    State is persisted in st.session_state under per-option keys
    (`<key>__chk__<option>`). Stale per-option keys for options no longer
    in the option set are removed automatically.

    Default behaviour: every option starts selected.
    """
    options = list(options)

    # Initialize per-option keys (default = checked) and prune stale keys
    valid_keys = {f"{key}__chk__{opt}" for opt in options}
    for opt in options:
        opt_key = f"{key}__chk__{opt}"
        if opt_key not in st.session_state:
            st.session_state[opt_key] = True
    for k in [k for k in st.session_state.keys() if k.startswith(f"{key}__chk__") and k not in valid_keys]:
        del st.session_state[k]

    selected = [opt for opt in options if st.session_state.get(f"{key}__chk__{opt}", False)]
    n_sel, n_total = len(selected), len(options)
    if n_total == 0:
        btn_label = f"{label} · (no options)"
    elif n_sel == n_total:
        btn_label = f"{label} · all ({n_total})"
    elif n_sel == 0:
        btn_label = f"{label} · none"
    else:
        btn_label = f"{label} · {n_sel}/{n_total}"

    with container.popover(btn_label, use_container_width=True):
        if n_total > 0:
            if n_sel == n_total:
                if st.button("Clear all", key=f"{key}__sa", use_container_width=True):
                    for opt in options:
                        st.session_state[f"{key}__chk__{opt}"] = False
                    st.rerun()
            else:
                if st.button(f"✓ Select all ({n_total})", key=f"{key}__sa", use_container_width=True):
                    for opt in options:
                        st.session_state[f"{key}__chk__{opt}"] = True
                    st.rerun()
            st.divider()
            for opt in options:
                st.checkbox(opt, key=f"{key}__chk__{opt}")

    return [opt for opt in options if st.session_state.get(f"{key}__chk__{opt}", False)]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def _sidebar(
    summary_df: Optional[pd.DataFrame],
    report_files: list[str],
) -> tuple[str, Optional[str]]:
    """Render sidebar; return (view_name, selected_video_or_None)."""
    st.sidebar.markdown("## SMP Demo")
    st.sidebar.caption("Tester quality assessment & coaching prototype")

    view = st.sidebar.radio(
        "View",
        options=["Single Video", "Tester Trajectory", "Cohort Overview"],
        label_visibility="collapsed",
    )
    st.sidebar.divider()

    if view != "Single Video":
        return view, None

    # Build options pool
    if summary_df is not None and "video_id" in summary_df.columns:
        opts = summary_df.copy()
    else:
        opts = pd.DataFrame({"video_id": [Path(f).stem for f in report_files]})
        opts["project"] = "?"
        opts["tier"] = "?"
        opts["tester"] = "?"

    for col in ["project", "tier", "tester"]:
        if col not in opts.columns:
            opts[col] = "?"

    tier_pick = _multiselect_all(
        st.sidebar,
        "Tier",
        options=["poor", "acceptable", "good"],
        key="filter_tier",
    )

    project_short_map = {p: C.project_short(p) for p in opts["project"].dropna().unique()}
    project_short_options = sorted(set(project_short_map.values()))
    project_pick_short = _multiselect_all(
        st.sidebar,
        "Project",
        options=project_short_options,
        key="filter_project",
    )

    # Filter
    filtered = opts.copy()
    if "tier" in filtered.columns:
        filtered = filtered[filtered["tier"].isin(tier_pick)]
    filtered = filtered[
        filtered["project"].map(lambda p: project_short_map.get(p, p)).isin(project_pick_short)
    ]

    if filtered.empty:
        st.sidebar.warning("No videos match filters.")
        return view, None

    st.sidebar.caption(f"Showing {len(filtered)} of {len(opts)} videos")

    # Sort: poor first for demo flow
    tier_rank = {"poor": 0, "acceptable": 1, "good": 2}
    if "tier" in filtered.columns:
        filtered = filtered.assign(
            _r=filtered["tier"].map(lambda t: tier_rank.get(t, 99))
        ).sort_values(["_r", "project", "tester", "video_id"])

    label_map = {
        row["video_id"]: C.video_option_label(
            row["video_id"],
            row.get("tier"),
            tester=row.get("tester"),
            project=row.get("project"),
        )
        for _, row in filtered.iterrows()
    }
    selected_options = list(label_map.keys())
    current_selected = st.session_state.get("sidebar_video_select")
    if current_selected not in selected_options:
        current_selected = selected_options[0]

    selected = st.sidebar.selectbox(
        f"Video ({len(label_map)})",
        options=selected_options,
        index=selected_options.index(current_selected),
        format_func=lambda v: label_map.get(v, v),
        key="sidebar_video_select",
    )
    selected_row = filtered[filtered["video_id"] == selected].iloc[0]
    st.sidebar.markdown(
        "\n".join(
            [
                f"**Tester**: `{selected_row.get('tester', '—')}`",
                f"**Project**: `{C.project_short(selected_row.get('project'))}`",
                f"**Tier**: `{selected_row.get('tier', '—')}`",
            ]
        )
    )
    if "reason" in selected_row and pd.notna(selected_row.get("reason")):
        st.sidebar.caption(str(selected_row.get("reason")))
    return view, selected


# ---------------------------------------------------------------------------
# View: Single Video
# ---------------------------------------------------------------------------

def _view_single_video(
    video_id: str,
    *,
    report: dict[str, Any],
    submission_row: Optional[pd.Series],
    findings_full: Optional[pd.DataFrame],
) -> None:
    overall = report.get("overall") or {}
    l3a = report.get("l3_assessment") or {}
    l3f = report.get("l3_findings") or {}
    coaching = report.get("coaching_recommendations") or []

    cap_reasons: list[str] = []
    score: Optional[float] = None
    if submission_row is not None:
        cap_raw = submission_row.get("cap_reasons")
        if isinstance(cap_raw, str) and cap_raw.strip() and cap_raw.lower() != "nan":
            cap_reasons = [c.strip() for c in cap_raw.split("|") if c.strip()]
        try:
            score = float(submission_row.get("score"))
            if pd.isna(score):
                score = None
        except (TypeError, ValueError):
            score = None

    # Hero — single source of truth for top stats
    duration = report.get("duration_sec") or 0
    dur_str = f"{int(duration // 60)}m {int(duration % 60):02d}s" if duration else "—"
    stats: list[tuple[str, str]] = []
    if score is not None:
        stats.append(("Score", f"{score:.0f}/100"))
    stats.append(("Findings", str(l3f.get("total_findings", 0))))
    stats.append(("Windows", str(report.get("total_windows", "—"))))
    stats.append(("Duration", dur_str))

    C.hero_card(
        title=video_id,
        subtitle=f"{report.get('tester_name', '?')} · {C.project_short(report.get('project'))}",
        tier=overall.get("quality_tier"),
        stats=stats,
        cap_reasons=cap_reasons,
    )

    # Tier reasoning (one-line, just below hero)
    reasoning = overall.get("reasoning") or []
    C.info_grid(
        [
            ("Tester", str(report.get("tester_name") or "—")),
            ("Project", C.project_short(report.get("project"))),
            ("Top severity", str(l3f.get("top_severity") or "—")),
            ("Reason", str(reasoning[0] if reasoning else "—")),
        ]
    )
    if reasoning:
        st.caption("Tier reasoning:  " + "  ·  ".join(escape_safe(r) for r in reasoning))

    tab_overview, tab_findings, tab_coaching, tab_layers = st.tabs(
        ["Overview", f"Findings ({l3f.get('total_findings', 0)})",
         f"Coaching ({len(coaching)})", "Layer detail"]
    )

    with tab_overview:
        _render_overview(l3a, l3f, submission_row)
    with tab_findings:
        _render_findings(video_id, l3f, findings_full)
    with tab_coaching:
        _render_coaching(coaching)
    with tab_layers:
        _render_layers(report)


def _render_overview(
    assessment: dict[str, Any],
    findings_summary: dict[str, Any],
    submission_row: Optional[pd.Series],
) -> None:
    # 5.1-B session-level assessment
    st.markdown("##### Session-level assessment (Layer 3-B)")
    cols = st.columns(3)
    cols[0].metric("Narration", str(assessment.get("narration_quality") or "—"))
    cols[1].metric("Recording", str(assessment.get("recording_quality") or "—"))
    cols[2].metric("Coaching evidence", str(assessment.get("coaching_evidence") or "—"))

    # R6 dimension breakdown (only if available)
    if submission_row is not None:
        st.markdown("##### R6 score breakdown")
        cols = st.columns(4)
        cols[0].metric("Raw composite", _fmt(submission_row.get("raw_score")))
        cols[1].metric("D1 Narration", _fmt(submission_row.get("d1_narration")))
        cols[2].metric("D2 Friction", _fmt(submission_row.get("d2_friction_surfacing")))
        cols[3].metric("D3 Recording", _fmt(submission_row.get("d3_recording")))
        st.caption(
            f"Weights: D1·0.50 + D2·0.35 + D3·0.15 → raw composite. "
            f"Caps bind after raw (Model E)."
        )

    # Distributions — only if findings exist
    if findings_summary.get("total_findings", 0) > 0:
        st.markdown("##### Severity distribution")
        C.distribution_bar(findings_summary.get("by_severity") or {}, S.SEVERITY_COLORS)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### Friction types")
            C.distribution_bar(findings_summary.get("by_friction_type") or {})
        with col_b:
            st.markdown("##### Sentiment")
            C.distribution_bar(findings_summary.get("by_sentiment") or {})


def _render_findings(
    video_id: str,
    findings_summary: dict[str, Any],
    findings_full: Optional[pd.DataFrame],
) -> None:
    total = int(findings_summary.get("total_findings") or 0)
    if total == 0:
        st.info("No L3 findings in this report.")
        return

    # Pull full findings for this video from filtered.csv
    rows: list[dict[str, Any]] = []
    if findings_full is not None and "video_id" in findings_full.columns:
        sub = findings_full[findings_full["video_id"] == video_id]
        rows = sub.to_dict("records")
    if not rows:
        # fallback to top_findings inside JSON
        rows = list(findings_summary.get("top_findings") or [])
        if rows:
            st.info(f"Showing {len(rows)} highlighted findings (full set unavailable).")

    # KPI strip
    by_sev = findings_summary.get("by_severity") or {}
    by_ft = findings_summary.get("by_friction_type") or {}
    top_ft = max(by_ft.items(), key=lambda kv: kv[1])[0] if by_ft else "—"
    C.info_grid(
        [
            ("Total findings", str(total)),
            ("S1", str(by_sev.get("S1", 0))),
            ("S2", str(by_sev.get("S2", 0))),
            ("Top friction", top_ft),
        ]
    )

    # Filters in sidebar-style row (compact pills)
    sev_options = sorted({(r.get("severity_s") or "—") for r in rows if r.get("severity_s")})
    ft_options = sorted({(r.get("friction_type") or "—") for r in rows if r.get("friction_type")})

    fcols = st.columns([2, 2, 1])
    with fcols[0]:
        sev_pick = _multiselect_all(fcols[0], "Severity", sev_options, "finding_sev")
    with fcols[1]:
        ft_pick = _multiselect_all(fcols[1], "Friction type", ft_options, "finding_ft")
    with fcols[2]:
        sort_mode = st.selectbox(
            "Sort",
            options=["Severity (S1 first)", "Window order"],
            key="finding_sort",
        )

    sev_rank = {f"S{i}": i for i in range(1, 7)}
    filtered_rows = [
        r for r in rows
        if r.get("severity_s") in sev_pick
        and r.get("friction_type") in ft_pick
    ]
    if sort_mode.startswith("Severity"):
        filtered_rows.sort(key=lambda r: sev_rank.get(r.get("severity_s") or "S6", 99))
    else:
        filtered_rows.sort(key=lambda r: r.get("window_id") or "")

    st.caption(f"Showing **{len(filtered_rows)}** of **{len(rows)}** findings.")
    if filtered_rows:
        filtered_by_sev = pd.Series(
            [r.get("severity_s") or "—" for r in filtered_rows]
        ).value_counts()
        C.info_grid(
            [
                ("Visible S1-S2", str(int(filtered_by_sev.get("S1", 0) + filtered_by_sev.get("S2", 0)))),
                ("Visible severity bands", str(len(filtered_by_sev))),
                ("Visible friction types", str(len({r.get("friction_type") for r in filtered_rows if r.get("friction_type")}))),
                ("Sort", sort_mode),
            ]
        )
    else:
        st.warning("No findings match the current filters.")
        return

    # Render
    for r in filtered_rows:
        C.finding_row(r)


def _render_coaching(coaching: list[dict[str, Any]]) -> None:
    if not coaching:
        st.info(
            "No coaching recommendations were generated. "
            "Narration / recording / coaching_evidence are all in their neutral default."
        )
        return
    sorted_recs = sorted(coaching, key=lambda r: r.get("priority", 99))
    for rec in sorted_recs:
        C.coaching_card(rec)


def _render_layers(report: dict[str, Any]) -> None:
    l1 = report.get("l1") or {}
    l2 = report.get("l2") or {}

    st.markdown("##### Layer 1 — rule-based flags")
    cols = st.columns(3)
    cols[0].metric("Total flags", l1.get("total_flags", 0))
    cols[1].metric("Duration anomaly", "Yes" if l1.get("duration_anomaly") else "No")
    cols[2].metric("Flagged windows", len(l1.get("flagged_window_ids") or []))
    if l1.get("flag_counts"):
        df = pd.DataFrame([{"Flag": k, "Count": v} for k, v in l1["flag_counts"].items()])
        st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("##### Layer 2 — clustering coverage")
    cols = st.columns(3)
    cols[0].metric("Coverage", _fmt(l2.get("coverage")))
    cols[1].metric("Dominant cluster", str(l2.get("dominant_cluster_id") or "—"))
    cols[2].metric("Dominance %", _fmt(l2.get("dominant_cluster_pct")))
    if l2.get("caveat"):
        st.caption(f"⚠️ {l2['caveat']}")


# ---------------------------------------------------------------------------
# View: Tester Trajectory
# ---------------------------------------------------------------------------

def _view_tester_trajectory(per_tester_df: Optional[pd.DataFrame]) -> None:
    if per_tester_df is None or per_tester_df.empty:
        st.warning("`per_tester.csv` is unavailable; run `python scripts/build_performance_tracking.py`.")
        return

    df = per_tester_df.copy()
    df["display"] = df.apply(
        lambda r: f"{S.TIER_EMOJI.get(str(r['tier']).lower(), '⚪')}  {r['tester_name']} "
        f"({int(r.get('submission_count', 0))} sub.)",
        axis=1,
    )
    df = df.sort_values(["tester_name"])

    selected_label = st.selectbox(
        f"Tester ({len(df)})",
        options=df["display"].tolist(),
    )
    row = df[df["display"] == selected_label].iloc[0]

    # Hero
    delta = _safe_float(row.get("delta_first_to_last"))
    sub_ids = _safe_split_csv(row.get("submission_video_ids"))
    sub_scores_raw = [_safe_float(s) for s in _safe_split_csv(row.get("submission_scores"))]
    sub_tiers = _safe_split_csv(row.get("submission_tiers"))
    n_total = int(row.get("submission_count") or 0)
    n_scored = int(row.get("submission_count_scored") or 0)
    score_v = _safe_float(row.get("score"))

    stats = [
        ("Aggregate", _fmt(score_v)),
        ("Direction", str(row.get("direction") or "—")),
    ]
    if delta is not None:
        sign = "+" if delta > 0 else ""
        stats.append(("Δ first→last", f"{sign}{delta:.0f}"))
    stats.append(("Submissions", f"{n_scored}/{n_total} scored"))

    projects_short = ", ".join(
        sorted({C.project_short(p) for p in _safe_split_csv(row.get("projects"))})
    ) or "—"

    C.hero_card(
        title=str(row["tester_name"]),
        subtitle=f"Projects: {projects_short}",
        tier=row.get("tier"),
        stats=stats,
    )

    # Trajectory chart
    if sub_ids and sub_scores_raw and len(sub_ids) == len(sub_scores_raw):
        st.markdown("##### Submission scores")
        projects_list = _safe_split_csv(row.get("projects"))
        if len(projects_list) == len(sub_ids):
            x_labels = [C.project_short(p) for p in projects_list]
        else:
            x_labels = sub_ids
        traj = pd.DataFrame({
            "order": list(range(1, len(sub_ids) + 1)),
            "submission": sub_ids,
            "project": x_labels,
            "score": sub_scores_raw,
            "tier": sub_tiers + [""] * (len(sub_ids) - len(sub_tiers)),
        })
        traj_plot = traj.dropna(subset=["score"])
        if len(traj_plot) >= 1:
            chart = (
                alt.Chart(traj_plot)
                .mark_line(
                    color=S.USYD_RED,
                    strokeWidth=2.5,
                    point=alt.OverlayMarkDef(
                        size=140, filled=True, color=S.USYD_RED, stroke=S.WHITE, strokeWidth=2,
                    ),
                )
                .encode(
                    x=alt.X(
                        "order:O",
                        title=None,
                        axis=alt.Axis(
                            labelAngle=0,
                            labelFontSize=12,
                            labelExpr=(
                                "{"
                                + ", ".join(f"{r.order}: '{r.project}'" for r in traj_plot.itertuples())
                                + "}[datum.value]"
                            ),
                        ),
                    ),
                    y=alt.Y(
                        "score:Q",
                        title="Score",
                        scale=alt.Scale(domain=[0, 100]),
                        axis=alt.Axis(
                            values=[0, 25, 50, 75, 100],
                            labelFontSize=11,
                            titleFontSize=12,
                            grid=True,
                            gridColor=S.SLATE_100,
                        ),
                    ),
                    tooltip=[
                        alt.Tooltip("submission:N", title="Submission"),
                        alt.Tooltip("project:N", title="Project"),
                        alt.Tooltip("score:Q", title="Score"),
                        alt.Tooltip("tier:N", title="Tier"),
                    ],
                )
                .properties(height=240)
                .configure_view(stroke=None)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.caption("No scored submissions in this trajectory.")
        st.dataframe(
            traj.drop(columns=["order"]),
            use_container_width=True,
            hide_index=True,
        )

    # Persistent friction + sentiment in one row
    persistent = _safe_split_csv(row.get("persistent_friction_types"))
    sent_dist_raw = row.get("sentiment_distribution")

    p_col, s_col = st.columns(2)
    with p_col:
        st.markdown("##### Persistent friction types")
        if persistent:
            st.markdown("".join(C.gray_chip(p) for p in persistent), unsafe_allow_html=True)
            st.caption(
                ", ".join(f"{p} = {S.FRICTION_LABELS.get(p, '')}" for p in persistent if p in S.FRICTION_LABELS)
            )
        else:
            st.caption("No friction type recurs in top-3 across multiple submissions.")
    with s_col:
        st.markdown("##### Sentiment roll-up")
        if isinstance(sent_dist_raw, str) and sent_dist_raw.strip():
            try:
                parsed = json.loads(sent_dist_raw.replace("'", '"'))
                if isinstance(parsed, dict) and parsed:
                    C.distribution_bar({k: int(v) for k, v in parsed.items()})
                else:
                    st.caption("(empty)")
            except (ValueError, json.JSONDecodeError):
                st.caption(f"Raw: {sent_dist_raw}")
        else:
            st.caption("(no sentiment roll-up)")

    # Compact metadata strip
    lane = row.get("cross_check_lanes") or "—"
    cal_mm = _safe_int(row.get("calibrator_aggregate_mismatch_count"))
    ordering = row.get("ordering_basis") or "—"
    parts = [
        f"Cross-check lane(s): `{lane}`",
        f"Ordering: `{ordering}`",
    ]
    if cal_mm and cal_mm > 0:
        parts.append(f"⚠️ Calibrator mismatch on {cal_mm} submission(s)")
    st.caption(" · ".join(parts))


# ---------------------------------------------------------------------------
# View: Cohort Overview
# ---------------------------------------------------------------------------

def _view_cohort_overview(
    summary_df: Optional[pd.DataFrame],
    per_submission_df: Optional[pd.DataFrame],
    per_tester_df: Optional[pd.DataFrame],
) -> None:
    if summary_df is None:
        st.warning("`_summary_dev55.csv` unavailable.")
        return

    n_videos = len(summary_df)
    n_testers = (
        per_tester_df["tester_name"].nunique() if per_tester_df is not None
        else summary_df["tester"].nunique()
    )
    cap_str = "—"
    median_score_str = "—"
    if per_submission_df is not None and not per_submission_df.empty:
        cap_count = (
            per_submission_df["cap_applied"].notna().sum()
            - (per_submission_df["cap_applied"] == "").sum()
            if "cap_applied" in per_submission_df.columns else 0
        )
        cap_str = f"{cap_count} / {len(per_submission_df)} ({100.0 * cap_count / len(per_submission_df):.0f}%)"
        try:
            median_score_str = f"{per_submission_df['score'].median():.0f}"
        except (KeyError, TypeError):
            pass

    # Hero
    C.hero_card(
        title="Cohort overview",
        subtitle="dev55 — the 55 official development videos",
        stats=[
            ("Videos", str(n_videos)),
            ("Testers", str(n_testers)),
            ("Median score", median_score_str),
            ("Caps applied", cap_str),
        ],
    )

    # R6 4-tier distribution (the meaningful view; fusion 3-tier omitted to avoid duplicate)
    if per_submission_df is not None and "tier" in per_submission_df.columns:
        st.markdown("##### Per-submission score tier (R6, post-cap)")
        order = ["Leading", "Proficient", "Developing", "Foundational"]
        counts = per_submission_df["tier"].value_counts()
        ordered = {t: int(counts.get(t, 0)) for t in order if counts.get(t, 0) > 0}
        # use TIER_COLORS keyed by lowercase
        color_map = {t: S.TIER_COLORS[t.lower()] for t in ordered if t.lower() in S.TIER_COLORS}
        # distribution_bar takes literal keys; pass the cased keys to keep labels readable
        C.distribution_bar(ordered, color_map=color_map)

    # Per-project tier breakdown — short names
    if "project" in summary_df.columns and "tier" in summary_df.columns:
        st.markdown("##### Per-project tier (fusion output)")
        cohort = summary_df.copy()
        cohort["project_s"] = cohort["project"].map(C.project_short)
        proj_tier = cohort.groupby(["project_s", "tier"]).size().unstack(fill_value=0)
        # ensure column ordering poor->acceptable->good for visual flow
        for col in ["poor", "acceptable", "good"]:
            if col not in proj_tier.columns:
                proj_tier[col] = 0
        proj_tier = proj_tier[["poor", "acceptable", "good"]]
        st.bar_chart(proj_tier, height=220)

    # Top friction (horizontal bar of F1-F7 frequency)
    if per_submission_df is not None and "top_friction_types" in per_submission_df.columns:
        st.markdown("##### Top friction types — frequency in submission top-3")
        all_ft: list[str] = []
        for v in per_submission_df["top_friction_types"].dropna():
            all_ft.extend(_safe_split_csv(v))
        if all_ft:
            ft_counts = pd.Series(all_ft).value_counts().reindex(
                [f"F{i}" for i in range(1, 8)], fill_value=0
            )
            ft_df = pd.DataFrame({
                "friction": [f"{f} {S.FRICTION_LABELS.get(f, '')}" for f in ft_counts.index],
                "count": ft_counts.values,
            }).set_index("friction")
            st.bar_chart(ft_df, height=240, horizontal=True)

    # Trajectory split as inline distribution bar
    if per_tester_df is not None and "direction" in per_tester_df.columns:
        st.markdown("##### Trajectory direction (testers with ≥2 scored submissions)")
        scored = per_tester_df[per_tester_df["submission_count_scored"].fillna(0) >= 2]
        if not scored.empty:
            dir_counts = scored["direction"].value_counts().to_dict()
            ordered = {
                "improving": int(dir_counts.get("improving", 0)),
                "stable": int(dir_counts.get("stable", 0)),
                "declining": int(dir_counts.get("declining", 0)),
            }
            C.distribution_bar(
                {k: v for k, v in ordered.items() if v > 0},
                color_map={
                    "improving": S.TIER_COLORS["good"],
                    "stable": {"bg": S.SLATE_200, "fg": S.SLATE_700},
                    "declining": S.TIER_COLORS["poor"],
                },
            )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(v: Any) -> str:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "—"
    if pd.isna(f):
        return "—"
    return f"{f:.1f}" if abs(f) < 100 else f"{f:.0f}"


def _safe_float(v: Any) -> Optional[float]:
    try:
        f = float(v)
        return None if pd.isna(f) else f
    except (TypeError, ValueError):
        return None


def _safe_int(v: Any) -> Optional[int]:
    try:
        f = float(v)
        return None if pd.isna(f) else int(f)
    except (TypeError, ValueError):
        return None


def _safe_split_csv(v: Any) -> list[str]:
    """Split a comma-delimited string column. Returns [] on missing/nan."""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    s = str(v).strip()
    if not s or s.lower() in {"nan", "none"}:
        return []
    return [x.strip() for x in s.split(",") if x.strip()]


def escape_safe(s: Any) -> str:
    from html import escape
    return escape(str(s))


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

    # USyd-red top ribbon
    st.markdown(
        f'<div style="border-top:4px solid {S.USYD_RED}; margin:-16px -16px 14px -16px;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<h1 style='margin-bottom:0;'>Intelligent Tester Quality Assessment</h1>"
        f"<div style='color:{S.SLATE_500}; font-size:0.92rem; margin-bottom:14px;'>"
        f"USyd CS20 · See Me Please · decision-support prototype</div>",
        unsafe_allow_html=True,
    )

    report_files = _load_report_files(str(REPORT_DIR))
    if not report_files:
        st.error(
            f"No JSON reports in {REPORT_DIR}. "
            "Run `python scripts/run_pipeline.py --all` first."
        )
        st.stop()

    summary_df = _load_csv(str(SUMMARY_PATH))
    findings_full = _load_csv(str(FINDINGS_PATH))
    per_submission_df = _load_csv(str(PER_SUBMISSION_PATH))
    per_tester_df = _load_csv(str(PER_TESTER_PATH))

    view, selected_video = _sidebar(summary_df, report_files)

    if view == "Single Video":
        if not selected_video:
            st.info("Select a video from the sidebar.")
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
            _view_single_video(
                selected_video,
                report=report,
                submission_row=sub_row,
                findings_full=findings_full,
            )

    elif view == "Tester Trajectory":
        _view_tester_trajectory(per_tester_df)

    elif view == "Cohort Overview":
        _view_cohort_overview(summary_df, per_submission_df, per_tester_df)

    C.footer(commit="d68c9cb", data_date="2026-05-07 · dev55 official")


if __name__ == "__main__":
    main()
