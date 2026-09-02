"""Convert a single combined phase-timestamp spreadsheet (one sheet, all
videos, mm:ss/hh:mm:ss timestamps) into the per-video interval CSVs the
Stage 2 notebook expects under annotations/{video_id}.csv.

Run this once, locally or in Colab, before Section 2 of
notebooks/stage2_phase_recognition.ipynb. It does not touch the notebook
or CFG — it only produces the annotations/ files that Stage 2's
load_video_intervals() reads.

Edit the CONFIG block below to match your spreadsheet's actual column
headers, then run:

    python scripts/spreadsheet_to_annotations.py
"""

import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# EDIT THESE to match your spreadsheet
# ---------------------------------------------------------------------------
INPUT_PATH = "phase_timestamps.xlsx"   # your spreadsheet (.xlsx or .csv)
SHEET_NAME = 0                          # sheet name or index, if .xlsx

COL_VIDEO = "video_id"                  # column identifying which video a row belongs to
COL_PHASE = "phase"                     # column with the phase label text
COL_START = "start_time"                # column with the mm:ss / hh:mm:ss start
COL_END = "end_time"                    # column with the mm:ss / hh:mm:ss end

# Must match the CVAT/annotations directory the Stage 2 notebook's CONFIG
# points DIRS["annotations"] at (default: <project_root>/annotations).
OUTPUT_DIR = "annotations"
# ---------------------------------------------------------------------------


TIMESTAMP_RE = re.compile(r"^\d{1,3}(:\d{2}){1,2}(\.\d+)?$")


def parse_timestamp(value) -> float:
    """Accepts mm:ss, hh:mm:ss, or a bare number of seconds. Returns seconds."""
    if pd.isna(value):
        raise ValueError("empty timestamp")
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if not TIMESTAMP_RE.match(s) and ":" not in s:
        return float(s)  # plain number stored as text, e.g. "252"
    parts = [float(p) for p in s.split(":")]
    if len(parts) == 2:
        m, sec = parts
        return m * 60 + sec
    if len(parts) == 3:
        h, m, sec = parts
        return h * 3600 + m * 60 + sec
    raise ValueError(f"unrecognized timestamp format: {value!r}")


def main():
    path = Path(INPUT_PATH)
    if path.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(path, sheet_name=SHEET_NAME)
    else:
        df = pd.read_csv(path)

    missing = {COL_VIDEO, COL_PHASE, COL_START, COL_END} - set(df.columns)
    if missing:
        raise ValueError(
            f"Spreadsheet is missing expected columns {missing}. "
            f"Found columns: {list(df.columns)}. Edit CONFIG at the top of this script."
        )

    df = df.rename(columns={COL_VIDEO: "video_id", COL_PHASE: "phase",
                             COL_START: "start_time", COL_END: "end_time"})
    df = df[["video_id", "phase", "start_time", "end_time"]].dropna(how="all")

    df["start_sec"] = df["start_time"].apply(parse_timestamp)
    df["end_sec"] = df["end_time"].apply(parse_timestamp)

    bad = df[df["end_sec"] <= df["start_sec"]]
    if len(bad):
        print("WARNING — rows where end <= start (fix in the spreadsheet before running Stage 2):")
        print(bad[["video_id", "phase", "start_time", "end_time"]])
        print()

    print("Unique phase labels found — check these match CFG.phase_taxonomy exactly (case-sensitive):")
    for p in sorted(df.phase.unique()):
        print(f"  {p!r}")
    print()

    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    for video_id, group in df.groupby("video_id"):
        group = group.sort_values("start_sec")

        # Same overlap check Stage 2's assert_no_overlap performs, run here
        # so a bad spreadsheet row is caught now rather than mid-notebook.
        prev_end = -1.0
        prev_phase = None
        for _, row in group.iterrows():
            if row.start_sec < prev_end:
                print(f"WARNING — [{video_id}] possible overlap: {row.phase!r} starts at "
                      f"{row.start_sec:.1f}s, before {prev_phase!r} ends at {prev_end:.1f}s")
            prev_end = max(prev_end, row.end_sec)
            prev_phase = row.phase

        out_path = out_dir / f"{video_id}.csv"
        group[["phase", "start_sec", "end_sec"]].to_csv(out_path, index=False)
        print(f"Wrote {out_path} ({len(group)} intervals)")


if __name__ == "__main__":
    main()
