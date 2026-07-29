# Prosthetic Vision Simulator

This repository contains a real-time prosthetic vision simulator that converts webcam input into low-bandwidth visual representations inspired by retinal and cortical visual prostheses.

The current implementation focuses on comparing encoder and renderer choices under practical constraints such as resolution, latency, edge preservation, and prosthetic-style phosphene display. It includes live webcam processing, multiple visual encoders, timing instrumentation, CSV logging, and a timing-summary utility.

## Current Capabilities

- Real-time webcam input through OpenCV.
- Grayscale pixelated encoder for a fast baseline.
- Canny edge encoder for classical edge-enhanced prosthetic vision.
- HED learned edge encoder using the local Caffe model in `src/models/HED/`.
- Hybrid HED + grayscale encoder that blends scene brightness with learned boundaries.
- Pixel-grid rendering and soft phosphene-dot rendering.
- Keyboard switching between encoders and renderers.
- Adjustable simulated grid resolution.
- Adjustable phosphene radius.
- On-screen FPS and latency overlay.
- Per-frame timing logs written to `outputs/logs/`.
- Timing summary generation through `src/utils/timing.py`.

## Project Goal

Build a real-time prosthetic vision simulator that converts live sensor input into low-bandwidth visual representations inspired by retinal and cortical visual prostheses.

The project is structured to grow into a research platform for comparing real-time encoding strategies under neural-interface constraints: limited resolution, latency, contrast loss, edge preservation, depth cues, phosphene rendering, noise, dropout, and task-specific visual prioritization.

## Repository Structure

```text
.
|-- app.py                         # Main webcam simulator
|-- requirements.txt               # Python dependencies
|-- tasks.md                       # Project roadmap and version notes
|-- README.md                      # Existing timing-results README
|-- README.generated.md            # Non-destructive generated README candidate
|-- data/
|   `-- test.jpg                   # Sample still image for run_test()
|-- outputs/
|   `-- timing_summary.csv         # Summary of preliminary timing run
`-- src/
    |-- encoders/
    |   |-- basic.py               # Grayscale and pixelation baseline
    |   |-- edge_enhanced.py       # Canny, HED, and hybrid encoders
    |   |-- contrast.py            # Placeholder
    |   `-- text_priority.py       # Placeholder
    |-- models/HED/
    |   |-- deploy.prototxt
    |   `-- hed_pretrained_bsds.caffemodel
    |-- renderers/
    |   |-- phosphene.py           # Soft phosphene renderer
    |   `-- pixel_grid.py          # Placeholder
    |-- tasks/
    |   |-- object_task.py         # Placeholder
    |   `-- reading_task.py        # Placeholder
    `-- utils/
        |-- display.py             # OpenCV display helper
        |-- image_io.py            # Placeholder
        `-- timing.py              # Timing log summarizer
```

## Requirements

The project is written in Python and uses OpenCV for webcam capture, image processing, display, and DNN inference.

Install the listed dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Current `requirements.txt`:

```text
opencv-python
numpy
streamlit
pillow
torch
```

The active webcam path uses `opencv-python` and `numpy`. The repository also lists `streamlit`, `pillow`, and `torch`, but they are not currently required by the main `app.py` execution path.

## Running the Simulator

Start the live webcam demo:

```bash
python app.py
```

The app opens an OpenCV window named `Prosthetic Vision Simulator`. It writes timing logs into `outputs/logs/`, which is ignored by git.

If the webcam cannot open, confirm that the machine has a camera available and that the terminal or Python process has camera permission.

## Controls

| Key | Action |
|---|---|
| `1` | Grayscale pixelated mode |
| `2` | Canny edge mode |
| `3` | HED learned edge mode |
| `4` | Hybrid HED + grayscale mode |
| `p` | Pixel renderer |
| `o` | Phosphene renderer |
| `+` / `=` | Increase grid size |
| `-` | Decrease grid size |
| `[` | Decrease phosphene radius |
| `]` | Increase phosphene radius |
| `q` | Quit |

## Processing Pipeline

The active webcam loop follows this structure:

```text
camera frame -> encoder -> renderer -> display/logging
```

Encoders reduce or transform the camera frame into a prosthetic-vision representation:

- `basic`: Converts the frame to grayscale, downsamples it to a square grid, then upsamples with nearest-neighbor interpolation.
- `edge_enhanced`: Applies grayscale conversion, Gaussian blur, Canny edge detection, thresholding, and pixelation.
- `hed`: Runs HED learned edge detection through OpenCV DNN using the local Caffe files.
- `hybrid`: Blends grayscale pixelation with HED output using 45% grayscale and 55% HED.

Renderers control how the encoded signal is displayed:

- `pixel`: Displays the encoded image as a square pixel-grid representation.
- `phosphene`: Resamples the encoded image to grid positions and renders each active channel as a blurred circular light blob.

## HED Model

The HED encoder uses the model files in `src/models/HED/`:

```text
src/models/HED/deploy.prototxt
src/models/HED/hed_pretrained_bsds.caffemodel
```

`src/encoders/edge_enhanced.py` registers a custom OpenCV DNN `Crop` layer to support the HED Caffe network and lazily loads the model once. This avoids reloading the network inside the webcam frame loop.

## Timing and Logging

During a webcam run, `app.py` records one CSV row per frame with:

- `timestamp_seconds`
- `mode`
- `renderer`
- `grid_size`
- `phosphene_radius`
- `loop_fps`
- `loop_ms`
- `capture_ms`
- `encode_ms`
- `display_ms`

Logs are saved to:

```text
outputs/logs/timing_YYYYMMDD_HHMMSS.csv
```

Summarize logs with:

```bash
python -m src.utils.timing
```

To summarize specific CSV files:

```bash
python -m src.utils.timing outputs/logs/timing_20260509_180751.csv
```

By default, the summary is written to:

```text
outputs/timing_summary.csv
```

## Preliminary Timing Results

A 423-frame timing run compared four real-time encoding modes.

| Mode | Frames | Mean FPS | Mean Encoder Latency | Mean Loop Time |
|---|---:|---:|---:|---:|
| Grayscale | 116 | 29.8 | 0.7 ms | 35.6 ms |
| Canny Edge | 136 | 28.8 | 9.1 ms | 36.0 ms |
| HED Edge | 63 | 9.7 | 68.6 ms | 105.3 ms |
| Hybrid HED + Gray | 108 | 9.9 | 66.5 ms | 102.0 ms |

These early results show a clear real-time tradeoff: grayscale and Canny modes maintain near-webcam-rate performance, while learned HED-based modes provide richer structural encoding at the cost of higher latency.

The tracked `outputs/timing_summary.csv` also includes capture and display timing:

| Mode | Mean Capture | Mean Display |
|---|---:|---:|
| Grayscale | 13.1 ms | 21.3 ms |
| Canny Edge | 8.3 ms | 18.2 ms |
| HED Edge | 17.8 ms | 18.4 ms |
| Hybrid HED + Gray | 16.6 ms | 18.3 ms |

## Current Roadmap

`tasks.md` describes the project direction in versioned stages:

- `v0.3`: Working baseline with webcam input, grayscale, Canny, HED, overlay metrics, mode switching, and adjustable grid resolution.
- `v0.4`: Hybrid grayscale + HED encoder.
- `v0.5`: Capture, encode, display, and full-loop timing breakdown.
- `v0.6`: Biologically inspired phosphene renderer.
- `v0.7`: Renderer switching independent of encoder selection.
- `v0.8`: Simulation parameters such as brightness scale, dropout rate, noise level, contrast limit, and field of view.
- `v0.9`: CSV logging and analysis workflow.

The code already includes much of the `v0.4` through `v0.7` functionality and partial `v0.9` logging. `v0.8` simulation parameters remain mostly future work.

## Known Gaps and Next Steps

- Move CSV logging setup into `src/utils/` to match the roadmap.
- Implement `src/renderers/pixel_grid.py` as an explicit renderer module instead of relying on pass-through behavior in `app.py`.
- Add brightness scaling, dropout, noise, contrast-limit, and field-of-view simulation parameters.
- Add CLI flags or configuration for camera index, default encoder, renderer, grid size, and logging behavior.
- Add automated tests for encoder output shape, grid-size validation, HED model loading failure paths, and timing-summary parsing.
- Decide whether `streamlit`, `pillow`, and `torch` are future dependencies or should be removed from `requirements.txt`.

## Development Notes

- Grayscale mode is the low-latency baseline and should remain fast.
- Canny mode is a fast classical edge baseline.
- HED mode is a slower learned-edge encoder that can produce more meaningful object boundaries.
- Hybrid mode should preserve more scene context than pure HED while emphasizing stronger boundaries than pure grayscale.
- HED should remain one encoder option, not the entire project focus.
