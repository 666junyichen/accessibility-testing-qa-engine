"""Visual design tokens and CSS for the SMP demo app.

Design principle: color = signal, not decoration.
Only TIER and SEVERITY use saturated color (they drive judgement).
Friction / sentiment / calibrator / alignment use grayscale + code, so the
eye is not pulled by 5 competing color systems.
"""
from __future__ import annotations


# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------

USYD_RED = "#C8102E"
INK = "#0F172A"
SLATE_700 = "#334155"
SLATE_500 = "#64748B"
SLATE_400 = "#94A3B8"
SLATE_300 = "#CBD5E1"
SLATE_200 = "#E2E8F0"
SLATE_100 = "#F1F5F9"
SLATE_50 = "#F8FAFC"
WHITE = "#FFFFFF"


# Quality tier — saturated (key judgement signal)
TIER_COLORS = {
    "good": {"bg": "#DCFCE7", "fg": "#166534", "border": "#16A34A"},
    "acceptable": {"bg": "#FEF3C7", "fg": "#92400E", "border": "#F59E0B"},
    "poor": {"bg": "#FEE2E2", "fg": "#991B1B", "border": "#DC2626"},
    "leading": {"bg": "#DCFCE7", "fg": "#166534", "border": "#16A34A"},
    "proficient": {"bg": "#DBEAFE", "fg": "#1E40AF", "border": "#3B82F6"},
    "developing": {"bg": "#FEF3C7", "fg": "#92400E", "border": "#F59E0B"},
    "foundational": {"bg": "#FEE2E2", "fg": "#991B1B", "border": "#DC2626"},
}


# Severity — saturated (drives finding ordering & clinical attention)
SEVERITY_COLORS = {
    "S1": {"bg": "#FECACA", "fg": "#7F1D1D"},
    "S2": {"bg": "#FED7AA", "fg": "#9A3412"},
    "S3": {"bg": "#FEF08A", "fg": "#854D0E"},
    "S4": {"bg": "#D9F99D", "fg": "#365314"},
    "S5": {"bg": "#E2E8F0", "fg": "#334155"},
    "S6": {"bg": "#F1F5F9", "fg": "#64748B"},
}


# Friction / sentiment / calibrator: grayscale, code-only
GRAY_CHIP = {"bg": SLATE_100, "fg": SLATE_700}
GRAY_CHIP_MUTED = {"bg": SLATE_50, "fg": SLATE_500}


FRICTION_LABELS = {
    "F1": "Comprehension",
    "F2": "Confidence",
    "F3": "Accessibility",
    "F4": "Unresponsive",
    "F5": "Unexpected",
    "F6": "Not Found",
    "F7": "Excessive Effort",
}

SENTIMENT_LABELS = {
    "E1": "Strongly negative",
    "E2": "Negative",
    "E3": "Neutral",
    "E4": "Positive",
    "E5": "Strongly positive",
}


# Project shortname (full slug -> demo label)
PROJECT_SHORTNAMES = {
    "department-of-premier-and-cabinet-wa": "DPC-WA",
    "suncorp-insurance": "AAMI",
    "the-university-of-queensland": "UQ",
    "web-health-information": "Bupa",
    "web-health-information-bupa": "Bupa",
    "digital-brochure": "Brighton",
    "wa": "DPC-WA",
    "suncorp": "AAMI",
    "uq": "UQ",
}


# Coaching category icons
CATEGORY_ICONS = {
    "narration": "🎙️",
    "recording": "🎬",
    "moderation": "👤",
}


# Tier emoji for sidebar list
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
  .stApp {{
    background-color: {SLATE_50};
  }}

  h1, h2, h3 {{
    color: {INK};
    font-weight: 700;
    letter-spacing: -0.01em;
  }}
  h1 {{ font-size: 1.85rem; }}
  h2 {{ font-size: 1.3rem; margin-top: 1.4rem; }}
  h3 {{ font-size: 1.05rem; margin-top: 0.9rem; color: {SLATE_700}; }}
  h5 {{
    color: {SLATE_500};
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 700;
    margin-top: 1.2rem;
    margin-bottom: 0.5rem;
  }}

  /* Streamlit metric */
  div[data-testid="stMetric"] {{
    background-color: {WHITE};
    border: 1px solid {SLATE_200};
    border-radius: 10px;
    padding: 12px 16px;
  }}
  div[data-testid="stMetricLabel"] {{
    font-size: 0.75rem;
    color: {SLATE_500};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-weight: 600;
  }}
  div[data-testid="stMetricValue"] {{
    font-size: 1.5rem;
    color: {INK};
    font-weight: 700;
  }}

  /* Hero card */
  .smp-hero {{
    background: {WHITE};
    border-left: 4px solid {USYD_RED};
    border-radius: 10px;
    padding: 20px 26px;
    margin-bottom: 18px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
  }}
  .smp-hero h2 {{
    margin: 0 0 4px 0;
    font-size: 1.35rem;
    color: {INK};
  }}
  .smp-hero .subtitle {{
    color: {SLATE_500};
    font-size: 0.9rem;
    margin-bottom: 16px;
  }}
  .smp-hero-grid {{
    display: flex;
    gap: 32px;
    flex-wrap: wrap;
    align-items: flex-end;
  }}
  .smp-hero-stat {{
    display: flex;
    flex-direction: column;
    min-width: 70px;
  }}
  .smp-hero-stat .label {{
    font-size: 0.7rem;
    color: {SLATE_500};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
  }}
  .smp-hero-stat .value {{
    font-size: 1.4rem;
    color: {INK};
    font-weight: 700;
    margin-top: 2px;
    line-height: 1.2;
  }}
  .smp-hero-cap {{
    margin-top: 14px;
    padding-top: 12px;
    border-top: 1px solid {SLATE_100};
    font-size: 0.78rem;
    color: {SLATE_500};
  }}

  /* Compact info grid */
  .smp-info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 10px;
    margin: 2px 0 18px 0;
  }}
  .smp-info-card {{
    background: {WHITE};
    border: 1px solid {SLATE_200};
    border-radius: 10px;
    padding: 12px 14px;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
  }}
  .smp-info-card .label {{
    font-size: 0.72rem;
    color: {SLATE_500};
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-weight: 600;
    margin-bottom: 4px;
  }}
  .smp-info-card .value {{
    font-size: 0.95rem;
    line-height: 1.45;
    color: {INK};
    font-weight: 600;
  }}

  /* Tier badge */
  .tier-badge {{
    display: inline-block;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1.5px solid;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }}
  .tier-badge-lg {{
    padding: 8px 18px;
    font-size: 0.95rem;
  }}

  /* Chip */
  .smp-chip {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 4px;
    white-space: nowrap;
    line-height: 1.6;
  }}

  /* Coaching card */
  .coaching-card {{
    background-color: {WHITE};
    border: 1px solid {SLATE_200};
    border-left: 3px solid {USYD_RED};
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
  }}
  .coaching-card .icon {{
    font-size: 1.15rem;
    margin-right: 8px;
  }}
  .coaching-card .title {{
    font-size: 1rem;
    font-weight: 700;
    color: {INK};
    margin-bottom: 4px;
  }}
  .coaching-card .summary {{
    color: {SLATE_700};
    font-size: 0.9rem;
    margin-bottom: 10px;
    line-height: 1.55;
  }}
  .coaching-card ul {{
    margin: 0;
    padding-left: 18px;
    color: {SLATE_700};
    font-size: 0.88rem;
    line-height: 1.7;
  }}
  .coaching-card .meta {{
    color: {SLATE_500};
    font-size: 0.75rem;
    margin-top: 10px;
  }}

  /* Finding row */
  .finding-row {{
    background-color: {WHITE};
    border: 1px solid {SLATE_200};
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
  }}
  .finding-row .head {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    align-items: center;
    margin-bottom: 6px;
  }}
  .finding-row .head .window-id {{
    color: {SLATE_400};
    font-size: 0.74rem;
    font-family: 'SF Mono', Menlo, Consolas, monospace;
    margin-left: auto;
  }}
  .finding-row .body {{
    color: {INK};
    font-size: 0.9rem;
    line-height: 1.55;
  }}
  .finding-row details {{
    margin-top: 8px;
  }}
  .finding-row details summary {{
    cursor: pointer;
    color: {SLATE_500};
    font-size: 0.78rem;
    user-select: none;
  }}
  .finding-row details summary:hover {{
    color: {USYD_RED};
  }}
  .finding-row .quote {{
    background-color: {SLATE_50};
    border-left: 3px solid {SLATE_200};
    padding: 8px 12px;
    color: {SLATE_700};
    font-size: 0.85rem;
    font-style: italic;
    margin-top: 8px;
    border-radius: 4px;
  }}

  /* Footer */
  .smp-footer {{
    margin-top: 40px;
    padding-top: 14px;
    border-top: 1px solid {SLATE_200};
    color: {SLATE_400};
    font-size: 0.74rem;
    text-align: center;
    line-height: 1.7;
  }}
  .smp-footer code {{
    background-color: {SLATE_100};
    padding: 1px 6px;
    border-radius: 4px;
    font-size: 0.72rem;
    color: {SLATE_500};
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background-color: {WHITE};
    border-right: 1px solid {SLATE_200};
  }}
  section[data-testid="stSidebar"] h2 {{
    color: {USYD_RED};
    font-size: 1.05rem;
    margin-bottom: 14px;
  }}

  /* Tabs */
  button[data-baseweb="tab"] {{
    font-weight: 600;
    color: {SLATE_500};
  }}
  button[data-baseweb="tab"][aria-selected="true"] {{
    color: {USYD_RED};
  }}

  /* Dataframe softening */
  .stDataFrame {{
    border-radius: 8px;
    overflow: hidden;
  }}

  /* Popover trigger button — make it look like a select dropdown */
  div[data-testid="stPopover"] button[data-testid="baseButton-secondary"],
  div[data-testid="stPopover"] > button {{
    background-color: {WHITE} !important;
    border: 1px solid {SLATE_300} !important;
    color: {SLATE_700} !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    text-align: left !important;
    justify-content: space-between !important;
    padding: 6px 12px !important;
    height: auto !important;
    min-height: 36px !important;
  }}
  div[data-testid="stPopover"] > button:hover {{
    border-color: {USYD_RED} !important;
    color: {INK} !important;
  }}
  div[data-testid="stPopover"] > button::after {{
    content: "▾";
    color: {SLATE_400};
    margin-left: auto;
    font-size: 0.7rem;
  }}

  /* Inputs used around filters */
  div[data-testid="stTextInput"] input,
  div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    border-radius: 10px !important;
  }}

  /* Multiselect chip — neutral gray (override default red) */
  div[data-baseweb="select"] span[data-baseweb="tag"] {{
    background-color: {SLATE_100} !important;
    color: {SLATE_700} !important;
    border-radius: 999px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
  }}
  div[data-baseweb="select"] span[data-baseweb="tag"] span[role="presentation"] {{
    color: {SLATE_700} !important;
  }}
  div[data-baseweb="select"] span[data-baseweb="tag"] svg {{
    fill: {SLATE_500} !important;
  }}

  /* Hide streamlit branding */
  #MainMenu {{ visibility: hidden; }}
  footer[data-testid="stFooter"] {{ visibility: hidden; }}

  /* Dist bar segment text */
  .dist-bar {{
    display: flex;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid {SLATE_200};
    height: 26px;
    margin-bottom: 14px;
  }}
  .dist-bar .seg {{
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 600;
    min-width: 32px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 4px;
  }}
</style>
"""
