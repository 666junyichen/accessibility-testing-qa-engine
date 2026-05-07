"""Visual design tokens and CSS for the SMP demo app.

Single source of truth for colors, spacing, and typography. Imported by
streamlit_demo.py once at startup; do not import from per-render code paths.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------

# Brand
USYD_RED = "#C8102E"
INK = "#0F172A"
SLATE_700 = "#334155"
SLATE_500 = "#64748B"
SLATE_300 = "#CBD5E1"
SLATE_100 = "#F1F5F9"
SLATE_50 = "#F8FAFC"
WHITE = "#FFFFFF"

# Quality tier
TIER_COLORS = {
    "good": {"bg": "#DCFCE7", "fg": "#166534", "border": "#16A34A"},
    "acceptable": {"bg": "#FEF3C7", "fg": "#92400E", "border": "#F59E0B"},
    "poor": {"bg": "#FEE2E2", "fg": "#991B1B", "border": "#DC2626"},
    "leading": {"bg": "#DCFCE7", "fg": "#166534", "border": "#16A34A"},
    "proficient": {"bg": "#DBEAFE", "fg": "#1E40AF", "border": "#3B82F6"},
    "developing": {"bg": "#FEF3C7", "fg": "#92400E", "border": "#F59E0B"},
    "foundational": {"bg": "#FEE2E2", "fg": "#991B1B", "border": "#DC2626"},
}

# Severity (S1 worst -> S6 mildest)
SEVERITY_COLORS = {
    "S1": {"bg": "#FECACA", "fg": "#7F1D1D"},
    "S2": {"bg": "#FED7AA", "fg": "#9A3412"},
    "S3": {"bg": "#FEF08A", "fg": "#854D0E"},
    "S4": {"bg": "#D9F99D", "fg": "#365314"},
    "S5": {"bg": "#E2E8F0", "fg": "#334155"},
    "S6": {"bg": "#F1F5F9", "fg": "#64748B"},
}

# Friction type chips (F1-F7)
FRICTION_COLORS = {
    "F1": {"bg": "#E0E7FF", "fg": "#3730A3"},  # Comprehension
    "F2": {"bg": "#FCE7F3", "fg": "#9D174D"},  # Confidence
    "F3": {"bg": "#CFFAFE", "fg": "#155E75"},  # Accessibility
    "F4": {"bg": "#FEE2E2", "fg": "#991B1B"},  # Unresponsive
    "F5": {"bg": "#FEF3C7", "fg": "#92400E"},  # Unexpected
    "F6": {"bg": "#DDD6FE", "fg": "#5B21B6"},  # Content not found
    "F7": {"bg": "#E0F2FE", "fg": "#075985"},  # Excessive Effort
}

FRICTION_LABELS = {
    "F1": "Comprehension",
    "F2": "Confidence",
    "F3": "Accessibility",
    "F4": "Unresponsive",
    "F5": "Unexpected",
    "F6": "Not Found",
    "F7": "Excessive Effort",
}

# Sentiment chips
SENTIMENT_COLORS = {
    "E1": {"bg": "#FECACA", "fg": "#7F1D1D"},
    "E2": {"bg": "#FED7AA", "fg": "#9A3412"},
    "E3": {"bg": "#E2E8F0", "fg": "#334155"},
    "E4": {"bg": "#DBEAFE", "fg": "#1E40AF"},
    "E5": {"bg": "#DCFCE7", "fg": "#166534"},
}
SENTIMENT_LABELS = {
    "E1": "Strongly negative",
    "E2": "Negative",
    "E3": "Neutral",
    "E4": "Positive",
    "E5": "Strongly positive",
}

# Coaching category icons
CATEGORY_ICONS = {
    "narration": "🎙️",
    "recording": "🎬",
    "moderation": "👤",
}

# Tier emoji for sidebar
TIER_EMOJI = {
    "good": "🟢",
    "acceptable": "🟡",
    "poor": "🔴",
    "leading": "🟢",
    "proficient": "🔵",
    "developing": "🟡",
    "foundational": "🔴",
}


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

GLOBAL_CSS = f"""
<style>
  /* Page-wide typography & spacing */
  .stApp {{
    background-color: {SLATE_50};
  }}
  h1, h2, h3 {{
    color: {INK};
    font-weight: 700;
    letter-spacing: -0.01em;
  }}
  h1 {{ font-size: 2.0rem; }}
  h2 {{ font-size: 1.4rem; margin-top: 1.5rem; }}
  h3 {{ font-size: 1.15rem; margin-top: 1.0rem; }}

  /* Streamlit metric card */
  div[data-testid="stMetric"] {{
    background-color: {WHITE};
    border: 1px solid {SLATE_300};
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  }}
  div[data-testid="stMetricLabel"] {{
    font-size: 0.78rem;
    color: {SLATE_500};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
  }}
  div[data-testid="stMetricValue"] {{
    font-size: 1.6rem;
    color: {INK};
    font-weight: 700;
  }}

  /* Container card */
  .smp-card {{
    background-color: {WHITE};
    border: 1px solid {SLATE_300};
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  }}

  /* Hero card (top of single video view) */
  .smp-hero {{
    background: linear-gradient(135deg, {WHITE} 0%, {SLATE_50} 100%);
    border-left: 5px solid {USYD_RED};
    border-radius: 12px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.08);
  }}
  .smp-hero h2 {{
    margin: 0 0 4px 0;
    font-size: 1.5rem;
    color: {INK};
  }}
  .smp-hero .smp-subtitle {{
    color: {SLATE_500};
    font-size: 0.95rem;
    margin-bottom: 14px;
  }}
  .smp-hero-grid {{
    display: flex;
    gap: 28px;
    flex-wrap: wrap;
    align-items: center;
  }}
  .smp-hero-stat {{
    display: flex;
    flex-direction: column;
  }}
  .smp-hero-stat .label {{
    font-size: 0.72rem;
    color: {SLATE_500};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }}
  .smp-hero-stat .value {{
    font-size: 1.3rem;
    color: {INK};
    font-weight: 700;
    margin-top: 2px;
  }}

  /* Tier badge */
  .tier-badge {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
    border: 1.5px solid;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  .tier-badge-lg {{
    padding: 10px 22px;
    font-size: 1.05rem;
  }}

  /* Severity / friction / sentiment chips */
  .smp-chip {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 4px;
    white-space: nowrap;
  }}

  /* Coaching card */
  .coaching-card {{
    background-color: {WHITE};
    border: 1px solid {SLATE_300};
    border-left: 4px solid {USYD_RED};
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
  }}
  .coaching-card .icon {{
    font-size: 1.3rem;
    margin-right: 8px;
  }}
  .coaching-card .title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {INK};
    margin-bottom: 4px;
  }}
  .coaching-card .summary {{
    color: {SLATE_700};
    font-size: 0.92rem;
    margin-bottom: 12px;
    line-height: 1.55;
  }}
  .coaching-card ul {{
    margin: 0;
    padding-left: 20px;
    color: {SLATE_700};
    font-size: 0.9rem;
    line-height: 1.7;
  }}
  .coaching-card .meta {{
    color: {SLATE_500};
    font-size: 0.78rem;
    margin-top: 12px;
    border-top: 1px solid {SLATE_100};
    padding-top: 10px;
  }}

  /* Finding row */
  .finding-row {{
    background-color: {WHITE};
    border: 1px solid {SLATE_300};
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
  }}
  .finding-row .head {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 8px;
  }}
  .finding-row .body {{
    color: {INK};
    font-size: 0.92rem;
    line-height: 1.6;
    margin-bottom: 6px;
  }}
  .finding-row .quote {{
    background-color: {SLATE_50};
    border-left: 3px solid {SLATE_300};
    padding: 8px 12px;
    color: {SLATE_700};
    font-size: 0.86rem;
    font-style: italic;
    margin-top: 6px;
    border-radius: 4px;
  }}
  .finding-row .window-id {{
    color: {SLATE_500};
    font-size: 0.78rem;
    font-family: 'SF Mono', Menlo, Consolas, monospace;
  }}

  /* Footer */
  .smp-footer {{
    margin-top: 48px;
    padding-top: 16px;
    border-top: 1px solid {SLATE_300};
    color: {SLATE_500};
    font-size: 0.78rem;
    text-align: center;
    line-height: 1.7;
  }}
  .smp-footer code {{
    background-color: {SLATE_100};
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.75rem;
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background-color: {WHITE};
    border-right: 1px solid {SLATE_300};
  }}
  section[data-testid="stSidebar"] h2 {{
    color: {USYD_RED};
    font-size: 1.1rem;
    margin-bottom: 16px;
  }}

  /* Tabs */
  button[data-baseweb="tab"] {{
    font-weight: 600;
    color: {SLATE_500};
  }}
  button[data-baseweb="tab"][aria-selected="true"] {{
    color: {USYD_RED};
  }}

  /* Hide streamlit branding */
  #MainMenu {{ visibility: hidden; }}
  footer[data-testid="stFooter"] {{ visibility: hidden; }}
</style>
"""
