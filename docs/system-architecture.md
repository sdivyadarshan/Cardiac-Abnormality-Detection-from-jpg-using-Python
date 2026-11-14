# System architecture

```mermaid
flowchart TD
    A[ECG image file] --> B[OpenCV: load image]
    B --> C[ROI selection]
    C --> D[Grayscale and blur]
    D --> E[Dark trace mask]
    E --> F[NumPy: waveform extraction]
    F --> G[SciPy: Gaussian smoothing]
    G --> H[SciPy: candidate R-peak detection]
    H --> I[NumPy: RR intervals and metrics]
    I --> J[Educational summary]
    F --> K[Matplotlib plot]
    H --> K
```

## Modules

- **Input layer:** accepts a local ECG image and command-line settings.
- **Image-processing layer:** selects the rhythm-strip region, converts it to grayscale and extracts a one-dimensional trace.
- **Signal-processing layer:** smooths the extracted sequence and identifies candidate peaks.
- **Analysis layer:** derives RR intervals, heart-rate estimate and variability statistics.
- **Presentation layer:** prints a text report and displays or saves a plot.

## Data flow

The image is transformed into a one-dimensional array of relative pixel amplitudes. Peak locations are measured in pixels and converted to time using the user-provided strip duration. Therefore crop selection and duration calibration directly affect the reported rate.
