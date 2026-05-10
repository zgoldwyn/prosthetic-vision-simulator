## Preliminary Timing Results

A 423-frame timing run compared four real-time encoding modes.

| Mode | Frames | Mean FPS | Mean Encoder Latency | Mean Loop Time |
|---|---:|---:|---:|---:|
| Grayscale | 116 | 29.8 | 0.7 ms | 35.6 ms |
| Canny Edge | 136 | 28.8 | 9.1 ms | 36.0 ms |
| HED Edge | 63 | 9.7 | 68.6 ms | 105.3 ms |
| Hybrid HED + Gray | 108 | 9.9 | 66.5 ms | 102.0 ms |

These early results show a clear real-time tradeoff: grayscale and Canny modes maintain near-webcam-rate performance, while learned HED-based modes provide richer structural encoding at the cost of higher latency.