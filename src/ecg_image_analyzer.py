"""Educational ECG image analyser.

Extracts a waveform from a selected ECG image region, detects candidate peaks,
estimates rate and RR variability, and plots the result.

This is not a clinical ECG interpretation or diagnostic tool.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse an ECG image rhythm strip.")
    parser.add_argument("image", type=Path, help="Input JPG/PNG ECG image")
    parser.add_argument("--duration", type=float, default=10.0,
                        help="Time in seconds represented by the selected ROI (default: 10)")
    parser.add_argument("--roi", nargs=4, type=int, metavar=("X", "Y", "W", "H"),
                        help="Optional crop in source-image pixels: x y width height")
    parser.add_argument("--min-peak-distance", type=float, default=0.30,
                        help="Minimum candidate beat separation in seconds (default: 0.30)")
    parser.add_argument("--prominence", type=float, default=0.8,
                        help="Peak prominence as a multiple of waveform robust standard deviation")
    parser.add_argument("--save-plot", type=Path, default=None,
                        help="Optional path to save the plot")
    return parser.parse_args()


def crop_rhythm_strip(image: np.ndarray, roi: list[int] | None) -> np.ndarray:
    height, width = image.shape[:2]
    if roi is not None:
        x, y, w, h = roi
        if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
            raise ValueError("ROI is outside the image or has invalid dimensions.")
        return image[y:y + h, x:x + w]

    # Typical 12-lead printouts place a long rhythm strip near the bottom.
    # This is only a default heuristic; use --roi for other layouts.
    y0, y1 = int(height * 0.76), int(height * 0.95)
    return image[y0:y1, :]


def extract_waveform(roi: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if roi.ndim == 3 else roi.copy()
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Dark ECG trace pixels become 1. A percentile-based threshold is used
    # rather than assuming a particular paper/grid colour.
    threshold = min(180, int(np.percentile(gray, 35)))
    mask = gray < threshold

    # Grid lines can create many pixels in a column. Restrict extraction to
    # columns containing dark pixels and use the median row as a robust trace
    # centre estimate. Columns with no trace are interpolated.
    rows = np.arange(mask.shape[0])
    signal = np.full(mask.shape[1], np.nan, dtype=float)
    for col in range(mask.shape[1]):
        ys = rows[mask[:, col]]
        if ys.size:
            signal[col] = float(np.median(ys))

    valid = np.flatnonzero(np.isfinite(signal))
    if valid.size < max(20, int(mask.shape[1] * 0.15)):
        raise ValueError(
            "Could not extract enough dark trace pixels. Select a tighter rhythm-strip ROI."
        )

    x = np.arange(signal.size)
    signal = np.interp(x, valid, signal[valid])

    # Image y increases downward; invert so upward ECG deflections are positive.
    signal = -signal
    signal -= np.median(signal)
    return signal


def detect_candidate_peaks(signal: np.ndarray, duration: float,
                           min_peak_distance: float,
                           prominence_factor: float) -> tuple[np.ndarray, np.ndarray]:
    samples = signal.size
    samples_per_second = samples / duration
    smooth = gaussian_filter1d(signal, sigma=max(1.0, samples * 0.002))

    # Robust scale limits sensitivity to occasional extreme pixels.
    median = np.median(smooth)
    mad = np.median(np.abs(smooth - median))
    robust_sigma = max(1.4826 * mad, 1.0)
    prominence = max(1.0, prominence_factor * robust_sigma)

    distance = max(1, int(min_peak_distance * samples_per_second))
    peaks, _ = find_peaks(smooth, distance=distance, prominence=prominence)
    return smooth, peaks


def calculate_metrics(peaks: np.ndarray, duration: float,
                      sample_count: int) -> dict[str, float | int | str]:
    if len(peaks) < 2:
        raise ValueError(
            "Fewer than two candidate peaks were found. Adjust --roi or --prominence."
        )

    seconds_per_pixel = duration / sample_count
    rr = np.diff(peaks) * seconds_per_pixel
    rr = rr[(rr > 0.25) & (rr < 2.5)]
    if rr.size == 0:
        raise ValueError("No plausible RR intervals remained after basic quality filtering.")

    mean_rr = float(np.mean(rr))
    bpm = 60.0 / mean_rr
    rr_std = float(np.std(rr, ddof=1)) if rr.size > 1 else 0.0
    rr_cv = rr_std / mean_rr if mean_rr else 0.0

    if rr_cv >= 0.12:
        label = "Irregular RR pattern (review required)"
    elif bpm < 60:
        label = "Low estimated rate"
    elif bpm > 100:
        label = "High estimated rate"
    else:
        label = "Rate and RR pattern within simple reference limits"

    return {
        "bpm": bpm,
        "rr_std": rr_std,
        "rr_cv": rr_cv,
        "interval_count": int(rr.size),
        "label": label,
    }


def main() -> int:
    args = parse_args()
    if args.duration <= 0:
        print("Error: --duration must be greater than zero.", file=sys.stderr)
        return 2

    image = cv2.imread(str(args.image))
    if image is None:
        print(f"Error: could not read image: {args.image}", file=sys.stderr)
        return 2

    try:
        roi = crop_rhythm_strip(image, args.roi)
        raw_signal = extract_waveform(roi)
        smooth, peaks = detect_candidate_peaks(
            raw_signal, args.duration, args.min_peak_distance, args.prominence
        )
        metrics = calculate_metrics(peaks, args.duration, len(raw_signal))
    except ValueError as exc:
        print(f"Analysis could not be completed: {exc}", file=sys.stderr)
        return 1

    print("\n========== ECG IMAGE ANALYSIS (EDUCATIONAL) ==========")
    print(f"File: {args.image.name}")
    print(f"Estimated heart rate: {metrics['bpm']:.2f} bpm")
    print(f"RR interval standard deviation: {metrics['rr_std']:.4f} s")
    print(f"RR coefficient of variation: {metrics['rr_cv']:.4f}")
    print(f"Usable RR intervals: {metrics['interval_count']}")
    print(f"Signal summary: {metrics['label']}")
    print("======================================================")
    print("Image-based estimates only; not intended for clinical diagnosis.\n")

    x_seconds = np.linspace(0, args.duration, len(smooth), endpoint=False)
    peak_times = peaks * args.duration / len(smooth)
    plt.figure(figsize=(13, 5))
    plt.plot(x_seconds, smooth, label="Extracted / smoothed ECG trace")
    plt.scatter(peak_times, smooth[peaks], color="red", s=28,
                label="Candidate R-peaks", zorder=3)
    plt.title(f"ECG rhythm-strip extraction — {args.image.name}")
    plt.xlabel("Time (seconds; scaled using --duration)")
    plt.ylabel("Relative image-derived amplitude (pixels)")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()

    if args.save_plot:
        args.save_plot.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(args.save_plot, dpi=160)
        print(f"Plot saved to: {args.save_plot}")
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
