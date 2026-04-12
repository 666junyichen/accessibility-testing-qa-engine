import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from preprocessing.window_splitter import MIN_DURATION, TARGET_DURATION, split_windows_from_data


def make_segment(
    seg_id,
    transcript,
    start,
    end,
    item_ids="",
    project="test-project",
    video_filename="test_video.mp4",
    tester_name="tester1",
):
    return {
        "segment_id": str(seg_id),
        "transcript": transcript,
        "start_time": str(start),
        "end_time": str(end),
        "item_ids": item_ids,
        "project": project,
        "video_filename": video_filename,
        "tester_name": tester_name,
    }


def make_item(
    item_id,
    content,
    item_type="pronunciation",
    project="test-project",
    video_filename="test_video.mp4",
    tester_name="tester1",
):
    return {
        "item_id": str(item_id),
        "content": content,
        "type": item_type,
        "start_time": "0.0",
        "end_time": "0.1",
        "confidence": "0.99",
        "project": project,
        "video_filename": video_filename,
        "tester_name": tester_name,
    }


class TestNormalSplit:
    def test_two_windows(self):
        segments = []
        items = []
        for i in range(20):
            start = i * 6.0
            end = start + 6.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 2
        assert windows[0]["start_time"] == 0.0
        assert windows[0]["duration"] >= TARGET_DURATION
        for window in windows:
            assert "window_id" in window
            assert "video_id" in window
            assert "start_time" in window
            assert "end_time" in window
            assert "duration" in window
            assert "text" in window
            assert "word_count" in window
            assert "segment_ids" in window
            assert "project" in window
            assert "video_filename" in window
            assert "tester_name" in window

    def test_window_continuity(self):
        segments = []
        items = []
        for i in range(30):
            start = i * 4.0
            end = start + 4.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert windows[0]["start_time"] == 0.0
        assert windows[-1]["end_time"] == 120.0


class TestShortTailMerge:
    def test_tail_merged(self):
        segments = []
        items = []
        for i in range(14):
            start = i * 5.0
            end = start + 5.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["end_time"] == 70.0
        assert windows[0]["word_count"] == 14

    def test_tail_not_merged_when_above_min(self):
        segments = []
        items = []
        for i in range(19):
            start = i * 5.0
            end = start + 5.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 2
        assert windows[1]["duration"] == 35.0


class TestShortVideo:
    def test_video_under_60s(self):
        segments = []
        items = []
        for i in range(9):
            start = i * 5.0
            end = start + 5.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["duration"] == 45.0

    def test_video_under_30s(self):
        segments = []
        items = []
        for i in range(3):
            start = i * 5.0
            end = start + 5.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["duration"] == 15.0

    def test_single_segment_video(self):
        segments = [make_segment(0, "hello world", 0.0, 3.5, "0")]
        items = [make_item(0, "hello"), make_item(1, "world")]

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["text"] == "hello world"


class TestWordCount:
    def test_counts_only_pronunciation(self):
        segments = [
            make_segment(0, "Hello world.", 0.0, 5.0, "0,1,2"),
        ]
        items = [
            make_item(0, "Hello", "pronunciation"),
            make_item(1, "world", "pronunciation"),
            make_item(2, ".", "punctuation"),
        ]

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["word_count"] == 2

    def test_word_count_across_segments(self):
        segments = [
            make_segment(0, "Hello", 0.0, 30.0, "0"),
            make_segment(1, "world", 30.0, 55.0, "1"),
        ]
        items = [
            make_item(0, "Hello", "pronunciation"),
            make_item(1, "world", "pronunciation"),
        ]

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["word_count"] == 2

    def test_empty_item_ids(self):
        segments = [
            make_segment(0, "silence", 0.0, 5.0, ""),
        ]
        items = []

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["word_count"] == 0


class TestWindowAndVideoId:
    def test_window_id_format(self):
        segments = []
        items = []
        for i in range(20):
            start = i * 6.0
            end = start + 6.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert windows[0]["window_id"] == "tester1_test-project_w000"
        assert windows[1]["window_id"] == "tester1_test-project_w001"

    def test_video_id_uses_project_abbr(self):
        segments = [
            make_segment(
                0,
                "hello",
                0.0,
                5.0,
                "0",
                project="department-of-premier-and-cabinet-wa",
                video_filename="test.mp4",
                tester_name="ghum",
            ),
        ]
        items = [
            make_item(
                0,
                "hello",
                project="department-of-premier-and-cabinet-wa",
                video_filename="test.mp4",
                tester_name="ghum",
            ),
        ]

        windows = split_windows_from_data(segments, items)
        assert windows[0]["video_id"] == "ghum_wa"
        assert windows[0]["window_id"] == "ghum_wa_w000"

    def test_video_id_cross_project_unique(self):
        segments = [
            make_segment(
                0,
                "hello",
                0.0,
                5.0,
                "0",
                project="department-of-premier-and-cabinet-wa",
                video_filename="vid1.mp4",
                tester_name="terry",
            ),
            make_segment(
                0,
                "world",
                0.0,
                5.0,
                "0",
                project="suncorp-insurance",
                video_filename="vid2.mp4",
                tester_name="terry",
            ),
        ]
        items = [
            make_item(
                0,
                "hello",
                project="department-of-premier-and-cabinet-wa",
                video_filename="vid1.mp4",
                tester_name="terry",
            ),
            make_item(
                0,
                "world",
                project="suncorp-insurance",
                video_filename="vid2.mp4",
                tester_name="terry",
            ),
        ]

        windows = split_windows_from_data(segments, items)
        video_ids = {window["video_id"] for window in windows}
        assert "terry_wa" in video_ids
        assert "terry_suncorp" in video_ids
        assert len(video_ids) == 2

    def test_window_id_unique_within_video(self):
        segments = []
        items = []
        for i in range(50):
            start = i * 4.0
            end = start + 4.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        window_ids = [window["window_id"] for window in windows]
        assert len(window_ids) == len(set(window_ids))


class TestMaxDuration:
    def test_tail_merge_near_max(self):
        segments = []
        items = []
        for i in range(17):
            start = i * 5.0
            end = start + 5.0
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        windows = split_windows_from_data(segments, items)
        assert len(windows) == 1
        assert windows[0]["duration"] == 85.0
        assert windows[0]["duration"] <= 90

    def test_tail_merge_exceeds_max_logs_warning(self, caplog):
        import logging

        segments = []
        items = []
        for i in range(14):
            start = i * 6.5
            end = start + 6.5
            segments.append(make_segment(i, f"word{i}", start, end, str(i)))
            items.append(make_item(i, f"word{i}"))

        with caplog.at_level(logging.WARNING, logger="preprocessing.window_splitter"):
            windows = split_windows_from_data(segments, items)

        assert len(windows) == 1
        assert windows[0]["duration"] == 91.0
        assert any("exceeds MAX_DURATION" in record.message for record in caplog.records)
