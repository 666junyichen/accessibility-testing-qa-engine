from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st


REPORT_DIR = Path("data/processed/reports/dev55")
SUMMARY_PATH = Path("data/processed/reports/_summary_dev55.csv")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_report_files(report_dir: Path) -> list[Path]:
    if not report_dir.exists():
        return []

    return sorted(
        p for p in report_dir.glob("*.json")
        if not p.name.startswith("_")
    )


def flatten_dict(d: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for key, value in d.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        rows.append({"Field": key, "Value": value})
    return pd.DataFrame(rows)


def show_section(title: str, data: Any) -> None:
    st.subheader(title)

    if data is None:
        st.info("Not available in this report.")
    elif isinstance(data, dict):
        st.dataframe(flatten_dict(data), use_container_width=True)
    elif isinstance(data, list):
        if len(data) == 0:
            st.info("No records.")
        elif all(isinstance(x, dict) for x in data):
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.json(data)
    else:
        st.write(data)


def main() -> None:
    st.set_page_config(
        page_title="SMP Quality Report Demo",
        layout="wide",
    )

    st.title("SMP Quality Report Demo")
    st.caption("Step 7.2 demo: summary overview + detailed QualityReport viewer.")

    report_files = find_report_files(REPORT_DIR)

    if not report_files:
        st.error(f"No JSON reports found in: {REPORT_DIR}")
        st.stop()

    summary_df = None
    if SUMMARY_PATH.exists():
        summary_df = pd.read_csv(SUMMARY_PATH)

    video_options = {path.stem: path for path in report_files}

    selected_video = st.sidebar.selectbox(
        "Select video",
        options=list(video_options.keys()),
    )

    report_path = video_options[selected_video]
    report = load_json(report_path)

    st.sidebar.write("Selected JSON:")
    st.sidebar.code(str(report_path))

    # -----------------------
    # Summary CSV information
    # -----------------------
    st.header("Summary Overview")

    if summary_df is not None and "video_id" in summary_df.columns:
        selected_summary = summary_df[summary_df["video_id"] == selected_video]

        if not selected_summary.empty:
            row = selected_summary.iloc[0]

            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                st.metric("Video ID", row.get("video_id", "N/A"))

            with row1_col2:
                st.metric("Project", row.get("project", "N/A"))

            row2_col1, row2_col2, row2_col3 = st.columns(3)
            
            with row2_col1:
                st.metric("Tester", row.get("tester", "N/A"))

            with row2_col2:
                st.metric("Tier", row.get("tier", "N/A"))

            with row2_col3:
                st.metric("L3 Findings", row.get("l3_findings", "N/A"))

            st.write("Reason:")
            st.info(row.get("reason", "N/A"))

            with st.expander("View selected summary row"):
                st.dataframe(selected_summary, use_container_width=True)

        else:
            st.warning("This video exists as a JSON report, but it was not found in _summary.csv.")
    else:
        st.warning("_summary.csv was not found or does not contain video_id.")

    st.divider()

    # -----------------------
    # Detailed JSON report
    # -----------------------
    st.header("Detailed Quality Report")

    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
        st.metric("Video ID", report.get("video_id", "N/A"))
        
    with row1_col2:
        st.metric("Project", report.get("project", "N/A"))
        
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.metric("Tester", report.get("tester_name", "N/A"))
    
    with row2_col2:
        st.metric("Quality Tier", report.get("overall", {}).get("quality_tier", "N/A"))
        

    show_section("Basic Information", {
        "total_windows": report.get("total_windows"),
        "duration_sec": report.get("duration_sec"),
    })

    show_section("Layer 1 Summary", report.get("l1"))
    show_section("Layer 2 Summary", report.get("l2"))
    show_section("Layer 3 Findings", report.get("l3_findings"))
    show_section("Layer 3 Assessment", report.get("l3_assessment"))
    show_section("Overall Assessment", report.get("overall"))
    show_section("Coaching Recommendations", report.get("coaching_recommendations"))

    with st.expander("View full raw JSON"):
        st.json(report)


if __name__ == "__main__":
    main()