# Testing checklist

## Environment

- [ ] Install Python 3.9+.
- [ ] Install packages using `python -m pip install -r requirements.txt`.
- [ ] Confirm the script starts without import errors.

## Functional tests

- [ ] Run with a valid JPG image.
- [ ] Run with a valid PNG image.
- [ ] Run with a missing image path and confirm a clear error.
- [ ] Run with an invalid ROI and confirm validation catches it.
- [ ] Run with a custom ROI around the rhythm strip.
- [ ] Confirm the plot shows the extracted waveform and candidate peaks.
- [ ] Save a plot using `--save-plot results/ecg_plot.png`.
- [ ] Confirm the supplied duration matches the selected strip's actual time span.

## Project sample set

The project discussion described four examples:
- ECG 1 — expected normal reference.
- ECG 2 — expected normal reference.
- ECG 3 — expected arrhythmia example.
- ECG 4 — expected abnormal example.

For each image, record:
| Sample | Expected category | Estimated BPM | RR SD (s) | RR CV | Visual peak check | Result |
|---|---|---:|---:|---:|---|---|
| ECG 1 | Normal reference | Not recorded | Not recorded | Not recorded | Pending | Pending |
| ECG 2 | Normal reference | Not recorded | Not recorded | Not recorded | Pending | Pending |
| ECG 3 | Arrhythmia example | Not recorded | Not recorded | Not recorded | Pending | Pending |
| ECG 4 | Abnormal example | Not recorded | Not recorded | Not recorded | Pending | Pending |

Do not mark a sample as passed solely because the printed category matches expectation. Check whether the crop, time calibration and candidate peaks are correct. Record actual measurements from the current code.

## Known failure modes

- Wrong rhythm-strip crop.
- Incorrect duration or horizontal scale.
- Grid lines or text mistaken for ECG trace.
- Missed peaks or multiple detections on one complex.
- Motion, scanning or printing artefacts.
- Arrhythmia not detectable from a short or poor-quality strip.

## Acceptance criteria

A test run is acceptable for a classroom demonstration only when the ROI and time scale are documented, candidate peaks are visually plausible, and results are recorded without claiming clinical validity.
