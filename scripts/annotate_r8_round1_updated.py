from pathlib import Path
import pandas as pd

# =========================
# Paths
# =========================
TAXONOMY_PATH = Path("docs/friction_taxonomy.md")
PROMPT_PATH = Path("docs/prompt_design.md")
INPUT_PATH = Path("data/annotations/round1_blind_for_r8.csv")
OUTPUT_PATH = Path("data/annotations/r8_manual_annotations_round1.csv")

# Forbidden files (do not read during blind annotation)
FORBIDDEN_PATHS = [
    "data/annotations/r3_manual_annotations_round1.csv",
    "docs/cluster_interpretation.md",
    "docs/case_studies.md",
]

# =========================
# Allowed label values
# =========================
SIGNAL_ALIGNMENT_VALUES = ["aligned", "conflicted", "stated_missing"]

# FIX 1: Added "none" and "unclear" to match prompt_design.md Output JSON Schema
FRICTION_TYPES = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "none", "unclear"]

# FIX 1: Added "none" and "unclear" to match prompt_design.md severity_id definition
SEVERITY_S_VALUES = ["S1", "S2", "S3", "S4", "S5", "S6", "none", "unclear"]

# FIX 2: Removed "null" string — true null is represented by blank input (allow_blank=True)
SENTIMENT_E_VALUES = ["E1", "E2", "E3", "E4", "E5"]

CALIBRATOR_SCORE_L_VALUES = ["L1", "L2", "L3", "L4", "L5"]

NARRATION_QUALITY_VALUES = ["none", "sparse", "adequate", "rich"]
RECORDING_QUALITY_VALUES = ["poor", "acceptable", "good"]
COACHING_EVIDENCE_VALUES = ["none", "explicit"]

CONFIDENCE_VALUES = ["low", "medium", "high"]


def print_header():
    print("=" * 90)
    print("R8 Manual Annotation Tool - Round 1 (Round 5 Canonical Schema)")
    print("=" * 90)
    print("This tool ONLY uses:")
    print(f"  - {TAXONOMY_PATH}")
    print(f"  - {PROMPT_PATH}")
    print(f"  - {INPUT_PATH}")
    print()
    print("It will NOT read the following files during blind annotation:")
    for p in FORBIDDEN_PATHS:
        print(f"  - {p}")
    print("=" * 90)
    print()


def read_guidelines():
    # Blind-safe read: only taxonomy + prompt design + blind input
    taxonomy_text = TAXONOMY_PATH.read_text(encoding="utf-8")
    prompt_text = PROMPT_PATH.read_text(encoding="utf-8")
    # FIX 4: Print guidelines so R8 can read full definitions at startup
    print("\n" + "=" * 90)
    print("FRICTION TAXONOMY (docs/friction_taxonomy.md)")
    print("=" * 90)
    print(taxonomy_text)
    print("\n" + "=" * 90)
    print("PROMPT DESIGN (docs/prompt_design.md)")
    print("=" * 90)
    print(prompt_text)
    return taxonomy_text, prompt_text


def print_guideline_summary():
    print("\nRound 5 canonical fields")
    print("-" * 90)
    print("5.1-A finding-level")
    print("  finding")
    print("  observed_signal")
    print("  stated_signal")
    print("  signal_alignment = aligned / conflicted / stated_missing")
    print("  friction_type     = F1 / F2 / F3 / F4 / F5 / F6 / F7 / none / unclear")
    print("  severity_s        = S1 / S2 / S3 / S4 / S5 / S6 / none / unclear")
    print("  sentiment_e       = E1 / E2 / E3 / E4 / E5 / (blank = null)")
    print("  calibrator_score_l= L1 / L2 / L3 / L4 / L5")
    print("  rationale")
    print("  structural_amplification_note")
    print()
    print("5.1-B video-level")
    print("  narration_quality = none / sparse / adequate / rich")
    print("  recording_quality = poor / acceptable / good")
    print("  coaching_evidence = none / explicit")
    print()
    print("Other")
    print("  confidence        = low / medium / high")
    print("  notes             = free text")
    print("-" * 90)
    print("Important discipline:")
    print("  - If there is no verbal statement, use stated_signal = blank and")
    print("    signal_alignment = stated_missing")
    print("  - E3 means neutral expression was present; blank/null means NO emotion")
    print("    evidence at all (only valid when stated_signal is also blank)")
    print("  - Use friction_type = none for windows with no observed impediment")
    print("  - Use friction_type = unclear when transcript is too ambiguous")
    print("  - Video-level fields are session-level. For the same video_id,")
    print("    keep narration/recording/coaching labels consistent.")
    print("-" * 90)
    print()


def build_or_load_annotation_file():
    df = pd.read_csv(INPUT_PATH)

    base_cols = ["window_id", "project", "video_id", "task_title", "text"]
    optional_cols = ["task_instructions"]
    missing = [c for c in base_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in input file: {missing}")

    keep_cols = base_cols + [c for c in optional_cols if c in df.columns]

    if OUTPUT_PATH.exists():
        out = pd.read_csv(OUTPUT_PATH)
        print(f"Loaded existing annotation file: {OUTPUT_PATH}")
    else:
        out = df[keep_cols].copy()
        # FIX 3: Added "annotated" column to explicitly track completion,
        # so that legitimately empty "finding" (no-friction windows) are not
        # mistaken for unannotated rows.
        # FIX 5: Force all annotation columns to object dtype to prevent
        # pandas LossySetitemError when writing long strings into empty columns.
        annotation_cols = [
            "annotated", "finding", "observed_signal", "stated_signal",
            "signal_alignment", "friction_type", "severity_s", "sentiment_e",
            "calibrator_score_l", "rationale", "structural_amplification_note",
            "narration_quality", "recording_quality", "coaching_evidence",
            "confidence", "notes", "annotator",
        ]
        for col in annotation_cols:
            out[col] = pd.array([""] * len(out), dtype=object)
        out["annotator"] = "R8"
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        print(f"Created new annotation file: {OUTPUT_PATH}")

    return out


def ask_choice(prompt, allowed, default=None, allow_blank=False):
    allowed_str = ", ".join(allowed)
    while True:
        if default is not None and default != "":
            value = input(f"{prompt} [{allowed_str}] (Enter to keep '{default}'): ").strip()
            if value == "":
                return default
        else:
            blank_hint = "Enter = null/blank" if allow_blank else "required"
            value = input(f"{prompt} [{allowed_str}] ({blank_hint}): ").strip()
            if value == "" and allow_blank:
                return ""

        if value in allowed:
            return value

        print(f"Invalid input. Please choose one of: {allowed_str}")


def ask_text(prompt, default="", allow_blank=True):
    value = input(f"{prompt} (Enter to keep current): ").strip()
    if value == "":
        return default if default != "" else ("" if allow_blank else default)
    return value


def autofill_video_level_fields(out: pd.DataFrame, idx: int):
    """
    For the same video_id, prefill video-level fields from the first completed row.
    """
    video_id = out.at[idx, "video_id"]
    same_video = out[out["video_id"] == video_id]

    for col in ["narration_quality", "recording_quality", "coaching_evidence"]:
        existing = same_video[col].dropna().astype(str)
        existing = [v for v in existing if v.strip() not in ["", "nan"]]
        if existing:
            out.at[idx, col] = existing[0]


def annotate_rows(out: pd.DataFrame):
    print("\nStart manual annotation")
    print("-" * 90)

    for idx, row in out.iterrows():
        autofill_video_level_fields(out, idx)
        row = out.loc[idx]

        # FIX 3: Use the explicit "annotated" flag instead of checking "finding",
        # because a legitimately no-friction window has finding = "" which is valid.
        already_done = str(row.get("annotated", "")).strip() == "yes"

        print("\n" + "=" * 90)
        print(f"Item {idx + 1} / {len(out)}")
        print(f"window_id : {row['window_id']}")
        print(f"project   : {row['project']}")
        print(f"video_id  : {row['video_id']}")
        print(f"task_title: {row['task_title']}")
        if "task_instructions" in out.columns:
            print("task_instructions:")
            print(row.get("task_instructions", ""))
        print("-" * 90)
        print("text:")
        print(row["text"])
        print("-" * 90)

        if already_done:
            skip = input("This row already has labels. Press Enter to review/edit, or type 'skip': ").strip().lower()
            if skip == "skip":
                continue

        current = {col: "" if pd.isna(row[col]) else str(row[col]) for col in out.columns}

        updates = {}
        updates["finding"] = ask_text(
            "finding (leave blank if window has no friction)",
            current.get("finding", ""),
        )
        updates["observed_signal"] = ask_text("observed_signal", current.get("observed_signal", ""))
        updates["stated_signal"] = ask_text(
            "stated_signal (leave blank if none spoken)",
            current.get("stated_signal", ""),
        )
        updates["signal_alignment"] = ask_choice(
            "signal_alignment",
            SIGNAL_ALIGNMENT_VALUES,
            current.get("signal_alignment", "") or None,
        )
        updates["friction_type"] = ask_choice(
            "friction_type",
            FRICTION_TYPES,
            current.get("friction_type", "") or None,
        )
        updates["severity_s"] = ask_choice(
            "severity_s",
            SEVERITY_S_VALUES,
            current.get("severity_s", "") or None,
        )
        # FIX 2: allow_blank=True so R8 can press Enter to record true null
        # (only valid when stated_signal is also blank / stated_missing)
        updates["sentiment_e"] = ask_choice(
            "sentiment_e (Enter = null, only if no verbal expression at all)",
            SENTIMENT_E_VALUES,
            current.get("sentiment_e", "") or None,
            allow_blank=True,
        )
        updates["calibrator_score_l"] = ask_choice(
            "calibrator_score_l",
            CALIBRATOR_SCORE_L_VALUES,
            current.get("calibrator_score_l", "") or None,
        )
        updates["rationale"] = ask_text("rationale", current.get("rationale", ""))
        updates["structural_amplification_note"] = ask_text(
            "structural_amplification_note (blank if not applicable)",
            current.get("structural_amplification_note", ""),
        )

        # 5.1-B video-level fields
        updates["narration_quality"] = ask_choice(
            "narration_quality",
            NARRATION_QUALITY_VALUES,
            current.get("narration_quality", "") or None,
        )
        updates["recording_quality"] = ask_choice(
            "recording_quality",
            RECORDING_QUALITY_VALUES,
            current.get("recording_quality", "") or None,
        )
        updates["coaching_evidence"] = ask_choice(
            "coaching_evidence",
            COACHING_EVIDENCE_VALUES,
            current.get("coaching_evidence", "") or None,
        )
        updates["confidence"] = ask_choice(
            "confidence",
            CONFIDENCE_VALUES,
            current.get("confidence", "") or None,
        )
        updates["notes"] = ask_text("notes", current.get("notes", ""))
        updates["annotator"] = "R8"
        # FIX 3: Mark row as explicitly annotated so blank "finding" is not
        # confused with an unannotated row on next load.
        updates["annotated"] = "yes"

        # FIX 5: write via loc with explicit object cast to avoid LossySetitemError
        for col, val in updates.items():
            out[col] = out[col].astype(object)
            out.loc[idx, col] = val

        out.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        print(f"Saved progress to {OUTPUT_PATH}")

    print("\nAll rows processed.")
    print(f"Final file saved to: {OUTPUT_PATH}")


def main():
    print_header()
    read_guidelines()  # FIX 4: now prints full taxonomy + prompt design for R8
    print_guideline_summary()
    out = build_or_load_annotation_file()
    annotate_rows(out)


if __name__ == "__main__":
    main()
