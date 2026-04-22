"""Migrate R3 round-1 annotations to the Round 5 canonical schema.

This script keeps `data/annotations/r3_manual_annotations_round1.csv` as the
historical input and writes:

- `data/annotations/r3_manual_annotations_round1_canonical.csv`
- `data/annotations/window_semantic_labels_template_canonical.csv`

The canonical field order matches `r8_manual_annotations_round1.csv`.
"""

import csv
from pathlib import Path


INPUT_PATH = Path("data/annotations/r3_manual_annotations_round1.csv")
OUTPUT_PATH = Path("data/annotations/r3_manual_annotations_round1_canonical.csv")
TEMPLATE_PATH = Path("data/annotations/window_semantic_labels_template_canonical.csv")

CANONICAL_FIELDS = [
    "window_id",
    "project",
    "video_id",
    "task_title",
    "text",
    "task_instructions",
    "annotated",
    "finding",
    "observed_signal",
    "stated_signal",
    "signal_alignment",
    "friction_type",
    "severity_s",
    "sentiment_e",
    "calibrator_score_l",
    "rationale",
    "structural_amplification_note",
    "narration_quality",
    "recording_quality",
    "coaching_evidence",
    "confidence",
    "notes",
    "annotator",
]

BASIC_FIELD_MAP = {
    "window_id": "window_id",
    "project": "project",
    "video_id": "video_id",
    "task_title": "task_title",
    "text": "text",
    "task_instructions": "task_instructions",
    "confidence": "confidence",
    "notes": "notes",
}

CURATED_CANONICAL_BY_WINDOW_ID = {
    "ramazankawish_wa_w075": {
        "finding": (
            "Participant could not locate the feedback page needed to submit "
            "website feedback."
        ),
        "observed_signal": (
            "Participant checked complaint and feedback text, scanned headings, "
            "and tried unrelated domestic violence and Court Safe areas before "
            "concluding the feedback option was not present."
        ),
        "stated_signal": "I'm struggling to find the feedback page, to be honest.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L3",
        "rationale": (
            "The task required locating the feedback form. Observed navigation "
            "across unrelated sections and the explicit statement of struggle "
            "both support F6 Content Not Found; the issue caused significant "
            "search effort but was not a full project blocker."
        ),
        "structural_amplification_note": "",
        "narration_quality": "adequate",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "gameoverdan_suncorp_w040": {
        "finding": (
            "Participant could not locate the online emergency support pathway "
            "from the homepage."
        ),
        "observed_signal": (
            "Participant searched the homepage, Resources, Help Center, Cancel "
            "Policy, Contact Us, Ask a Question, and then returned to Claim "
            "Online."
        ),
        "stated_signal": "No, we're doing it online. Doing it online. Claim online.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L2",
        "rationale": (
            "The task required finding online information about AAMI support "
            "during an extreme weather event. The participant followed a "
            "non-optimal path through several irrelevant options, but continued "
            "the task without abandonment."
        ),
        "structural_amplification_note": "",
        "narration_quality": "adequate",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "Sharelinsonny_uq_w026": {
        "finding": (
            "Participant found the terms and cookie language too formal and "
            "legalistic to read in detail."
        ),
        "observed_signal": (
            "Participant scrolled through a dense terms/cookie section and did "
            "not engage with the content in detail."
        ),
        "stated_signal": (
            "Written in formal legal language, it's not very user-friendly, "
            "and I wouldn't realistically read all of it in detail."
        ),
        "signal_alignment": "aligned",
        "calibrator_score_l": "L2",
        "rationale": (
            "The participant explicitly identified formal legal language as "
            "not user-friendly and disengaged from detailed reading. This is "
            "F1 Comprehension Friction with moderate impact because the account "
            "creation task was not blocked."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "oliviamitchell22_suncorp_w007": {
        "finding": (
            "Participant did not understand the insurance term third party "
            "while scanning service options."
        ),
        "observed_signal": (
            "Participant paused on third party and motor insurance options, "
            "asked what the term meant, then moved on to home and contents "
            "insurance."
        ),
        "stated_signal": "What's third party? I have no clue.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L1",
        "rationale": (
            "The participant explicitly did not understand an insurance term, "
            "so the dominant issue is F1 Comprehension Friction. The friction "
            "was minor because the participant quickly moved past it and found "
            "the target product category."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "giuliaclemente26_uq_w050": {
        "finding": (
            "Multi-factor authenticator setup created extra installation and "
            "task-recovery effort."
        ),
        "observed_signal": (
            "Participant had to consider installing Google Authenticator, scan "
            "a QR code, enter a code, and work out how to maintain task state."
        ),
        "stated_signal": "I need to install something which is already a pain.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L3",
        "rationale": (
            "The participant described the authenticator setup as painful and "
            "questioned how someone would complete it while remembering where "
            "they were. This is F7 Excessive Effort with significant friction "
            "because the task became substantially more demanding."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "reneerussell99_uq_w009": {
        "finding": (
            "The citizenship status field appeared in an unexpected location, "
            "causing a registration retry."
        ),
        "observed_signal": (
            "Participant pressed Register, received a required citizenship "
            "status prompt, looked back through the form, and found the field "
            "at the top."
        ),
        "stated_signal": "I didn't see that. I was expecting that to be...",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L2",
        "rationale": (
            "The participant understood the form but was unsure where the "
            "citizenship status question belonged. The failed register attempt "
            "and retry show F2 Confidence Friction with moderate, recoverable "
            "impact."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "ghum_wa_w029": {
        "finding": "PDF content was inaccessible to the participant's screen reader.",
        "observed_signal": (
            "Participant opened a PDF and the screen reader repeatedly announced "
            "empty groups and page containers instead of meaningful content."
        ),
        "stated_signal": "I've got no access to the content in here at all.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L4",
        "rationale": (
            "The participant could not access the PDF content through assistive "
            "technology. This is F3 Accessibility Friction with severe impact "
            "because the relevant resource existed but was not usable through "
            "the participant's access method."
        ),
        "structural_amplification_note": (
            "Screen-reader/PDF accessibility barriers structurally amplify "
            "impact for Blind or AT users because visual content may exist but "
            "not be exposed to assistive technology."
        ),
        "narration_quality": "adequate",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "marychaunguyen_suncorp_w011": {
        "finding": (
            "Homepage information density created a high listening load for a "
            "VoiceOver user."
        ),
        "observed_signal": (
            "Participant described many homepage items, drop-downs, and heading "
            "navigation options that had to be listened through to reach the "
            "target content."
        ),
        "stated_signal": (
            "For someone who's using a voiceover, there's a lot to listen to."
        ),
        "signal_alignment": "aligned",
        "calibrator_score_l": "L3",
        "rationale": (
            "The participant explicitly tied the navigation burden to VoiceOver "
            "use, and the observed homepage density supports that statement. "
            "This is F3 Accessibility Friction with significant effort, though "
            "the participant still identifies possible ways to navigate."
        ),
        "structural_amplification_note": (
            "VoiceOver users must process page structure sequentially, so dense "
            "homepage content can create more friction than it would for visual "
            "skimming."
        ),
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "giuliaclemente26_uq_w004": {
        "finding": (
            "Early download or input prompts reduced confidence before the "
            "participant could assess the site."
        ),
        "observed_signal": (
            "Participant encountered prompts to download or input information "
            "before reviewing the landing page and formed a low-trust "
            "impression."
        ),
        "stated_signal": (
            "They try and have you download things or input things that you "
            "haven't even had the time to look at the landing page."
        ),
        "signal_alignment": "aligned",
        "calibrator_score_l": "L2",
        "rationale": (
            "The participant understood the page but did not trust being asked "
            "for downloads or input so early. This is F2 Confidence Friction "
            "with moderate impact because it harmed trust but did not yet block "
            "task progress."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "margieflint_suncorp_w007": {
        "finding": (
            "Participant questioned whether insurance search and comparison "
            "results were trustworthy."
        ),
        "observed_signal": (
            "Participant compared Google results, noted missing expected brands, "
            "and observed repeated promoted results while evaluating whether to "
            "trust the options."
        ),
        "stated_signal": "I don't know if I trust them.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L2",
        "rationale": (
            "The participant could continue searching, but explicitly questioned "
            "trust in the results and providers. This is F2 Confidence Friction "
            "with moderate impact on decision confidence."
        ),
        "structural_amplification_note": "",
        "narration_quality": "adequate",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "tianarosie1_wa_w015": {
        "finding": (
            "Sensitive coercive-control examples created high cognitive and "
            "emotional reading effort."
        ),
        "observed_signal": (
            "Participant became quiet while reading the examples, then explained "
            "that the content confirmed the scenario but was intense to process."
        ),
        "stated_signal": "Very full-on to read all of the examples.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L2",
        "rationale": (
            "The content was informative and helped answer the task, but the "
            "participant described a high processing load. This is F7 Excessive "
            "Effort with moderate impact because the task continued."
        ),
        "structural_amplification_note": "",
        "narration_quality": "adequate",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "thanoptions_uq_w008": {
        "finding": "",
        "observed_signal": (
            "Participant reviewed the UQ site, located the search function and "
            "campus information quickly, and gave positive overall feedback."
        ),
        "stated_signal": (
            "The website looks nice. I like it. It's nice and simple, it's clear, "
            "not too cluttered."
        ),
        "signal_alignment": "aligned",
        "calibrator_score_l": "L1",
        "rationale": (
            "The window shows positive task progress and no observed impediment. "
            "This should remain a no-friction example for agreement evaluation."
        ),
        "structural_amplification_note": "",
        "narration_quality": "adequate",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "fjone7_uq_w066": {
        "finding": "",
        "observed_signal": (
            "Participant used the standard file upload dialogue with keyboard "
            "navigation and type-to-search, then continued through the form "
            "without difficulty."
        ),
        "stated_signal": "Standard file upload dialogue fairly accessible for me.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L1",
        "rationale": (
            "The participant described the upload control as accessible and "
            "completed the interaction without observed friction. This should "
            "remain a no-friction example."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
    "oliviamitchell22_suncorp_w017": {
        "finding": "",
        "observed_signal": (
            "Participant reviewed weather event support, claims process, "
            "emergency accommodation, and FAQ content successfully."
        ),
        "stated_signal": "This seems like an all-encompassing page, which is great.",
        "signal_alignment": "aligned",
        "calibrator_score_l": "L1",
        "rationale": (
            "The participant found the support page comprehensive and useful, "
            "with no observed task impediment. This should remain a positive "
            "no-friction example."
        ),
        "structural_amplification_note": "",
        "narration_quality": "rich",
        "recording_quality": "good",
        "coaching_evidence": "none",
    },
}


def read_rows(path=INPUT_PATH):
    """Read CSV rows using UTF-8 with BOM tolerance."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def normalize_code(value):
    """Return the leading taxonomy code from a legacy value."""
    value = (value or "").strip()
    if not value:
        return ""
    return value.split()[0]


def seed_rationale(row):
    """Build a fallback rationale from legacy evidence fields."""
    parts = []
    evidence = (row.get("primary_evidence") or "").strip()
    notes = (row.get("notes") or "").strip()
    if evidence:
        parts.append(f"Legacy evidence: {evidence}")
    if notes:
        parts.append(f"Legacy note: {notes}")
    return " ".join(parts)


def migrate_row(row):
    """Convert one legacy R3 row to the canonical output row."""
    window_id = row.get("window_id", "")
    if window_id not in CURATED_CANONICAL_BY_WINDOW_ID:
        raise ValueError(f"Missing curated canonical fields for {window_id}")

    migrated = {field: "" for field in CANONICAL_FIELDS}
    for canonical_field, old_field in BASIC_FIELD_MAP.items():
        migrated[canonical_field] = row.get(old_field, "")

    migrated.update(
        {
            "annotated": "yes",
            "friction_type": normalize_code(row.get("friction_type")),
            "severity_s": normalize_code(row.get("severity_id")),
            "sentiment_e": normalize_code(row.get("sentiment_id")),
            "rationale": seed_rationale(row),
            "annotator": "R3",
        }
    )
    migrated.update(CURATED_CANONICAL_BY_WINDOW_ID[window_id])
    return {field: migrated[field] for field in CANONICAL_FIELDS}


def migrate_rows(rows):
    """Convert all legacy R3 rows to canonical rows."""
    return [migrate_row(row) for row in rows]


def write_csv(path, fieldnames, rows):
    """Write rows with a stable header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_outputs(rows, output_path=OUTPUT_PATH, template_path=TEMPLATE_PATH):
    """Write the migrated canonical CSV and a header-only canonical template."""
    canonical_rows = migrate_rows(rows)
    write_csv(output_path, CANONICAL_FIELDS, canonical_rows)
    write_csv(template_path, CANONICAL_FIELDS, [])


def main():
    rows = read_rows(INPUT_PATH)
    write_outputs(rows, OUTPUT_PATH, TEMPLATE_PATH)
    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")
    print(f"Wrote canonical template to {TEMPLATE_PATH}")


if __name__ == "__main__":
    main()
