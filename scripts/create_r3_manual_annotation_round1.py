"""Create the first R3 manual annotation sample set.

This is a one-off helper script for Step 5.3. It selects representative
transcript windows from the R3 review sample and writes:

- data/annotations/r3_manual_annotations_round1.csv
- data/annotations/round1_blind_for_r8.csv

The labels follow the client F1-F7, S1-S6, and E1-E5 framework documented in
docs/friction_taxonomy.md.
"""

import csv
from pathlib import Path


INPUT_PATH = Path("data/annotations/r3_window_review_sample.csv")
OUTPUT_PATH = Path("data/annotations/r3_manual_annotations_round1.csv")
BLIND_OUTPUT_PATH = Path("data/annotations/round1_blind_for_r8.csv")
R8_OUTPUT_PATH = Path("data/annotations/r8_manual_annotations_round1.csv")

TASK_PATHS = {
    "department-of-premier-and-cabinet-wa": Path(
        "data/raw/department-of-premier-and-cabinet-wa/"
        "coercive-control-support-tasks.csv"
    ),
    "suncorp-insurance": Path(
        "data/raw/suncorp-insurance/aami-website-tasks.csv"
    ),
    "the-university-of-queensland": Path(
        "data/raw/the-university-of-queensland/"
        "postgrad-enrolment-experience-tasks.csv"
    ),
}

OUTPUT_FIELDS = [
    "window_id",
    "project",
    "video_id",
    "video_filename",
    "tester_name",
    "task_title",
    "task_instructions",
    "start_time",
    "end_time",
    "duration",
    "text",
    "narration_type",
    "at_context_present",
    "friction_type",
    "friction_label",
    "severity_id",
    "severity",
    "sentiment_id",
    "sentiment",
    "confidence",
    "primary_evidence",
    "secondary_friction_type",
    "notes",
    "annotator",
]

LABEL_FIELDS = {
    "narration_type",
    "at_context_present",
    "friction_type",
    "friction_label",
    "severity_id",
    "severity",
    "sentiment_id",
    "sentiment",
    "confidence",
    "primary_evidence",
    "secondary_friction_type",
    "notes",
    "annotator",
}

BLIND_OUTPUT_FIELDS = [
    field for field in OUTPUT_FIELDS if field not in LABEL_FIELDS
]

# Hand-picked from the 50 reviewed windows to cover the client F1-F7 framework,
# accessibility-specific evidence, and no-friction positive examples.
SELECTED_WINDOW_IDS = [
    "ramazankawish_wa_w075",  # F6: feedback form/content not found
    "gameoverdan_suncorp_w040",  # F6: online support path not found
    "Sharelinsonny_uq_w026",  # F1: formal/legal content comprehension
    "oliviamitchell22_suncorp_w007",  # F1: unclear insurance terminology
    "giuliaclemente26_uq_w050",  # F7: authenticator setup effort
    "reneerussell99_uq_w009",  # F2: uncertainty about required form field
    "ghum_wa_w029",  # F3: inaccessible PDF/content
    "marychaunguyen_suncorp_w011",  # F3: VoiceOver information load
    "giuliaclemente26_uq_w004",  # F2: low confidence in site behaviour
    "margieflint_suncorp_w007",  # F2: trust/confidence uncertainty
    "tianarosie1_wa_w015",  # F7: high cognitive/emotional effort
    "thanoptions_uq_w008",  # none: positive site impression
    "fjone7_uq_w066",  # none: accessible file upload
    "oliviamitchell22_suncorp_w017",  # none: positive support page evaluation
]

# windows.csv does not currently include a task/order field, so these links are
# manually inferred from the selected window text and then joined to tasks.csv.
TASK_ORDER_BY_WINDOW_ID = {
    "ramazankawish_wa_w075": "13",
    "gameoverdan_suncorp_w040": "7",
    "Sharelinsonny_uq_w026": "3",
    "oliviamitchell22_suncorp_w007": "3",
    "giuliaclemente26_uq_w050": "8",
    "reneerussell99_uq_w009": "3",
    "ghum_wa_w029": "6",
    "marychaunguyen_suncorp_w011": "2",
    "giuliaclemente26_uq_w004": "1",
    "margieflint_suncorp_w007": "1",
    "tianarosie1_wa_w015": "4",
    "thanoptions_uq_w008": "2",
    "fjone7_uq_w066": "6",
    "oliviamitchell22_suncorp_w017": "7",
}

ANNOTATION_BY_WINDOW_ID = {
    "ramazankawish_wa_w075": {
        "friction_type": "F6",
        "friction_label": "Content Not Found",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "negative",
        "notes": (
            "Task required finding the feedback form; tester could not locate "
            "the needed pathway."
        ),
    },
    "gameoverdan_suncorp_w040": {
        "friction_type": "F6",
        "friction_label": "Content Not Found",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "negative",
        "notes": (
            "Task required online support information; tester repeatedly "
            "searched but could not locate the appropriate online path."
        ),
    },
    "Sharelinsonny_uq_w026": {
        "friction_type": "F1",
        "friction_label": "Comprehension Friction",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "negative",
        "notes": "Formal legal language makes the content difficult to understand.",
    },
    "oliviamitchell22_suncorp_w007": {
        "friction_type": "F1",
        "friction_label": "Comprehension Friction",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "mixed",
        "notes": (
            "Unclear insurance terminology is the main issue, although the "
            "window also includes some positive evaluation."
        ),
    },
    "giuliaclemente26_uq_w050": {
        "friction_type": "F7",
        "friction_label": "Excessive Effort",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "negative",
        "notes": "Authenticator setup adds extra work and cognitive effort.",
    },
    "reneerussell99_uq_w009": {
        "friction_type": "F2",
        "friction_label": "Confidence Friction",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "mixed",
        "notes": (
            "Tester is uncertain where or when the required citizenship status "
            "field should have been completed."
        ),
    },
    "ghum_wa_w029": {
        "friction_type": "F3",
        "friction_label": "Accessibility Friction",
        "severity_id": "S3",
        "severity": "high",
        "sentiment_id": "E4",
        "sentiment": "negative",
        "notes": (
            "PDF/content is inaccessible to the tester's assistive technology, "
            "preventing access to the content."
        ),
    },
    "marychaunguyen_suncorp_w011": {
        "friction_type": "F3",
        "friction_label": "Accessibility Friction",
        "severity_id": "S3",
        "severity": "high",
        "sentiment_id": "E4",
        "sentiment": "mixed",
        "notes": (
            "VoiceOver context dominates; tester describes a high listening "
            "load despite some useful page content."
        ),
    },
    "giuliaclemente26_uq_w004": {
        "friction_type": "F2",
        "friction_label": "Confidence Friction",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "negative",
        "notes": (
            "Site behaviour asks for downloads or input before trust is "
            "established, reducing tester confidence."
        ),
    },
    "margieflint_suncorp_w007": {
        "friction_type": "F2",
        "friction_label": "Confidence Friction",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "mixed",
        "notes": (
            "Tester explicitly questions whether they trust the search or "
            "comparison result."
        ),
    },
    "tianarosie1_wa_w015": {
        "friction_type": "F7",
        "friction_label": "Excessive Effort",
        "severity_id": "S5",
        "severity": "medium",
        "sentiment_id": "E4",
        "sentiment": "mixed",
        "notes": (
            "Sensitive examples are useful but cognitively and emotionally "
            "heavy to read."
        ),
    },
    "thanoptions_uq_w008": {
        "friction_type": "none",
        "friction_label": "No observed friction",
        "severity_id": "none",
        "severity": "none",
        "sentiment_id": "E2",
        "sentiment": "positive",
        "notes": "Positive evaluation with no observed task impediment.",
    },
    "fjone7_uq_w066": {
        "friction_type": "none",
        "friction_label": "No observed friction",
        "severity_id": "none",
        "severity": "none",
        "sentiment_id": "E2",
        "sentiment": "positive",
        "notes": "Accessible standard file upload with no observed task impediment.",
    },
    "oliviamitchell22_suncorp_w017": {
        "friction_type": "none",
        "friction_label": "No observed friction",
        "severity_id": "none",
        "severity": "none",
        "sentiment_id": "E1",
        "sentiment": "positive",
        "notes": "Positive support page evaluation with no observed task impediment.",
    },
}


def detect_at_context(row):
    """Infer whether assistive technology/accessibility context is present."""
    text = " ".join(
        [
            row.get("text", ""),
            row.get("initial_observation", ""),
            row.get("notes", ""),
        ]
    ).lower()
    keywords = [
        "accessib",
        "assistive",
        "screen reader",
        "voiceover",
        "voice over",
        "heading",
        "headings",
        "focus",
        "keyboard",
        "zoom",
        "pdf",
        "ocr",
    ]
    return "yes" if any(keyword in text for keyword in keywords) else "no"


def load_tasks():
    """Load tasks by project and task order."""
    tasks = {}
    for project, path in TASK_PATHS.items():
        with path.open(newline="", encoding="utf-8-sig") as task_file:
            tasks[project] = {
                task["Order"]: task for task in csv.DictReader(task_file)
            }
    return tasks


def get_task_context(row, tasks):
    """Return the task title and instructions for a selected window."""
    window_id = row.get("window_id", "")
    project = row.get("project", "")
    task_order = TASK_ORDER_BY_WINDOW_ID.get(window_id)
    if task_order is None:
        raise ValueError(f"No task order mapping for window_id: {window_id}")

    task = tasks.get(project, {}).get(task_order)
    if task is None:
        raise ValueError(
            f"No task found for project={project!r}, order={task_order!r}"
        )

    return task.get("Title", ""), task.get("Instructions", "")


def convert_row(row, tasks):
    """Convert a reviewed sample row to the manual annotation schema."""
    window_id = row.get("window_id", "")
    task_title, task_instructions = get_task_context(row, tasks)
    annotation = ANNOTATION_BY_WINDOW_ID[window_id]
    return {
        "window_id": window_id,
        "project": row.get("project", ""),
        "video_id": row.get("video_id", ""),
        "video_filename": row.get("video_filename", ""),
        "tester_name": row.get("tester_name", ""),
        "task_title": task_title,
        "task_instructions": task_instructions,
        "start_time": row.get("start_time", ""),
        "end_time": row.get("end_time", ""),
        "duration": row.get("duration", ""),
        "text": row.get("text", ""),
        "narration_type": row.get("possible_narration_type", ""),
        "at_context_present": detect_at_context(row),
        "friction_type": annotation["friction_type"],
        "friction_label": annotation["friction_label"],
        "severity_id": annotation["severity_id"],
        "severity": annotation["severity"],
        "sentiment_id": annotation["sentiment_id"],
        "sentiment": annotation["sentiment"],
        "confidence": "medium",
        "primary_evidence": row.get("primary_evidence", ""),
        "secondary_friction_type": "",
        "notes": annotation["notes"],
        "annotator": "R3",
    }


def main():
    tasks = load_tasks()

    with INPUT_PATH.open(newline="", encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))

    rows_by_id = {row["window_id"]: row for row in rows}
    missing = [
        window_id
        for window_id in SELECTED_WINDOW_IDS
        if window_id not in rows_by_id
    ]
    if missing:
        raise ValueError(f"Selected window IDs not found: {missing}")

    selected_rows = [
        convert_row(rows_by_id[window_id], tasks)
        for window_id in SELECTED_WINDOW_IDS
    ]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(selected_rows)

    blind_rows = [
        {field: row[field] for field in BLIND_OUTPUT_FIELDS}
        for row in selected_rows
    ]
    with BLIND_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=BLIND_OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(blind_rows)

    r8_rows = []
    for row in selected_rows:
        blind_annotation_row = dict(row)
        for field in LABEL_FIELDS:
            blind_annotation_row[field] = ""
        blind_annotation_row["annotator"] = "R8"
        r8_rows.append(blind_annotation_row)

    with R8_OUTPUT_PATH.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(r8_rows)

    print(f"Wrote {len(selected_rows)} rows to {OUTPUT_PATH}")
    print(f"Wrote {len(blind_rows)} rows to {BLIND_OUTPUT_PATH}")
    print(f"Wrote {len(r8_rows)} blank rows to {R8_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
