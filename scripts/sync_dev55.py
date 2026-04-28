"""Sync the official dev55 report subset from the main reports directory.

The dev55 directory is a physical whitelist: it should contain byte-identical
copies of the current report JSON files listed in dev55_official_list.csv.
"""

from __future__ import annotations

import argparse
import csv
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "data" / "processed" / "reports"
DEFAULT_LIST = REPORTS_DIR / "dev55_official_list.csv"
DEFAULT_DEV55_DIR = REPORTS_DIR / "dev55"


def read_video_ids(list_path: Path) -> list[str]:
    with list_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if "video_id" not in (reader.fieldnames or []):
            raise ValueError(f"{list_path} must contain a video_id column")
        return [row["video_id"].strip() for row in reader if row.get("video_id")]


def expected_paths(video_ids: list[str], reports_dir: Path) -> dict[str, Path]:
    return {video_id: reports_dir / f"{video_id}.json" for video_id in video_ids}


def check_subset(video_ids: list[str], reports_dir: Path, dev55_dir: Path) -> list[str]:
    errors: list[str] = []
    for video_id, source_path in expected_paths(video_ids, reports_dir).items():
        target_path = dev55_dir / source_path.name
        if not source_path.exists():
            errors.append(f"missing source: {source_path}")
        elif not target_path.exists():
            errors.append(f"missing dev55 copy: {target_path}")
        elif not filecmp.cmp(source_path, target_path, shallow=False):
            errors.append(f"content drift: {target_path}")

    expected_names = {f"{video_id}.json" for video_id in video_ids}
    if dev55_dir.exists():
        for extra_path in dev55_dir.glob("*.json"):
            if extra_path.name not in expected_names:
                errors.append(f"unexpected dev55 file: {extra_path}")

    return errors


def sync_subset(video_ids: list[str], reports_dir: Path, dev55_dir: Path) -> None:
    sources = expected_paths(video_ids, reports_dir)
    missing = [str(path) for path in sources.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing source report(s):\n" + "\n".join(missing))

    dev55_dir.mkdir(parents=True, exist_ok=True)
    expected_names = {path.name for path in sources.values()}

    for existing_path in dev55_dir.glob("*.json"):
        if existing_path.name not in expected_names:
            existing_path.unlink()

    for source_path in sources.values():
        shutil.copy2(source_path, dev55_dir / source_path.name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync data/processed/reports/dev55 from dev55_official_list.csv."
    )
    parser.add_argument("--check", action="store_true", help="check for drift without copying")
    parser.add_argument("--list", type=Path, default=DEFAULT_LIST, help="path to dev55 CSV")
    parser.add_argument("--reports-dir", type=Path, default=REPORTS_DIR, help="main reports dir")
    parser.add_argument("--dev55-dir", type=Path, default=DEFAULT_DEV55_DIR, help="dev55 output dir")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    video_ids = read_video_ids(args.list)

    if args.check:
        errors = check_subset(video_ids, args.reports_dir, args.dev55_dir)
        if errors:
            print("dev55 drift check failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print(f"dev55 drift check passed: {len(video_ids)}/{len(video_ids)} files match.")
        return 0

    sync_subset(video_ids, args.reports_dir, args.dev55_dir)
    errors = check_subset(video_ids, args.reports_dir, args.dev55_dir)
    if errors:
        print("dev55 sync completed but verification failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"dev55 sync complete: {len(video_ids)} files copied and verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
