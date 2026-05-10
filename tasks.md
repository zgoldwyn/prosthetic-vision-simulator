# Prosthetic Vision Simulator — Development Tasks

## Project Goal

Build a real-time prosthetic vision simulator that transforms live camera input into low-bandwidth visual encodings inspired by retinal and cortical visual prostheses.

The simulator should become a platform for comparing different real-time encoding strategies under neural-interface constraints such as limited resolution, latency, edge preservation, contrast loss, phosphene rendering, noise, and electrode dropout.

---

# Current Version

## v0.3 — Current Milestone

Completed:

- Real-time webcam input
- Grayscale pixelated prosthetic vision mode
- Canny edge mode
- HED learned edge detection mode
- HED Caffe model integrated locally
- HED CropLayer fixed
- HED now spatially aligns with the other modes
- FPS / latency overlay
- Keyboard mode switching

Current controls:

| Key | Action |
|---|---|
| `1` | Grayscale pixelated mode |
| `2` | Canny edge mode |
| `3` | HED learned edge mode |
| `+` / `=` | Increase grid size |
| `-` | Decrease grid size |
| `q` | Quit |

Current known performance:

- Grayscale mode: real-time webcam FPS, very low latency
- HED mode: slower, around ~10 FPS and ~60 ms encode latency, but usable as an experimental learned-edge encoder

---

# Immediate Next Goal

## v0.4 — Hybrid Grayscale + HED Mode

### Goal

Add a fourth mode that combines raw grayscale prosthetic vision with HED learned edges.

The purpose is to preserve overall scene structure while also emphasizing object boundaries.

Pure HED loses brightness/context. Pure grayscale loses strong object boundaries. Hybrid mode should test whether combining them creates a more useful prosthetic-vision representation.

### New control

| Key | Mode |
|---|---|
| `4` | Hybrid grayscale + HED |

---

## Step 1 — Create a hybrid encoder function

File:

```text
src/encoders/edge_enhanced.py
```

Add a new function:

```python
def hybrid_hed_grayscale(image: np.ndarray, grid_size: int = 64) -> np.ndarray:
    ...
```

Concept:

```text
original image
→ grayscale pixelated image
→ HED edge pixelated image
→ blend them together
→ return hybrid output
```

Expected blend:

```python
hybrid = cv2.addWeighted(gray_pixelated, 0.45, hed_pixelated, 0.55, 0)
```

Potential weights to test later:

| Grayscale weight | HED weight | Expected result |
|---:|---:|---|
| 0.70 | 0.30 | More natural scene structure |
| 0.50 | 0.50 | Balanced |
| 0.30 | 0.70 | Stronger edges |
| 0.20 | 0.80 | Mostly HED |

Start with:

```text
45% grayscale, 55% HED
```

---

## Step 2 — Wire hybrid mode into `app.py`

File:

```text
app.py
```

Update imports:

```python
from src.encoders.edge_enhanced import edge_enhanced_image, hed_edge_detection, hybrid_hed_grayscale
```

In the mode-selection block, add:

```python
elif mode == 'hybrid':
    pixelated = hybrid_hed_grayscale(frame, grid_size)
```

In the key controls, add:

```python
if key == ord("4"):
    mode = 'hybrid'
```

Update the overlay display logic so hybrid mode appears as:

```text
Hybrid HED + Gray
```

Update the controls text:

```text
1=Gray  2=Canny  3=HED  4=Hybrid  +/-=Grid  q=Quit
```

---

## Step 3 — Test v0.4 manually

Run:

```bash
python app.py
```

Test:

- Press `1`: grayscale mode works
- Press `2`: Canny mode works
- Press `3`: HED mode works
- Press `4`: hybrid mode works
- Press `+`: grid size increases
- Press `-`: grid size decreases
- Press `q`: app exits cleanly

Observe:

- Does hybrid mode preserve face/body/wall structure better than pure HED?
- Does hybrid mode preserve boundaries better than grayscale?
- Is latency close to HED mode?
- Is the output spatially aligned?

---

## Step 4 — Commit v0.4

Once working:

```bash
git status
git add app.py src/encoders/edge_enhanced.py
git commit -m "add hybrid grayscale and HED encoder mode"
git push
```

Optional version tag:

```bash
git tag -a v0.4 -m "v0.4: add hybrid grayscale and HED encoder mode"
git push origin v0.4
```

---

# Next Milestones

## v0.5 — Timing Breakdown

### Goal

Separate timing into:

| Metric | Meaning |
|---|---|
| `capture_ms` | Webcam frame capture time |
| `encode_ms` | Encoder processing time |
| `display_ms` | Display and waitKey time |
| `loop_ms` | Full loop time |
| `loop_fps` | Actual user-experienced FPS |

### Why

This turns the project into a stronger real-time systems project.

Instead of saying:

```text
HED feels slow.
```

We can say:

```text
HED mode runs at X FPS with Y ms encode latency, while grayscale runs at A FPS with B ms encode latency.
```

### Tasks

- Add capture timing around `webcam.read()`
- Add encode timing around encoder selection
- Add display timing around `imshow()` and `waitKey()`
- Print timing breakdown to terminal
- Show simplified timing overlay in the window

Commit:

```bash
git commit -m "add timing breakdown for real time encoder modes"
```

---

## v0.6 — Phosphene Renderer

### Goal

Move beyond square pixel blocks and simulate prosthetic vision more realistically using phosphene dots.

Current rendering:

```text
low-resolution square blocks
```

Target rendering:

```text
soft circular / Gaussian blobs
```

### New folder

```text
src/renderers/
```

### New file

```text
src/renderers/phosphene.py
```

### Function idea

```python
def render_phosphene_grid(low_res_image: np.ndarray, output_size: tuple[int, int]) -> np.ndarray:
    ...
```

### Parameters to support later

| Parameter | Meaning |
|---|---|
| `phosphene_radius` | Blob size |
| `brightness_scale` | Brightness intensity |
| `dropout_rate` | Missing/dead electrodes |
| `noise_level` | Random perceptual/electrical noise |
| `field_of_view` | How much of the image is visible |

### Why

Real visual prosthesis users do not see neat square pixels. They often perceive dots, blobs, streaks, or phosphenes. This makes the simulator more research-accurate.

Commit:

```bash
git commit -m "add phosphene renderer prototype"
```

---

## v0.7 — Renderer Mode Switching

### Goal

Allow switching between square-pixel rendering and phosphene rendering.

Controls:

| Key | Renderer |
|---|---|
| `p` | Pixel grid renderer |
| `o` | Phosphene renderer |

Modes should be independent from encoders.

Example:

```text
Encoder: HED
Renderer: phosphene
```

or:

```text
Encoder: grayscale
Renderer: pixel grid
```

This creates the architecture:

```text
camera frame
→ encoder
→ renderer
→ display
```

Commit:

```bash
git commit -m "add renderer switching"
```

---

## v0.8 — CSV Logging

### Goal

Log system and mode data for later analysis.

Create:

```text
outputs/logs/
```

Each run should save a CSV with:

| Column | Meaning |
|---|---|
| timestamp | Current time |
| mode | grayscale, Canny, HED, hybrid |
| renderer | pixel grid, phosphene |
| grid_size | Simulated resolution |
| fps | Actual loop FPS |
| encode_ms | Encoder latency |
| capture_ms | Webcam capture time |
| display_ms | Display time |
| loop_ms | Full loop time |

Commit:

```bash
git commit -m "add CSV logging for real time performance"
```

---

## v0.9 — Simple User Task Mode

### Goal

Add the first evaluation task.

Start with a basic object-identification task.

Example:

```text
Show an object under prosthetic simulation.
Ask user to press a key identifying the object.
Record mode, grid size, accuracy, and response time.
```

Possible first tasks:

| Task | Metric |
|---|---|
| Object recognition | Accuracy and response time |
| Read large text | Accuracy and response time |
| Direction choice | Correct left/right/up/down |
| Find object in scene | Time to response |

Commit:

```bash
git commit -m "add basic object recognition task"
```

---

# Research Direction

## Core research question

> Which real-time visual encoding strategy produces the most useful low-bandwidth representation for simulated retinal or cortical prosthetic vision?

## Current modes

| Mode | Type | Purpose |
|---|---|---|
| Grayscale | Baseline | Preserve brightness and scene layout |
| Canny | Classical edge detection | Fast edge-only baseline |
| HED | Learned edge detection | More meaningful object boundaries |
| Hybrid | Combined | Preserve scene layout and learned boundaries |

## Later modes

| Mode | Purpose |
|---|---|
| Contrast-enhanced | Improve low-contrast visibility |
| Text-priority | Prioritize reading signs/labels |
| Object-priority | Highlight important objects |
| Navigation-priority | Highlight paths, doors, obstacles |
| Face/person-priority | Preserve human/social cues |

---

# Development Rules

## Keep commits small

Each commit should represent one working milestone.

Good commit examples:

```bash
git commit -m "add hybrid grayscale and HED encoder mode"
git commit -m "add phosphene renderer prototype"
git commit -m "add timing breakdown for encoder modes"
```

Avoid huge vague commits like:

```bash
git commit -m "stuff"
```

---

## Preserve working states

Before experimental changes:

```bash
git status
git add -A
git commit -m "save working state before experimenting with ..."
```

---

## Do not let HED dominate the project

HED is one encoder mode, not the whole project.

The project is about:

```text
real-time neural visual encoding strategies
```

not just:

```text
getting HED perfect
```

---

# Next Action

Start v0.4:

1. Add `hybrid_hed_grayscale()` to `src/encoders/edge_enhanced.py`
2. Add mode `4` in `app.py`
3. Test visually
4. Commit
5. Tag as `v0.4`

