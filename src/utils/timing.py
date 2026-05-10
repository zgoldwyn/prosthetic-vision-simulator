"""
Timing analysis utility for Prosthetic Vision Simulator.

Reads one or more timing CSV files from outputs/logs/ and summarizes
real-time performance by encoder mode.

Usage:
    python -m src.utils.timing
    python -m src.utils.timing outputs/logs/timing_20260509_180751.csv
"""

from __future__ import annotations
import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, median


TIMING_COLUMNS = [
    "loop_fps",
    "loop_ms",
    "capture_ms",
    "encode_ms",
    "display_ms",
]


def parse_float(value: str) -> float | None:
    """Safely parse a float from a CSV cell."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows(csv_paths: list[Path]) -> list[dict[str, str]]:
    """Load timing rows from one or more CSV files."""
    rows: list[dict[str, str]] = []

    for csv_path in csv_paths:
        if not csv_path.exists():
            print(f"Skipping missing file: {csv_path}")
            continue

        with csv_path.open("r", newline="") as file:
            reader = csv.DictReader(file)
            rows.extend(reader)

    return rows


def summarize_by_mode(rows: list[dict[str, str]]) -> dict[str, dict[str, float]]:
    """Summarize timing values by encoder mode."""
    values_by_mode: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for row in rows:
        mode = row.get("mode", "unknown")

        for column in TIMING_COLUMNS:
            parsed_value = parse_float(row.get(column, ""))
            if parsed_value is not None:
                values_by_mode[mode][column].append(parsed_value)

    summary: dict[str, dict[str, float]] = {}

    for mode, columns in values_by_mode.items():
        summary[mode] = {"frames": float(len(next(iter(columns.values()), [])))}

        for column, values in columns.items():
            if not values:
                continue

            summary[mode][f"mean_{column}"] = mean(values)
            summary[mode][f"median_{column}"] = median(values)
            summary[mode][f"min_{column}"] = min(values)
            summary[mode][f"max_{column}"] = max(values)

    return summary


def format_mode_name(mode: str) -> str:
    """Convert internal mode names into readable labels."""
    return {
        "basic": "Grayscale",
        "edge_enhanced": "Canny Edge",
        "hed": "HED Edge",
        "hybrid": "Hybrid HED + Gray",
    }.get(mode, mode)


def print_summary(summary: dict[str, dict[str, float]]) -> None:
    """Print a readable performance summary."""
    if not summary:
        print("No timing data found.")
        return

    print("\nTiming Summary by Mode")
    print("=" * 80)
    print(
        f"{'Mode':<22} {'Frames':>8} {'Mean FPS':>10} {'Encode ms':>12} "
        f"{'Loop ms':>10} {'Capture ms':>12} {'Display ms':>12}"
    )
    print("-" * 80)

    for mode, stats in summary.items():
        print(
            f"{format_mode_name(mode):<22} "
            f"{int(stats.get('frames', 0)):>8} "
            f"{stats.get('mean_loop_fps', 0):>10.1f} "
            f"{stats.get('mean_encode_ms', 0):>12.1f} "
            f"{stats.get('mean_loop_ms', 0):>10.1f} "
            f"{stats.get('mean_capture_ms', 0):>12.1f} "
            f"{stats.get('mean_display_ms', 0):>12.1f}"
        )

    print("=" * 80)


def print_poster_language(summary: dict[str, dict[str, float]]) -> None:
    """Print short language that can be reused in a README, poster, or notes."""
    if not summary:
        return

    print("\nDraft poster language")
    print("=" * 80)

    for mode, stats in summary.items():
        mode_name = format_mode_name(mode)
        mean_fps = stats.get("mean_loop_fps", 0)
        mean_encode = stats.get("mean_encode_ms", 0)
        mean_loop = stats.get("mean_loop_ms", 0)

        print(
            f"- {mode_name} ran at an average of {mean_fps:.1f} FPS "
            f"with {mean_encode:.1f} ms mean encoder latency and "
            f"{mean_loop:.1f} ms mean loop time."
        )

    print("=" * 80)


def write_summary_csv(summary: dict[str, dict[str, float]], output_path: Path) -> None:
    """Write summary statistics to a CSV file for plotting or poster tables."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "mode",
        "display_mode",
        "frames",
        "mean_loop_fps",
        "mean_loop_ms",
        "mean_capture_ms",
        "mean_encode_ms",
        "mean_display_ms",
        "median_loop_fps",
        "median_loop_ms",
        "median_capture_ms",
        "median_encode_ms",
        "median_display_ms",
    ]

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for mode, stats in summary.items():
            row = {field: stats.get(field, "") for field in fieldnames}
            row["mode"] = mode
            row["display_mode"] = format_mode_name(mode)
            writer.writerow(row)


def find_default_logs() -> list[Path]:
    """Find timing CSVs in the default outputs/logs directory."""
    logs_dir = Path("outputs/logs")
    return sorted(logs_dir.glob("timing_*.csv"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze prosthetic vision timing logs.")
    parser.add_argument(
        "csv_paths",
        nargs="*",
        type=Path,
        help="Optional timing CSV files. If omitted, outputs/logs/timing_*.csv is used.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/timing_summary.csv"),
        help="Path for the summary CSV output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    csv_paths = args.csv_paths if args.csv_paths else find_default_logs()

    if not csv_paths:
        print("No timing CSV files found. Run app.py first to create logs.")
        return

    rows = load_rows(csv_paths)
    summary = summarize_by_mode(rows)

    print(f"Loaded {len(rows)} rows from {len(csv_paths)} file(s).")
    print_summary(summary)
    print_poster_language(summary)
    write_summary_csv(summary, args.output)
    print(f"\nSaved summary CSV to {args.output}")


if __name__ == "__main__":
    main()