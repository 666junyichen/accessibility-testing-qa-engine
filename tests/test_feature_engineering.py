import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from layer2.feature_engineering import (
    AUDIO_FEATURE_COLS,
    FEATURE_COLS,
    ID_COLS,
    NAN_THRESHOLD,
    build_feature_matrices,
    build_text_features,
    impute_or_fail,
    validate_join,
)


class TestBuildTextFeatures:
    def test_empty_string_returns_zero(self):
        result = build_text_features("")
        assert result == {"unique_words_ratio": 0.0, "avg_sentence_length": 0.0}

    def test_whitespace_only_returns_zero(self):
        result = build_text_features("   \t\n  ")
        assert result == {"unique_words_ratio": 0.0, "avg_sentence_length": 0.0}

    def test_punctuation_only_returns_zero(self):
        result = build_text_features("... !! ??")
        assert result == {"unique_words_ratio": 0.0, "avg_sentence_length": 0.0}

    def test_unique_words_ratio_basic(self):
        result = build_text_features("hello world hello")
        assert result["unique_words_ratio"] == pytest.approx(2 / 3)

    def test_avg_sentence_length_basic(self):
        result = build_text_features("one two three. four five.")
        assert result["avg_sentence_length"] == pytest.approx(2.5)

    def test_consecutive_punctuation_edge_case(self):
        result = build_text_features("Hello... world!!")
        assert result["unique_words_ratio"] == pytest.approx(1.0)
        assert result["avg_sentence_length"] == pytest.approx(1.0)

    def test_punctuation_tokens_filtered(self):
        result = build_text_features("a , , b")
        assert result["unique_words_ratio"] == pytest.approx(1.0)
        assert result["avg_sentence_length"] == pytest.approx(2.0)

    def test_no_sentence_delimiter_fallback(self):
        result = build_text_features("hello world foo")
        assert result["avg_sentence_length"] == pytest.approx(3.0)


class TestValidateJoin:
    def _make_audio_df(self, window_ids):
        return pd.DataFrame({"window_id": window_ids})

    def _make_windows_df(self, window_ids):
        return pd.DataFrame(
            {
                "window_id": window_ids,
                "text": ["foo"] * len(window_ids),
                "project": ["p"] * len(window_ids),
                "tester_name": ["t"] * len(window_ids),
            }
        )

    def test_clean_one_to_one_passes(self):
        audio = self._make_audio_df(["w1", "w2", "w3"])
        windows = self._make_windows_df(["w1", "w2", "w3", "w4"])
        validate_join(audio, windows)

    def test_missing_window_id_raises(self):
        audio = self._make_audio_df(["w1", "w2", "w99"])
        windows = self._make_windows_df(["w1", "w2"])
        with pytest.raises(ValueError, match="missing"):
            validate_join(audio, windows)

    def test_duplicate_window_id_in_windows_raises(self):
        audio = self._make_audio_df(["w1", "w2"])
        windows = pd.DataFrame(
            {
                "window_id": ["w1", "w1", "w2"],
                "text": ["a", "b", "c"],
                "project": ["p", "p", "p"],
                "tester_name": ["t", "t", "t"],
            }
        )
        with pytest.raises(ValueError, match="duplicate"):
            validate_join(audio, windows)

    def test_duplicate_window_id_in_audio_raises(self):
        audio = self._make_audio_df(["w1", "w1", "w2"])
        windows = self._make_windows_df(["w1", "w2"])
        with pytest.raises(ValueError, match="duplicate"):
            validate_join(audio, windows)


class TestImputeOrFail:
    def _make_df(self, n_rows: int, nan_positions: dict):
        data = {col: np.random.rand(n_rows) for col in AUDIO_FEATURE_COLS}
        data["window_id"] = [f"w{i}" for i in range(n_rows)]
        data["video_id"] = [f"v{i % 5}" for i in range(n_rows)]
        df = pd.DataFrame(data)
        for col, rows in nan_positions.items():
            df.loc[rows, col] = np.nan
        return df

    def test_no_nan_returns_unchanged(self):
        df = self._make_df(1000, nan_positions={})
        out, stats = impute_or_fail(df)
        pd.testing.assert_frame_equal(out, df)
        assert all(s["filled"] == 0 for s in stats["columns"].values())

    def test_low_nan_rate_fills_with_mean(self):
        df = self._make_df(1000, nan_positions={"silence_ratio": [0, 1, 2, 3, 4]})
        out, stats = impute_or_fail(df)
        assert out["silence_ratio"].isna().sum() == 0
        assert stats["columns"]["silence_ratio"]["filled"] == 5
        expected_mean = df["silence_ratio"].mean()
        assert out.loc[0, "silence_ratio"] == pytest.approx(expected_mean)

    def test_high_nan_rate_raises(self):
        nan_rows = list(range(50))
        df = self._make_df(1000, nan_positions={"words_per_minute": nan_rows})
        with pytest.raises(ValueError, match="NaN rate"):
            impute_or_fail(df)

    def test_boundary_exactly_1_percent_raises(self):
        nan_rows = list(range(10))
        df = self._make_df(1000, nan_positions={"avg_confidence": nan_rows})
        with pytest.raises(ValueError, match="NaN rate"):
            impute_or_fail(df)

    def test_stats_dict_shape(self):
        df = self._make_df(1000, nan_positions={"narration_density": [0, 1]})
        _, stats = impute_or_fail(df)
        col_stats = stats["columns"]["narration_density"]
        assert col_stats["nan_count"] == 2
        assert col_stats["nan_rate"] == pytest.approx(0.002)
        assert col_stats["filled"] == 2
        assert "by_video_id" in col_stats


@pytest.fixture
def tiny_csvs(tmp_path):
    audio = pd.DataFrame(
        {
            "window_id": ["w1", "w2", "w3"],
            "video_id": ["v1", "v1", "v2"],
            "video_filename": ["a.mp4", "a.mp4", "b.mp4"],
            "start_time": [0.0, 60.0, 0.0],
            "end_time": [60.0, 120.0, 60.0],
            "duration": [60.0, 60.0, 60.0],
            "silence_ratio": [0.3, 0.4, 0.5],
            "narration_density": [0.8, 0.7, 0.6],
            "avg_silence_duration": [1.0, 1.2, 1.5],
            "words_per_minute": [120.0, 100.0, 80.0],
            "avg_confidence": [0.9, 0.85, 0.8],
        }
    )
    windows = pd.DataFrame(
        {
            "window_id": ["w1", "w2", "w3", "w4"],
            "video_id": ["v1", "v1", "v2", "v3"],
            "start_time": [0.0, 60.0, 0.0, 0.0],
            "end_time": [60.0, 120.0, 60.0, 60.0],
            "duration": [60.0, 60.0, 60.0, 60.0],
            "text": [
                "hello world hello foo",
                "bar baz. qux quux.",
                "",
                "should not appear",
            ],
            "word_count": [4, 4, 0, 3],
            "segment_ids": ["s1", "s2", "s3", "s4"],
            "project": ["proj_a", "proj_a", "proj_b", "proj_c"],
            "video_filename": ["a.mp4", "a.mp4", "b.mp4", "c.mp4"],
            "tester_name": ["t1", "t1", "t2", "t3"],
        }
    )

    audio_csv = tmp_path / "audio.csv"
    windows_csv = tmp_path / "windows.csv"
    raw_out = tmp_path / "raw.csv"
    scaled_out = tmp_path / "scaled.csv"
    log_out = tmp_path / "imputation.log"

    audio.to_csv(audio_csv, index=False)
    windows.to_csv(windows_csv, index=False)

    return {
        "audio_csv": audio_csv,
        "windows_csv": windows_csv,
        "raw_out": raw_out,
        "scaled_out": scaled_out,
        "log_out": log_out,
    }


@pytest.fixture
def large_csvs_with_low_nan(tmp_path):
    n = 200
    audio = pd.DataFrame(
        {
            "window_id": [f"w{i}" for i in range(n)],
            "video_id": [f"v{i % 5}" for i in range(n)],
            "video_filename": [f"vid{i % 5}.mp4" for i in range(n)],
            "start_time": [float(i * 60) for i in range(n)],
            "end_time": [float((i + 1) * 60) for i in range(n)],
            "duration": [60.0] * n,
            "silence_ratio": [0.3 + 0.001 * i for i in range(n)],
            "narration_density": [0.7 - 0.001 * i for i in range(n)],
            "avg_silence_duration": [1.0 + 0.01 * i for i in range(n)],
            "words_per_minute": [100.0 + i for i in range(n)],
            "avg_confidence": [0.9 - 0.001 * i for i in range(n)],
        }
    )
    audio.loc[42, "silence_ratio"] = float("nan")

    windows = pd.DataFrame(
        {
            "window_id": [f"w{i}" for i in range(n)],
            "video_id": [f"v{i % 5}" for i in range(n)],
            "start_time": [float(i * 60) for i in range(n)],
            "end_time": [float((i + 1) * 60) for i in range(n)],
            "duration": [60.0] * n,
            "text": ["hello world."] * n,
            "word_count": [2] * n,
            "segment_ids": [f"s{i}" for i in range(n)],
            "project": [f"proj_{i % 3}" for i in range(n)],
            "video_filename": [f"vid{i % 5}.mp4" for i in range(n)],
            "tester_name": [f"t{i % 4}" for i in range(n)],
        }
    )

    audio_csv = tmp_path / "audio.csv"
    windows_csv = tmp_path / "windows.csv"
    raw_out = tmp_path / "raw.csv"
    scaled_out = tmp_path / "scaled.csv"
    log_out = tmp_path / "imputation.log"

    audio.to_csv(audio_csv, index=False)
    windows.to_csv(windows_csv, index=False)

    return {
        "audio_csv": audio_csv,
        "windows_csv": windows_csv,
        "raw_out": raw_out,
        "scaled_out": scaled_out,
        "log_out": log_out,
    }


class TestBuildFeatureMatrices:
    def test_row_count_matches_audio(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        raw = pd.read_csv(tiny_csvs["raw_out"])
        scaled = pd.read_csv(tiny_csvs["scaled_out"])
        assert len(raw) == 3
        assert len(scaled) == 3

    def test_raw_and_scaled_window_ids_identical(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        raw = pd.read_csv(tiny_csvs["raw_out"])
        scaled = pd.read_csv(tiny_csvs["scaled_out"])
        assert list(raw["window_id"]) == list(scaled["window_id"])

    def test_scaled_feature_columns_are_zscore(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        scaled = pd.read_csv(tiny_csvs["scaled_out"])
        for col in FEATURE_COLS:
            assert scaled[col].mean() == pytest.approx(0.0, abs=1e-6)
            assert scaled[col].var(ddof=0) == pytest.approx(1.0, abs=1e-6)

    def test_scaled_columns_exact_set_and_order(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        scaled = pd.read_csv(tiny_csvs["scaled_out"])
        assert list(scaled.columns) == ID_COLS + FEATURE_COLS

    def test_raw_columns_exact_set_and_order(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        raw = pd.read_csv(tiny_csvs["raw_out"])
        assert list(raw.columns) == ID_COLS + FEATURE_COLS

    def test_id_cols_identical_between_raw_and_scaled(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        raw = pd.read_csv(tiny_csvs["raw_out"])
        scaled = pd.read_csv(tiny_csvs["scaled_out"])
        for col in ID_COLS:
            assert list(raw[col].astype(str)) == list(scaled[col].astype(str))

    def test_empty_text_yields_zero_text_features(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        raw = pd.read_csv(tiny_csvs["raw_out"])
        row = raw.loc[raw["window_id"] == "w3"].iloc[0]
        assert row["unique_words_ratio"] == 0.0
        assert row["avg_sentence_length"] == 0.0

    def test_log_file_written(self, tiny_csvs):
        build_feature_matrices(**tiny_csvs)
        assert tiny_csvs["log_out"].exists()
        content = tiny_csvs["log_out"].read_text()
        for col in AUDIO_FEATURE_COLS:
            assert col in content


class TestEndToEndImputation:
    def test_low_nan_rate_fills_and_logs(self, large_csvs_with_low_nan):
        build_feature_matrices(**large_csvs_with_low_nan)
        raw = pd.read_csv(large_csvs_with_low_nan["raw_out"])
        assert raw["silence_ratio"].isna().sum() == 0
        content = large_csvs_with_low_nan["log_out"].read_text()
        assert "silence_ratio" in content
        assert "filled=1" in content


class TestJoinConsistency:
    def test_mismatched_overlap_column_raises(self, tmp_path):
        audio = pd.DataFrame(
            {
                "window_id": ["w1", "w2"],
                "video_id": ["v1", "v2"],
                "video_filename": ["a.mp4", "b.mp4"],
                "start_time": [0.0, 0.0],
                "end_time": [60.0, 60.0],
                "duration": [60.0, 60.0],
                "silence_ratio": [0.3, 0.4],
                "narration_density": [0.8, 0.7],
                "avg_silence_duration": [1.0, 1.2],
                "words_per_minute": [120.0, 100.0],
                "avg_confidence": [0.9, 0.85],
            }
        )
        windows = pd.DataFrame(
            {
                "window_id": ["w1", "w2"],
                "video_id": ["v1", "v99"],
                "start_time": [0.0, 0.0],
                "end_time": [60.0, 60.0],
                "duration": [60.0, 60.0],
                "text": ["a", "b"],
                "word_count": [1, 1],
                "segment_ids": ["s1", "s2"],
                "project": ["p", "p"],
                "video_filename": ["a.mp4", "b.mp4"],
                "tester_name": ["t", "t"],
            }
        )
        audio_csv = tmp_path / "a.csv"
        windows_csv = tmp_path / "w.csv"
        audio.to_csv(audio_csv, index=False)
        windows.to_csv(windows_csv, index=False)

        with pytest.raises(ValueError, match="inconsistent"):
            build_feature_matrices(
                audio_csv=audio_csv,
                windows_csv=windows_csv,
                raw_out=tmp_path / "raw.csv",
                scaled_out=tmp_path / "scaled.csv",
                log_out=tmp_path / "log.log",
            )
