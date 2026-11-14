# Design decisions

1. **Image-based input:** The prototype accepts JPG/PNG ECG images rather than requiring a live ECG acquisition board.
2. **Python processing stack:** OpenCV handles image operations, NumPy handles array calculations, SciPy provides smoothing and peak detection, and Matplotlib provides visual verification.
3. **Rhythm-strip ROI:** A configurable crop is supported because ECG layouts vary. The default lower-strip crop is only a convenience heuristic.
4. **Explicit duration:** The strip duration is supplied by the operator instead of being silently guessed. Incorrect duration calibration produces incorrect BPM.
5. **Candidate peak terminology:** Detected maxima are called candidate R-peaks because image artefacts and grid intersections can create false detections.
6. **Conservative output:** The program reports rate and RR variability rather than asserting a clinical diagnosis.
7. **Existing licence:** The repository's pre-existing MIT licence is retained; no new licence is asserted by this documentation update.
8. **No fabricated validation:** The four discussed sample images are documented as intended test cases, but inconsistent earlier results mean the current implementation must be re-tested before any accuracy claim.
