# Algorithm and processing logic

## Input

The program accepts a raster ECG image (JPG, JPEG or PNG). The selected region should contain one continuous rhythm strip. The default crop targets the lower strip of a typical 12-lead printout; other layouts require an explicit ROI.

## Processing stages

1. **Image loading — OpenCV:** `cv2.imread` loads the image. The selected region is converted to grayscale and lightly blurred to reduce isolated pixel noise.
2. **Trace segmentation — OpenCV and NumPy:** A dark-pixel mask is created. For each image column, the median row containing dark pixels is used as a rough trace coordinate. Missing columns are linearly interpolated.
3. **Waveform orientation:** Image coordinates increase downward, so the extracted row coordinate is inverted to make upward deflections positive. The median is removed to centre the signal.
4. **Smoothing — SciPy:** A Gaussian filter suppresses small pixel-level variations.
5. **Candidate peak detection — SciPy:** `scipy.signal.find_peaks` identifies local maxima using a minimum separation and prominence threshold. These are candidate R-peaks and must be checked against the plotted signal.
6. **RR intervals — NumPy:** Differences between candidate peak positions are converted to seconds using the supplied duration of the selected strip.
7. **Metrics:** Mean RR interval is converted to beats per minute using (HR = 60 / mean(RR)). The program also reports RR standard deviation and coefficient of variation.
8. **Visualisation — Matplotlib:** The extracted trace and candidate peaks are plotted for manual review.

## Important assumptions

- The crop contains one rhythm strip, not multiple stacked leads.
- The duration argument accurately describes the horizontal time represented by the crop.
- The ECG trace is darker than most of the background.
- The simple column-median extraction can be confused by grid lines, text, calibration marks, overlapping traces and artefacts.

## Classification scope

The output uses only estimated rate and RR variability to create a cautious signal summary. An irregular RR pattern is not, by itself, a diagnosis of arrhythmia. This implementation does not claim to measure PR interval, QRS duration or ST-segment deviation reliably.
