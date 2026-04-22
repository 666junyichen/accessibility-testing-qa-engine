import pandas as pd

windows = pd.read_csv("data/processed/windows.csv")

sample = windows.sample(n=50, random_state=42)[[
    "window_id",
    "project",
    "video_id",
    "video_filename",
    "tester_name",
    "start_time",
    "end_time",
    "duration",
    "text",
]]

sample["initial_observation"] = ""
sample["possible_friction_type"] = ""
sample["possible_sentiment"] = ""
sample["possible_narration_type"] = ""
sample["primary_evidence"] = ""
sample["notes"] = ""

sample.to_csv("data/annotations/r3_window_review_sample.csv", index=False)
