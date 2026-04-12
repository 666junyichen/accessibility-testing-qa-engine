import csv
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

TARGET_DURATION = 60
MIN_DURATION = 30
MAX_DURATION = 90

PROJECT_ABBR = {
    "department-of-premier-and-cabinet-wa": "wa",
    "suncorp-insurance": "suncorp",
    "the-university-of-queensland": "uq",
}


def _make_video_id(tester_name, project):
    return f"{tester_name}_{PROJECT_ABBR.get(project, project)}"


def _build_items_index(items):
    index = {}
    for item in items:
        key = (item["project"], item["video_filename"], item["tester_name"], item["item_id"])
        index[key] = item["type"]
    return index


def _count_words(segment_ids, segments_by_id, items_index, project, video_filename, tester_name):
    count = 0
    for segment_id in segment_ids:
        segment = segments_by_id.get(segment_id)
        if not segment or not segment["item_ids"]:
            continue
        for item_id in segment["item_ids"].split(","):
            item_id = item_id.strip()
            if not item_id:
                continue
            key = (project, video_filename, tester_name, item_id)
            if items_index.get(key) == "pronunciation":
                count += 1
    return count


def _make_window(start, end, text_parts, segment_ids, video_id, index):
    duration = end - start
    if duration > MAX_DURATION:
        logger.warning(
            "Window %s_w%03d duration %.1fs exceeds MAX_DURATION %ds",
            video_id,
            index,
            duration,
            MAX_DURATION,
        )
    return {
        "start_time": start,
        "end_time": end,
        "duration": round(duration, 3),
        "text": " ".join(text_parts),
        "segment_ids": ",".join(segment_ids),
    }


def _split_video_windows(video_segments, video_id):
    sorted_segments = sorted(video_segments, key=lambda segment: float(segment["start_time"]))

    windows = []
    current_start = None
    current_end = None
    current_text_parts = []
    current_segment_ids = []

    for segment in sorted_segments:
        segment_start = float(segment["start_time"])
        segment_end = float(segment["end_time"])

        if current_start is None:
            current_start = segment_start

        current_end = segment_end
        current_text_parts.append(segment["transcript"] or "")
        current_segment_ids.append(segment["segment_id"])

        if current_end - current_start >= TARGET_DURATION:
            windows.append(
                _make_window(
                    current_start,
                    current_end,
                    current_text_parts,
                    current_segment_ids,
                    video_id,
                    len(windows),
                )
            )
            current_start = None
            current_end = None
            current_text_parts = []
            current_segment_ids = []

    if current_start is not None:
        tail_duration = current_end - current_start
        if tail_duration < MIN_DURATION and windows:
            last_window = windows[-1]
            last_window["end_time"] = current_end
            last_window["duration"] = round(current_end - last_window["start_time"], 3)
            last_window["text"] = last_window["text"] + " " + " ".join(current_text_parts)
            last_window["segment_ids"] = last_window["segment_ids"] + "," + ",".join(current_segment_ids)
            if last_window["duration"] > MAX_DURATION:
                logger.warning(
                    "Window %s_w%03d duration %.1fs exceeds MAX_DURATION %ds after tail merge",
                    video_id,
                    len(windows) - 1,
                    last_window["duration"],
                    MAX_DURATION,
                )
        else:
            windows.append(
                _make_window(
                    current_start,
                    current_end,
                    current_text_parts,
                    current_segment_ids,
                    video_id,
                    len(windows),
                )
            )

    for index, window in enumerate(windows):
        window["window_id"] = f"{video_id}_w{index:03d}"
        window["video_id"] = video_id

    return windows


def split_windows_from_data(segments, items):
    items_index = _build_items_index(items)

    video_groups = defaultdict(list)
    for segment in segments:
        video_groups[(segment["project"], segment["video_filename"], segment["tester_name"])].append(segment)

    segments_by_video_and_id = {}
    for segment in segments:
        key = (segment["project"], segment["video_filename"], segment["tester_name"])
        if key not in segments_by_video_and_id:
            segments_by_video_and_id[key] = {}
        segments_by_video_and_id[key][segment["segment_id"]] = segment

    all_windows = []
    for (project, video_filename, tester_name), video_segments in sorted(video_groups.items()):
        video_id = _make_video_id(tester_name, project)
        windows = _split_video_windows(video_segments, video_id)
        segments_by_id = segments_by_video_and_id[(project, video_filename, tester_name)]

        for window in windows:
            segment_ids = [segment_id.strip() for segment_id in window["segment_ids"].split(",") if segment_id.strip()]
            window["word_count"] = _count_words(
                segment_ids,
                segments_by_id,
                items_index,
                project,
                video_filename,
                tester_name,
            )
            window["project"] = project
            window["video_filename"] = video_filename
            window["tester_name"] = tester_name

        all_windows.extend(windows)

    return all_windows


def split_windows(segments_csv_path, items_csv_path):
    with open(segments_csv_path, "r", encoding="utf-8") as segments_file:
        segments = list(csv.DictReader(segments_file))
    with open(items_csv_path, "r", encoding="utf-8") as items_file:
        items = list(csv.DictReader(items_file))
    return split_windows_from_data(segments, items)


def build_windows_csv(segments_csv_path, items_csv_path, output_path):
    windows = split_windows(segments_csv_path, items_csv_path)
    fieldnames = [
        "window_id",
        "video_id",
        "start_time",
        "end_time",
        "duration",
        "text",
        "word_count",
        "segment_ids",
        "project",
        "video_filename",
        "tester_name",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(windows)
    print(f"Wrote {len(windows)} windows to {output_path}")
    return windows


if __name__ == "__main__":
    build_windows_csv(
        "data/processed/segments.csv",
        "data/processed/items.csv",
        "data/processed/windows.csv",
    )
