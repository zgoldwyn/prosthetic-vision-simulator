# Prosthetic Vision Simulator — Tasks

## Project Goal

Build a real-time prosthetic vision simulator that converts live sensor input into low-bandwidth visual representations inspired by retinal and cortical visual prostheses.

The project should grow into a research platform for comparing how different real-time encoding strategies perform under neural-interface constraints: limited resolution, latency, contrast loss, edge preservation, depth cues, phosphene rendering, noise, dropout, and task-specific visual prioritization.

---

# Current Version

## v0.3 — Working Baseline

Current completed features:

- Real-time webcam input
- Grayscale pixelated prosthetic vision mode
- Canny edge mode
- HED learned edge detection mode
- Local HED Caffe model integration
- HED CropLayer fix
- HED spatial alignment with other modes
- FPS / latency overlay
- Keyboard mode switching
- Adjustable simulated grid resolution

Current controls:

| Key | Action |
|---|---|
| `1` | Grayscale pixelated mode |
| `2` | Canny edge mode |
| `3` | HED learned edge mode |
| `+` / `=` | Increase grid size |
| `-` | Decrease grid size |
| `q` | Quit |

Current notes:

- Grayscale mode is the baseline and should remain fast.
- Canny mode is a fast classical edge baseline.
- HED mode is a learned-edge encoder and is slower, but it produces more meaningful object boundaries.
- HED should remain one encoder option, not the entire project focus.

---

# v0.4 — Hybrid Grayscale + HED Encoder

## Goal

Add a hybrid visual encoding mode that blends raw grayscale prosthetic vision with HED learned edges.

This mode should preserve overall scene structure while emphasizing object boundaries.

## Why this matters

Pure grayscale preserves brightness and spatial context but can lose important object boundaries at low resolution. Pure HED preserves boundaries but loses smooth context, brightness, and scene structure. Hybrid mode should test whether combining both creates a more useful low-bandwidth prosthetic-vision representation.

## Tasks

- Add a hybrid encoder function in `src/encoders/edge_enhanced.py`.
- Blend grayscale pixelation with HED edge output.
- Start with an approximate blend of 45% grayscale and 55% HED.
- Add a fourth mode to `app.py`.
- Add key `4` for hybrid mode.
- Update the mode overlay to show `Hybrid HED + Gray`.
- Update the controls overlay to include `4=Hybrid`.
- Confirm that hybrid mode is spatially aligned with grayscale and HED.
- Compare hybrid mode visually against grayscale and HED.
- Commit and tag as `v0.4` once stable.

## Success criteria

- Pressing `4` switches to hybrid mode.
- Hybrid mode preserves more scene context than pure HED.
- Hybrid mode preserves stronger boundaries than pure grayscale.
- Latency is close to HED mode.
- Existing modes still work.

---

# v0.5 — Timing Breakdown

## Goal

Turn the app into a stronger real-time systems project by separating performance timing into capture, encode, display, and full-loop measurements.

## Metrics

| Metric | Meaning |
|---|---|
| `capture_ms` | Time spent reading from webcam |
| `encode_ms` | Time spent running the selected encoder |
| `display_ms` | Time spent displaying frame and processing key input |
| `loop_ms` | Full loop time |
| `loop_fps` | Actual user-experienced FPS |

## Tasks

- Measure webcam capture time.
- Measure encoder processing time.
- Measure display / `waitKey` time.
- Measure full-loop time.
- Show simplified performance metrics in the window overlay.
- Print a detailed timing breakdown to the terminal.
- Compare timing across grayscale, Canny, HED, and hybrid modes.
- Keep the overlay readable and not too crowded.

## Success criteria

- Each mode reports actual loop FPS.
- Each mode reports encoder latency.
- HED and hybrid performance can be compared quantitatively.
- Timing output helps identify whether the bottleneck is capture, encoding, or display.

---

# v0.6 — Phosphene Renderer

## Goal

Move beyond square pixel blocks and add a more biologically inspired prosthetic-vision renderer using soft phosphene dots.

## Why this matters

Real visual prosthesis users do not usually perceive clean square pixels. They often perceive dots, blobs, streaks, flashes, or distorted light patterns. A phosphene renderer makes the simulator more research-relevant.

## Tasks

- Create a renderer module under `src/renderers/`.
- Add a phosphene renderer that converts a low-resolution image into soft circular or Gaussian blobs.
- Keep the current square-pixel rendering as a baseline renderer.
- Separate the project architecture into encoder and renderer stages.
- Preserve compatibility with all current encoders.
- Add adjustable phosphene radius.
- Add adjustable brightness scaling.
- Prepare for later dropout and noise parameters.

## Success criteria

- The same encoder output can be shown as either square pixels or phosphene dots.
- Phosphene rendering works in real time for grayscale mode.
- Phosphene rendering works acceptably for HED and hybrid modes.
- The visual output looks more like a low-channel neural display than a normal pixelation filter.

---

# v0.7 — Renderer Switching

## Goal

Allow the user to switch between pixel-grid rendering and phosphene rendering independently of the selected encoder.

## Architecture target

```text
camera frame
→ encoder
→ renderer
→ display
```

## Tasks

- Add a renderer state variable.
- Add keyboard controls for renderer switching.
- Keep encoder controls independent from renderer controls.
- Show both current encoder and current renderer in the overlay.
- Support combinations such as:
  - grayscale + pixel grid
  - grayscale + phosphene
  - HED + pixel grid
  - HED + phosphene
  - hybrid + phosphene

## Success criteria

- Encoder and renderer are separate concepts in the code.
- Switching renderers does not change the selected encoder.
- The overlay clearly shows both mode types.
- Renderer switching does not break FPS/latency reporting.

---

# v0.8 — Simulation Parameters

## Goal

Add adjustable parameters that make the simulated prosthetic vision more realistic and experimentally useful.

## Parameters

| Parameter | Meaning |
|---|---|
| `grid_size` | Simulated number of visual channels |
| `phosphene_radius` | Size of each perceived light blob |
| `brightness_scale` | Overall stimulation/perceived brightness |
| `dropout_rate` | Fraction of missing/dead channels |
| `noise_level` | Random visual/electrical noise |
| `contrast_limit` | Reduced contrast sensitivity |
| `field_of_view` | Visible region of the prosthetic display |

## Tasks

- Add parameter variables with clear defaults.
- Add keyboard controls only for the most useful parameters.
- Keep advanced parameters documented even if not all are interactive at first.
- Make parameter changes visible in the overlay or terminal.
- Ensure parameters work consistently across encoders/renderers.

## Success criteria

- The simulator can model different prosthetic-vision conditions.
- Parameters can be used later in user studies.
- Parameter values are easy to log and reproduce.

---

# v0.9 — CSV Logging

## Goal

Log real-time performance and mode settings to CSV so results can be analyzed later.

## Log location

```text
outputs/logs/
```

## Suggested CSV columns

| Column | Meaning |
|---|---|
| `timestamp` | Current time |
| `encoder` | grayscale, Canny, HED, hybrid |
| `renderer` | pixel grid, phosphene |
| `grid_size` | Simulated resolution |
| `fps` | Actual loop FPS |
| `capture_ms` | Webcam capture time |
| `encode_ms` | Encoder latency |
| `display_ms` | Display time |
| `loop_ms` | Full loop time |
| `phosphene_radius` | Current phosphene radius, if applicable |
| `dropout_rate` | Current dropout rate, if applicable |
| `noise_level` | Current noise level, if applicable |

## Tasks

- Create a logging utility under `src/utils/`.
- Create a new CSV file per run.
- Log one row per frame or one row every N frames.
- Avoid logging so aggressively that it hurts FPS.
- Add a flag or key to enable/disable logging if needed.
- Make sure logs are ignored or managed appropriately if they become large.

## Success criteria

- A run produces a usable CSV file.
- CSV rows include mode, renderer, grid size, FPS, and latency.
- Logs can be loaded later for plotting.

---

# v1.0 — First Evaluation Task

## Goal

Add a simple user task so the project can measure whether one encoding strategy is actually more useful than another.

## First recommended task

Object identification under simulated prosthetic vision.

## Possible tasks

| Task | Measurement |
|---|---|
| Object recognition | Accuracy and response time |
| Reading short text | Accuracy and response time |
| Direction choice | Correct left/right/up/down response |
| Find object in scene | Time to response |
| Detect obstacle | Hit/miss and response time |

## Tasks

- Create a task module under `src/tasks/`.
- Start with a simple object-recognition or reading task.
- Show the user a simulated prosthetic view.
- Capture keyboard responses.
- Record response time and correctness.
- Log encoder, renderer, grid size, and trial result.
- Keep the first task simple enough to test quickly.

## Success criteria

- The simulator can run at least one structured task.
- Results are saved in a format that can be analyzed.
- Different modes can be compared on accuracy and response time.

---

# v1.1 — Depth-Aware Encoding Exploration

## Goal

Explore adding depth information as an additional cue for prosthetic vision encoding.

## Motivation

Depth sensing could help a low-bandwidth neural visual interface prioritize the most important parts of a scene: nearby obstacles, walkable space, doorways, people, and objects.

An Xbox Kinect-style system uses depth sensing to convert the world into a structured representation. An iPhone LiDAR sensor can potentially support a similar direction for this project.

## Possible input sources

| Source | Use |
|---|---|
| iPhone LiDAR | Real depth capture or exported depth data |
| RGB-D datasets | Offline development and testing |
| Monocular depth estimation | Depth prediction from normal webcam frames |
| Segmentation models | Approximate object/person/background priority |
| Kinect / RealSense later | Dedicated depth-camera pipeline |

## Depth-aware modes to explore

| Mode | Purpose |
|---|---|
| Near-obstacle priority | Brighten or outline close objects |
| Walkable-space mode | Highlight open paths and suppress background |
| Person-aware mode | Prioritize human bodies/faces |
| Doorway/path mode | Highlight navigation-relevant structure |
| Depth-edge mode | Use depth discontinuities instead of RGB edges |

## Tasks

- Research practical ways to access iPhone LiDAR depth data.
- Determine whether real-time iPhone LiDAR streaming is feasible.
- If real-time streaming is difficult, start with exported RGB-D images/videos.
- Add a depth-aware encoder prototype using prerecorded data first.
- Compare RGB-edge encoding with depth-edge encoding.
- Evaluate whether depth cues are more useful than visual edges for navigation-like tasks.

## Success criteria

- The project has a clear path for incorporating depth data.
- At least one depth-aware encoding mode is prototyped.
- Depth-aware encoding can be compared against grayscale, HED, and hybrid modes.

---

# v1.2 — Text-Priority Mode

## Goal

Add a mode that prioritizes reading text, signs, labels, or high-contrast characters.

## Motivation

Reading is one of the most important functional goals for retinal prostheses. A prosthetic-vision system should not necessarily send raw video; it may need to detect and enhance text regions.

## Tasks

- Add a text-priority encoder.
- Start with simple high-contrast text detection or OCR later.
- Highlight or enlarge detected text regions before low-resolution rendering.
- Compare text-priority mode against grayscale and hybrid mode on reading tasks.

## Success criteria

- Text-priority mode improves readability in at least simple test scenes.
- Text-related task results can be logged and compared.

---

# v1.3 — Navigation-Priority Mode

## Goal

Add a mode optimized for movement/navigation rather than object detail.

## Motivation

A low-channel visual prosthesis may be more useful if it highlights paths, obstacles, and environmental layout instead of trying to show the full scene.

## Tasks

- Prototype a navigation-oriented encoder.
- Use depth, segmentation, edges, or simple heuristics.
- Highlight walkable regions, doorways, obstacles, and nearby hazards.
- Compare against grayscale/HED/hybrid modes on simple navigation-style tasks.

## Success criteria

- Navigation mode presents less clutter than raw visual modes.
- Nearby obstacles or paths are visually emphasized.
- The mode is ready for a simple experimental comparison.

---

# Research Framing

## Core research question

> Which real-time visual encoding strategy produces the most useful low-bandwidth representation for simulated retinal or cortical prosthetic vision?

## Current encoder categories

| Encoder | Type | Purpose |
|---|---|---|
| Grayscale | Baseline | Preserve brightness and scene layout |
| Canny | Classical computer vision | Fast edge-only baseline |
| HED | Learned edge detection | More meaningful object boundaries |
| Hybrid | Combined encoding | Preserve scene layout and learned boundaries |

## Future encoder categories

| Encoder | Purpose |
|---|---|
| Contrast-enhanced | Improve low-contrast visibility |
| Text-priority | Prioritize reading signs/labels |
| Object-priority | Highlight important objects |
| Navigation-priority | Highlight paths, doors, and obstacles |
| Depth-aware | Use distance and scene geometry |
| Face/person-priority | Preserve human/social cues |

## Key system tradeoffs

| Tradeoff | Why it matters |
|---|---|
| Accuracy vs latency | Better encoders may be too slow for real-time use |
| Detail vs simplicity | Too much detail can clutter low-channel displays |
| Edges vs brightness | Edge-only modes lose context; grayscale loses boundaries |
| RGB vs depth | Color/brightness may be less useful than distance for navigation |
| Pixel grid vs phosphene rendering | Square pixels are easy but biologically unrealistic |
| General-purpose vs task-specific encoding | The best encoding may depend on the task |

---

# Development Rules

## Keep commits small

Each commit should represent one working milestone.

Good commit messages:

```bash
git commit -m "add hybrid grayscale and HED encoder mode"
git commit -m "add timing breakdown for encoder modes"
git commit -m "add phosphene renderer prototype"
git commit -m "add depth-aware encoder prototype"
```

Avoid vague commits:

```bash
git commit -m "stuff"
git commit -m "updates"
```

---

## Preserve working states

Before risky changes:

```bash
git status
git add -A
git commit -m "save working state before experimenting with <feature>"
```

---

## Keep HED in perspective

HED is one encoder mode. It is useful because it gives learned object boundaries, but the broader project is about comparing real-time neural visual encoding strategies.

The project should not become only about making HED perfect.

---

## Keep the architecture modular

Target architecture:

```text
input source
→ encoder
→ renderer
→ display
→ task/logging
```

Each part should be replaceable:

| Layer | Examples |
|---|---|
| Input | webcam, image, video, RGB-D, iPhone LiDAR |
| Encoder | grayscale, Canny, HED, hybrid, depth-aware, text-priority |
| Renderer | pixel grid, phosphene, noisy phosphene |
| Task | reading, object recognition, navigation |
| Logging | FPS, latency, accuracy, response time |

---

# Next Action

Start v0.4:

1. Add the hybrid grayscale + HED encoder.
2. Add key `4` for hybrid mode.
3. Verify all four modes still work.
4. Compare hybrid visually against grayscale and HED.
5. Commit and tag as `v0.4`.

