"""Reusable UI components for the SMP demo app.

Design discipline:
- Tier and severity are colored (they drive judgement).
- Friction / sentiment / calibrator / alignment chips are grayscale + code only.
  Their meaning is in position, count, and grouping — not in hue.
"""
from __future__ import annotations

from html import escape
from typing import Any, Iterable, Optional

import pandas as pd
import streamlit as st

from . import styles as S


# ---------------------------------------------------------------------------
# Atoms — chips
# ---------------------------------------------------------------------------

def tier_badge(tier: str, *, large: bool = False) -> str:
    tier_lower = (tier or "").lower()
    palette = S.TIER_COLORS.get(
        tier_lower, {"bg": S.SLATE_100, "fg": S.SLATE_500, "border": S.SLATE_200}
    )
    cls = "tier-badge tier-badge-lg" if large else "tier-badge"
    return (
        f'<span class="{cls}" '
        f'style="background:{palette["bg"]}; color:{palette["fg"]}; '
        f'border-color:{palette["border"]};">{escape(str(tier or "—"))}</span>'
    )


def severity_chip(sev: str) -> str:
    palette = S.SEVERITY_COLORS.get(sev, S.GRAY_CHIP)
    return (
        f'<span class="smp-chip" style="background:{palette["bg"]}; color:{palette["fg"]};">'
        f"{escape(sev)}</span>"
    )


def gray_chip(text: str, *, muted: bool = False) -> str:
    """Inline gray chip — for friction / sentiment / calibrator / alignment."""
    palette = S.GRAY_CHIP_MUTED if muted else S.GRAY_CHIP
    return (
        f'<span class="smp-chip" style="background:{palette["bg"]}; color:{palette["fg"]};">'
        f"{escape(text)}</span>"
    )


# ---------------------------------------------------------------------------
# Hero card
# ---------------------------------------------------------------------------

def hero_card(
    *,
    title: str,
    subtitle: str,
    tier: Optional[str] = None,
    stats: Iterable[tuple[str, str]] = (),
    cap_reasons: Optional[Iterable[str]] = None,
) -> None:
    """Generic top-of-page hero. `stats` is an iterable of (label, value)."""
    tier_html = ""
    if tier:
        tier_html = (
            f'<div class="smp-hero-stat"><span class="label">Tier</span>'
            f'<span class="value">{tier_badge(tier, large=True)}</span></div>'
        )
    stat_html = "".join(
        f'<div class="smp-hero-stat"><span class="label">{escape(label)}</span>'
        f'<span class="value">{value}</span></div>'
        for label, value in stats
    )
    caps_html = ""
    if cap_reasons:
        cap_chips = " ".join(escape(c) for c in cap_reasons if c)
        if cap_chips:
            caps_html = f'<div class="smp-hero-cap"><strong>Cap reasons:</strong> {cap_chips}</div>'

    st.markdown(
        (
            f'<div class="smp-hero">'
            f'<h2>{escape(title)}</h2>'
            f'<div class="subtitle">{escape(subtitle)}</div>'
            f'<div class="smp-hero-grid">{tier_html}{stat_html}</div>'
            f'{caps_html}'
            f'</div>'
        ),
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Coaching card
# ---------------------------------------------------------------------------

def coaching_card(rec: dict[str, Any]) -> None:
    cat = (rec.get("category") or "").lower()
    icon = S.CATEGORY_ICONS.get(cat, "📋")
    title = escape(rec.get("title") or "Untitled")
    summary = escape(rec.get("summary") or "")
    advice_items = rec.get("advice") or []
    advice_html = "".join(f"<li>{escape(str(a))}</li>" for a in advice_items)

    priority = rec.get("priority")
    trigger_field = rec.get("trigger_field", "")
    trigger_value = rec.get("trigger_value", "")
    meta_parts = []
    if priority is not None:
        meta_parts.append(f"Priority {priority}")
    if trigger_field:
        meta_parts.append(f"{trigger_field}={trigger_value}")
    meta_text = " · ".join(meta_parts)

    st.markdown(
        f"""
        <div class="coaching-card">
          <div class="title"><span class="icon">{icon}</span>{title}</div>
          <div class="summary">{summary}</div>
          <ul>{advice_html}</ul>
          <div class="meta">{meta_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Finding row — minimal: severity color + friction code (gray) + window id
# Details (sentiment / calibrator / alignment / observed_signal / rationale)
# go in a <details> dropdown so the row stays clean.
# ---------------------------------------------------------------------------

def finding_row(f: dict[str, Any]) -> None:
    sev = f.get("severity_s") or "—"
    ft = f.get("friction_type") or ""
    window = f.get("window_id") or ""
    finding_text = escape(f.get("finding") or "")

    head_chips = []
    head_chips.append(severity_chip(sev))
    if ft:
        head_chips.append(gray_chip(ft))

    chips_html = "".join(head_chips)
    window_html = f'<span class="window-id">{escape(window)}</span>' if window else ""

    # Detail rows — only include what's present
    detail_rows = []
    if f.get("sentiment_e"):
        detail_rows.append(("Sentiment", f"{f['sentiment_e']} · {S.SENTIMENT_LABELS.get(f['sentiment_e'], '')}"))
    if f.get("calibrator_score_l"):
        detail_rows.append(("Calibrator", str(f["calibrator_score_l"])))
    if f.get("signal_alignment"):
        detail_rows.append(("Signal alignment", str(f["signal_alignment"])))
    if f.get("observed_signal"):
        detail_rows.append(("Observed", str(f["observed_signal"])))
    if f.get("rationale"):
        detail_rows.append(("Rationale", str(f["rationale"])))

    details_html = ""
    if detail_rows:
        rows_html = "".join(
            f'<div style="margin-top:6px;"><strong style="color:{S.SLATE_500}; font-size:0.75rem; '
            f'text-transform:uppercase; letter-spacing:0.04em;">{escape(label)}:</strong> '
            f'<span style="color:{S.SLATE_700}; font-size:0.85rem;">{escape(value)}</span></div>'
            for label, value in detail_rows
        )
        details_html = (
            '<details><summary>More detail</summary>'
            f'<div style="margin-top:8px;">{rows_html}</div></details>'
        )

    stated = f.get("stated_signal")

    if pd.isna(stated) or stated is None:
        quote_html = ""
    else:
        quote_html = f'<div class="quote">"{escape(str(stated))}"</div>'

    st.markdown(
        f"""
        <div class="finding-row">
          <div class="head">{chips_html}{window_html}</div>
          <div class="body">{finding_text}</div>
          {quote_html}
          {details_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Distribution bar — horizontal stacked, color_map controls hue
# ---------------------------------------------------------------------------

def distribution_bar(counts: dict[str, int], color_map: Optional[dict] = None) -> None:
    if not counts or sum(counts.values()) == 0:
        st.caption("(no data)")
        return
    total = sum(counts.values())
    color_map = color_map or {}
    segs = []
    for k in sorted(counts.keys()):
        v = counts[k]
        if v == 0:
            continue
        palette = color_map.get(k, S.GRAY_CHIP)
        pct = 100.0 * v / total
        segs.append(
            f'<div class="seg" title="{escape(k)}: {v} ({pct:.0f}%)" '
            f'style="flex:{v}; background:{palette["bg"]}; color:{palette["fg"]};">'
            f"{escape(k)} · {v}</div>"
        )
    st.markdown(f'<div class="dist-bar">{"".join(segs)}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Sidebar option label with tier emoji
# ---------------------------------------------------------------------------

def video_option_label(video_id: str, tier: Optional[str]) -> str:
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
        "Decision support — not replacing human review. "
        "USyd CS20 · See Me Please."
    )
    body = " · ".join(parts)
    st.markdown(f'<div class="smp-footer">{body}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Helpers reused across views
# ---------------------------------------------------------------------------

def project_short(project: Optional[str]) -> str:
    if not project:
        return "—"
    return S.PROJECT_SHORTNAMES.get(project, project)
