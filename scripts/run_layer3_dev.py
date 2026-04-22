"""Run Step 5.2 Layer 3 dev-set classification.

Examples:
    python scripts/run_layer3_dev.py --level A --input data/processed/windows.csv --limit 3 --dry-run
    python scripts/run_layer3_dev.py --level B --input data/processed/windows.csv --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from layer3.llm_classifier import (  # noqa: E402
    VideoInput,
    WindowInput,
    batch_classify_videos,
    batch_classify_windows,
)


logger = logging.getLogger(__name__)


def _load_project_task_context(root: Path, project: str) -> tuple[str, str]:
    task_dir = root / "data" / "raw" / project
    task_files = sorted(task_dir.glob("*-tasks.csv"))
    if not task_files:
        logger.warning("No tasks CSV found for project=%s", project)
        return "Unknown task", "No task instructions provided."

    tasks = pd.read_csv(task_files[0])
    if tasks.empty:
        logger.warning("Tasks CSV is empty for project=%s path=%s", project, task_files[0])
        return "Unknown task", "No task instructions provided."

    # windows.csv currently has no task/order field, so full-dev CLI uses the
    # first project task as a stable placeholder until R1/R7 provide mapping.
    row = tasks.iloc[0]
    return str(row.get("Title", "Unknown task")), str(
        row.get("Instructions", "No task instructions provided.")
    )


def _build_window_inputs(windows: pd.DataFrame, root: Path) -> list[WindowInput]:
    context_by_project = {
        project: _load_project_task_context(root, project)
        for project in sorted(windows["project"].dropna().unique())
    }
    inputs: list[WindowInput] = []
    for row in windows.itertuples(index=False):
        task_title, task_instructions = context_by_project.get(
            row.project, ("Unknown task", "No task instructions provided.")
        )
        inputs.append(
            WindowInput(
                window_id=str(row.window_id),
                project=str(row.project),
                video_id=str(row.video_id),
                window_text=str(row.text),
                task_title=task_title,
                task_instructions=task_instructions,
            )
        )
    return inputs


def _build_video_inputs(windows: pd.DataFrame, root: Path) -> list[VideoInput]:
    context_by_project = {
        project: _load_project_task_context(root, project)
        for project in sorted(windows["project"].dropna().unique())
    }
    inputs: list[VideoInput] = []
    for video_id, block in windows.groupby("video_id", sort=True):
        first = block.iloc[0]
        task_title, _ = context_by_project.get(
            first["project"], ("Unknown task", "No task instructions provided.")
        )
        transcript = "\n\n".join(block.sort_values("start_time")["text"].fillna("").astype(str))
        inputs.append(
            VideoInput(
                video_id=str(video_id),
                project=str(first["project"]),
                task_title=task_title,
                aggregated_transcript=transcript,
            )
        )
    return inputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level", choices=["A", "B"], required=True)
    parser.add_argument("--input", required=True, help="Path to windows.csv")
    parser.add_argument("--output", default=None)
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-concurrency", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    args = parse_args()

    level = args.level.upper()
    output = args.output or str(ROOT / "outputs" / f"layer3_dev_level_{level}_results.csv")
    checkpoint = args.checkpoint or str(
        ROOT / "outputs" / f"layer3_dev_level_{level}_checkpoint.csv"
    )

    windows = pd.read_csv(args.input)
    if args.limit is not None:
        windows = windows.head(args.limit)

    if level == "A":
        inputs = _build_window_inputs(windows, ROOT)
        summary = batch_classify_windows(
            inputs,
            output_csv=output,
            checkpoint_csv=checkpoint,
            max_concurrency=args.max_concurrency or 4,
            dry_run=args.dry_run,
        )
    else:
        inputs = _build_video_inputs(windows, ROOT)
        summary = batch_classify_videos(
            inputs,
            output_csv=output,
            checkpoint_csv=checkpoint,
            max_concurrency=args.max_concurrency or 2,
            dry_run=args.dry_run,
        )

    print(summary)


if __name__ == "__main__":
    main()
