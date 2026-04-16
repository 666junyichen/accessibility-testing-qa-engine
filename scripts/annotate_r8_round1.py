from pathlib import Path
import pandas as pd

# =========================
# Paths
# =========================
TAXONOMY_PATH = Path("docs/friction_taxonomy.md")
PROMPT_PATH = Path("docs/prompt_design.md")
INPUT_PATH = Path("data/annotations/round1_blind_for_r8.csv")
OUTPUT_PATH = Path("data/annotations/r8_manual_annotations_round1.csv")

# Forbidden files (do not read)
FORBIDDEN_PATHS = [
    "data/annotations/r3_manual_annotations_round1.csv",
    "docs/cluster_interpretation.md",
    "docs/case_studies.md",
]

# =========================
# Allowed label values
# =========================
NARRATION_TYPES = [
    "thinking_aloud",
    "reading_page",
    "navigation",
    "feedback_evaluation",
    "task_response",
    "off_task",
    "unclear",
]

AT_CONTEXT_VALUES = ["yes", "no", "unclear"]

FRICTION_TYPES = [
    "F1",  # Navigation / Findability Issue
    "F2",  # Content Clarity Issue
    "F3",  # Interaction / Control Issue
    "F4",  # Accessibility / Assistive Technology Issue
    "F5",  # Task Understanding / Expectation Mismatch
    "F6",  # Support / Trust / Safety Concern
    "F7",  # No Clear Friction / Positive Feedback
]

SEVERITY_VALUES = ["none", "low", "medium", "high"]
SENTIMENT_VALUES = ["positive", "neutral", "negative", "mixed", "unclear"]
CONFIDENCE_VALUES = ["low", "medium", "high"]


def print_header():
    print("=" * 80)
    print("R8 Manual Annotation Tool - Round 1")
    print("=" * 80)
    print("This tool ONLY uses:")
    print(f"  - {TAXONOMY_PATH}")
    print(f"  - {PROMPT_PATH}")
    print(f"  - {INPUT_PATH}")
    print()
    print("It will NOT read the following files:")
    for p in FORBIDDEN_PATHS:
        print(f"  - {p}")
    print("=" * 80)
    print()


def read_guidelines():
    taxonomy_text = TAXONOMY_PATH.read_text(encoding="utf-8")
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    return taxonomy_text, prompt_text


def print_guideline_summary():
    print("\nAnnotation field summary")
    print("-" * 80)
    print("friction_type:")
    print("  F1 = Navigation / Findability Issue")
    print("  F2 = Content Clarity Issue")
    print("  F3 = Interaction / Control Issue")
    print("  F4 = Accessibility / Assistive Technology Issue")
    print("  F5 = Task Understanding / Expectation Mismatch")
    print("  F6 = Support / Trust / Safety Concern")
    print("  F7 = No Clear Friction / Positive Feedback")
    print()
    print("severity:")
    print("  none / low / medium / high")
    print()
    print("sentiment:")
    print("  positive / neutral / negative / mixed / unclear")
    print()
    print("narration_type:")
    print("  thinking_aloud / reading_page / navigation /")
    print("  feedback_evaluation / task_response / off_task / unclear")
    print()
    print("at_context_present:")
    print("  yes / no / unclear")
    print()
    print("confidence:")
    print("  low / medium / high")
    print("-" * 80)
    print()


def build_or_load_annotation_file():
    df = pd.read_csv(INPUT_PATH)

    base_cols = ["window_id", "project", "video_id", "task_title", "text"]
    missing = [c for c in base_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in input file: {missing}")

    if OUTPUT_PATH.exists():
        out = pd.read_csv(OUTPUT_PATH)
        print(f"Loaded existing annotation file: {OUTPUT_PATH}")
    else:
        out = df[base_cols].copy()
        out["narration_type"] = ""
        out["at_context_present"] = ""
        out["friction_type"] = ""
        out["severity"] = ""
        out["sentiment"] = ""
        out["confidence"] = ""
        out["notes"] = ""
        out["annotator"] = "R8"
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        print(f"Created new annotation file: {OUTPUT_PATH}")

    return out


def ask_choice(prompt, allowed, default=None):
    allowed_str = ", ".join(allowed)
    while True:
        if default:
            value = input(f"{prompt} [{allowed_str}] (Enter to keep '{default}'): ").strip()
            if value == "":
                return default
        else:
            value = input(f"{prompt} [{allowed_str}]: ").strip()

        if value in allowed:
            return value

        print(f"Invalid input. Please choose one of: {allowed_str}")


def ask_text(prompt, default=""):
    value = input(f"{prompt} (Enter to keep current): ").strip()
    if value == "":
        return default
    return value


def annotate_rows(out: pd.DataFrame):
    print("\nStart manual annotation")
    print("-" * 80)

    for idx, row in out.iterrows():
        already_done = all(
            str(row[col]).strip() not in ["", "nan"]
            for col in [
                "narration_type",
                "at_context_present",
                "friction_type",
                "severity",
                "sentiment",
                "confidence",
            ]
        )

        print("\n" + "=" * 80)
        print(f"Item {idx + 1} / {len(out)}")
        print(f"window_id : {row['window_id']}")
        print(f"project   : {row['project']}")
        print(f"video_id  : {row['video_id']}")
        print(f"task_title: {row['task_title']}")
        print("-" * 80)
        print("text:")
        print(row["text"])
        print("-" * 80)

        if already_done:
            skip = input("This row already has labels. Press Enter to review/edit, or type 'skip': ").strip().lower()
            if skip == "skip":
                continue

        current_narration = "" if pd.isna(row["narration_type"]) else str(row["narration_type"])
        current_at = "" if pd.isna(row["at_context_present"]) else str(row["at_context_present"])
        current_friction = "" if pd.isna(row["friction_type"]) else str(row["friction_type"])
        current_severity = "" if pd.isna(row["severity"]) else str(row["severity"])
        current_sentiment = "" if pd.isna(row["sentiment"]) else str(row["sentiment"])
        current_confidence = "" if pd.isna(row["confidence"]) else str(row["confidence"])
        current_notes = "" if pd.isna(row["notes"]) else str(row["notes"])

        out.at[idx, "narration_type"] = ask_choice("narration_type", NARRATION_TYPES, current_narration if current_narration else None)
        out.at[idx, "at_context_present"] = ask_choice("at_context_present", AT_CONTEXT_VALUES, current_at if current_at else None)
        out.at[idx, "friction_type"] = ask_choice("friction_type", FRICTION_TYPES, current_friction if current_friction else None)
        out.at[idx, "severity"] = ask_choice("severity", SEVERITY_VALUES, current_severity if current_severity else None)
        out.at[idx, "sentiment"] = ask_choice("sentiment", SENTIMENT_VALUES, current_sentiment if current_sentiment else None)
        out.at[idx, "confidence"] = ask_choice("confidence", CONFIDENCE_VALUES, current_confidence if current_confidence else None)
        out.at[idx, "notes"] = ask_text("notes", current_notes)
        out.at[idx, "annotator"] = "R8"

        out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        print(f"Saved progress to {OUTPUT_PATH}")

    print("\nAll rows processed.")
    print(f"Final file saved to: {OUTPUT_PATH}")


def main():
    print_header()

    # Read allowed guideline files only
    read_guidelines()

    print_guideline_summary()

    out = build_or_load_annotation_file()
    annotate_rows(out)


if __name__ == "__main__":
    main()
