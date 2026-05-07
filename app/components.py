"""Reusable UI components for the SMP demo app.

Each function emits a small block of styled HTML/markdown via streamlit.
Components consume already-loaded report dicts and DataFrames; they do not
perform IO. Keep functions self-contained: a component should render
exactly one visual element.
"""
from __future__ import annotations

from html import escape
from typing import Any, Iterable, Optional

import pandas as pd
import streamlit as st

from . import styles as S


# ---------------------------------------------------------------------------
# Inline atoms
# ---------------------------------------------------------------------------

def tier_badge(tier: str, *, large: bool = False) -> str:
    """Return HTML string for a tier badge. Use via st.markdown(..., unsafe_allow_html=True)."""
    tier_lower = (tier or "").lower()
    palette = S.TIER_COLORS.get(tier_lower, {"bg": S.SLATE_100, "fg": S.SLATE_700, "border": S.SLATE_300})
    cls = "tier-badge tier-badge-lg" if large else "tier-badge"
    return (
        f'<span class="{cls}" '
        f'style="background:{palette["bg"]}; color:{palette["fg"]}; '
        f'border-color:{palette["border"]};">{escape(str(tier or "N/A"))}</span>'
    )


def severity_chip(sev: str) -> str:
    palette = S.SEVERITY_COLORS.get(sev, {"bg": S.SLATE_100, "fg": S.SLATE_700})
    return (
        f'<span class="smp-chip" style="background:{palette["bg"]}; color:{palette["fg"]};">'
        f'{escape(sev)}</span>'
    )


def friction_chip(ft: str) -> str:
    palette = S.FRICTION_COLORS.get(ft, {"bg": S.SLATE_100, "fg": S.SLATE_700})
    label = S.FRICTION_LABELS.get(ft, "")
    text = f"{ft} · {label}" if label else ft
    return (
        f'<span class="smp-chip" style="background:{palette["bg"]}; color:{palette["fg"]};">'
        f'{escape(text)}</span>'
    )


def sentiment_chip(e: str) -> str:
    palette = S.SENTIMENT_COLORS.get(e, {"bg": S.SLATE_100, "fg": S.SLATE_700})
    label = S.SENTIMENT_LABELS.get(e, "")
    text = f"{e} {label}" if label else e
    return (
        f'<span class="smp-chip" style="background:{palette["bg"]}; color:{palette["fg"]};">'
        f'{escape(text)}</span>'
    )


def calibrator_chip(l: str) -> str:
    """Calibrator score L1-L5; L1 best, L5 worst."""
    fg_map = {"L1": "#166534", "L2": "#1E40AF", "L3": "#854D0E", "L4": "#9A3412", "L5": "#7F1D1D"}
    bg_map = {"L1": "#DCFCE7", "L2": "#DBEAFE", "L3": "#FEF08A", "L4": "#FED7AA", "L5": "#FECACA"}
    bg = bg_map.get(l, S.SLATE_100)
    fg = fg_map.get(l, S.SLATE_700)
    return f'<span class="smp-chip" style="background:{bg}; color:{fg};">{escape(l)}</span>'


# ---------------------------------------------------------------------------
# Hero card
# ---------------------------------------------------------------------------

def hero_card(
    *,
    title: str,
    tester: str,
    project: str,
    tier: str,
    score: Optional[float] = None,
    duration_sec: Optional[float] = None,
    total_windows: Optional[int] = None,
    total_findings: Optional[int] = None,
    cap_reasons: Optional[Iterable[str]] = None,
) -> None:
    """Render the top-of-page hero card with key stats."""
    score_html = ""
    if score is not None:
        score_html = (
            f'<div class="smp-hero-stat"><span class="label">Score</span>'
            f'<span class="value">{score:.0f} / 100</span></div>'
        )

    duration_html = ""
    if duration_sec is not None and duration_sec > 0:
        mins = int(duration_sec // 60)
        secs = int(duration_sec % 60)
        duration_html = (
            f'<div class="smp-hero-stat"><span class="label">Duration</span>'
            f'<span class="value">{mins}m {secs:02d}s</span></div>'
        )

    windows_html = ""
    if total_windows is not None:
        windows_html = (
            f'<div class="smp-hero-stat"><span class="label">Windows</span>'
            f'<span class="value">{total_windows}</span></div>'
        )

    findings_html = ""
    if total_findings is not None:
        findings_html = (
            f'<div class="smp-hero-stat"><span class="label">Findings</span>'
            f'<span class="value">{total_findings}</span></div>'
        )

    tier_html = (
        f'<div class="smp-hero-stat"><span class="label">Tier</span>'
        f'<span class="value">{tier_badge(tier, large=True)}</span></div>'
    )

    caps_html = ""
    if cap_reasons:
        cap_chips = "".join(
            f'<span class="smp-chip" style="background:{S.SLATE_100}; color:{S.SLATE_700};">{escape(c)}</span>'
            for c in cap_reasons if c
        )
        if cap_chips:
            caps_html = f'<div style="margin-top:14px;"><span class="label" style="font-size:0.75rem; color:{S.SLATE_500}; text-transform:uppercase; letter-spacing:0.05em; font-weight:600;">Cap reasons</span><br>{cap_chips}</div>'

    st.markdown(
        f"""
        <div class="smp-hero">
          <h2>{escape(title)}</h2>
          <div class="smp-subtitle">{escape(tester)} · {escape(project)}</div>
          <div class="smp-hero-grid">
            {tier_html}
            {score_html}
            {findings_html}
            {windows_html}
            {duration_html}
          </div>
          {caps_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Coaching card
# ---------------------------------------------------------------------------

def coaching_card(rec: dict[str, Any]) -> None:
    """Render one coaching recommendation as a styled card."""
    cat = (rec.get("category") or "").lower()
    icon = S.CATEGORY_ICONS.get(cat, "📋")
    title = escape(rec.get("title") or "Untitled")
    summary = escape(rec.get("summary") or "")
    advice_items = rec.get("advice") or []
    advice_html = "".join(f"<li>{escape(str(a))}</li>" for a in advice_items)

    priority = rec.get("priority")
    trigger = f'{rec.get("trigger_field", "")}={rec.get("trigger_value", "")}'
    evidence = rec.get("evidence_note") or ""
    tags = rec.get("tags") or []
    tags_html = "".join(
        f'<span class="smp-chip" style="background:{S.SLATE_100}; color:{S.SLATE_500};">{escape(t)}</span>'
        for t in tags
    )

    meta_parts = []
    if priority is not None:
        meta_parts.append(f"Priority: {priority}")
    if trigger and trigger != "=":
        meta_parts.append(f"Trigger: <code>{escape(trigger)}</code>")
    if evidence:
        meta_parts.append(escape(evidence))
    meta_text = " · ".join(meta_parts)

    st.markdown(
        f"""
        <div class="coaching-card">
          <div class="title"><span class="icon">{icon}</span>{title}</div>
          <div class="summary">{summary}</div>
          <ul>{advice_html}</ul>
          <div class="meta">{meta_text}<br>{tags_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Finding row
# ---------------------------------------------------------------------------

def finding_row(f: dict[str, Any]) -> None:
    """Render one finding as a styled row with chips + quote."""
    chips = []
    if f.get("severity_s"):
        chips.append(severity_chip(f["severity_s"]))
    if f.get("friction_type"):
        chips.append(friction_chip(f["friction_type"]))
    if f.get("sentiment_e"):
        chips.append(sentiment_chip(f["sentiment_e"]))
    if f.get("calibrator_score_l"):
        chips.append(calibrator_chip(f["calibrator_score_l"]))
    if f.get("signal_alignment"):
        align = f["signal_alignment"]
        align_color = S.SLATE_500 if align == "aligned" else "#9A3412"
        chips.append(
            f'<span class="smp-chip" style="background:{S.SLATE_100}; color:{align_color};">{escape(align)}</span>'
        )

    chips_html = "".join(chips)
    finding_text = escape(f.get("finding") or "")
    window_id = escape(f.get("window_id") or "")
    stated = f.get("stated_signal") or ""
    quote_html = (
        f'<div class="quote">“{escape(stated)}”</div>' if stated else ""
    )

    st.markdown(
        f"""
        <div class="finding-row">
          <div class="head">{chips_html}<span class="window-id">· {window_id}</span></div>
          <div class="body">{finding_text}</div>
          {quote_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Distribution bar (horizontal stacked)
# ---------------------------------------------------------------------------

def distribution_bar(counts: dict[str, int], color_map: dict[str, dict], *, height: int = 24) -> None:
    """Render a horizontal stacked bar showing counts per category."""
    if not counts:
        st.caption("(no data)")
        return
    total = sum(counts.values())
    if total == 0:
        st.caption("(no data)")
        return

    segs = []
    for k in sorted(counts.keys()):
        v = counts[k]
        pct = 100.0 * v / total
        palette = color_map.get(k, {"bg": S.SLATE_300, "fg": S.SLATE_700})
        segs.append(
            f'<div title="{escape(k)}: {v} ({pct:.0f}%)" '
            f'style="flex:{v}; background:{palette["bg"]}; '
            f'color:{palette["fg"]}; height:{height}px; '
            f'display:flex; align-items:center; justify-content:center; '
            f'font-size:0.75rem; font-weight:600;">'
            f'{escape(k)} {v}</div>'
        )
    bar = (
        '<div style="display:flex; border-radius:6px; overflow:hidden; '
        'border:1px solid #CBD5E1;">' + "".join(segs) + "</div>"
    )
    st.markdown(bar, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar option label with tier emoji
# ---------------------------------------------------------------------------

def video_option_label(video_id: str, tier: Optional[str]) -> str:
    """Format a sidebar selectbox label as '🟡 video_id'."""
    emoji = S.TIER_EMOJI.get((tier or "").lower(), "⚪")
    return f"{emoji}  {video_id}"


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def footer(*, commit: str = "", data_date: str = "") -> None:
    parts = []
    if commit:
        parts.append(f"Commit <code>{escape(commit)}</code>")
    if data_date:
        parts.append(f"Data {escape(data_date)}")
    parts.append(
        "<strong>Decision support — not replacing human review.</strong> "
        "Internal SMP review-team prototype, USyd CS20 Capstone."
    )
    body = " · ".join(parts)
    st.markdown(f'<div class="smp-footer">{body}</div>', unsafe_allow_html=True)
