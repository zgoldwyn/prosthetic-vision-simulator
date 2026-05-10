import csv
import time
from pathlib import Path

import cv2

from src.renderers.phosphene import render_phosphene_grid
from src.utils.display import show_image
from src.encoders.basic import pixelate_image
from src.encoders.edge_enhanced import edge_enhanced_image, hed_edge_detection, hybrid_hed_grayscale

def main() -> None:
    run_webcam_demo()


def run_test():
    image = cv2.imread("data/test.jpg")

    if image is None:
        print("Could not find image. Put a file named test.jpg inside the data folder.")
        return

    pixelated = pixelate_image(image, grid_size=64)

    show_image("Original Image", image)
    show_image("Grayscale Pixelated Prosthetic Vision", pixelated)

def run_webcam_demo() -> None:
    webcam = cv2.VideoCapture(0)


    if not webcam.isOpened():
        print("Could not open webcam.")
        return

    previous_frame_time = cv2.getTickCount()
    grid_size = 64
    mode = 'basic'  # 'basic' for grayscale, 'edge_enhanced' for edge detection

    renderer = 'pixel'
    phosphene_radius = 8

    logs_dir = Path("outputs/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"timing_{time.strftime('%Y%m%d_%H%M%S')}.csv"

    log_file = open(log_path, "w", newline="")
    timing_writer = csv.DictWriter(
        log_file,
        fieldnames=[
            "timestamp_seconds",
            "mode",
            "renderer",
            "grid_size",
            "phosphene_radius",
            "loop_fps",
            "loop_ms",
            "capture_ms",
            "encode_ms",
            "display_ms",
        ],
    )
    timing_writer.writeheader()
    print(f"Logging timing data to {log_path}")

    try:
        while True:
            tick_frequency = cv2.getTickFrequency()
            loop_start = cv2.getTickCount()

            capture_start = cv2.getTickCount()
            success, frame = webcam.read()
            capture_end = cv2.getTickCount()

            if not success:
                print("Could not read frame")
                break

            encode_start = cv2.getTickCount()
            if mode == 'basic':
                pixelated = pixelate_image(frame, grid_size)
            elif mode == 'edge_enhanced':
                pixelated = edge_enhanced_image(frame, grid_size)
            elif mode == 'hed':
                pixelated = hed_edge_detection(frame, grid_size)
            elif mode == 'hybrid':
                pixelated = hybrid_hed_grayscale(frame, grid_size)
            else:
                pixelated = pixelate_image(frame, grid_size)
            encode_end = cv2.getTickCount()

            height, width = pixelated.shape[:2]

            if renderer == 'phosphene':
                display_image = render_phosphene_grid(
                    pixelated,
                    grid_size=grid_size,
                    output_width=width,
                    output_height=height,
                    phosphene_radius=phosphene_radius,
                )
            else:
                display_image = pixelated

            capture_ms = (capture_end - capture_start) / tick_frequency * 1000
            encode_ms = (encode_end - encode_start) / tick_frequency * 1000

            current_time = cv2.getTickCount()
            frame_time = (current_time - previous_frame_time) / tick_frequency
            previous_frame_time = current_time
            loop_fps = 1 / frame_time if frame_time > 0 else 0

            mode_display = {
                'basic': 'Grayscale',
                'edge_enhanced': 'Canny Edge',
                'hed': 'HED Edge',
                'hybrid': 'Hybrid HED + Gray',
            }.get(mode, mode)

            overlay_lines = [
                f"Mode: {mode_display} | Renderer: {renderer} | Grid: {grid_size}x{grid_size}",
                f"FPS: {loop_fps:.1f} | Encode: {encode_ms:.1f} ms | Capture: {capture_ms:.1f} ms",
                "Keys: 1=Gray  2=Canny  3=HED  4=Hybrid  p=Pixel  o=Phosphene  [/] Radius  +/-=Grid  q=Quit",
            ]

            for line_index, overlay_text in enumerate(overlay_lines):
                cv2.putText(
                    display_image,
                    overlay_text,
                    (20, 35 + line_index * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            display_start = cv2.getTickCount()
            cv2.imshow("Prosthetic Vision Simulator", display_image)
            key = cv2.waitKey(1) & 0xFF
            display_end = cv2.getTickCount()
            loop_end = cv2.getTickCount()

            display_ms = (display_end - display_start) / tick_frequency * 1000
            loop_ms = (loop_end - loop_start) / tick_frequency * 1000

            timing_writer.writerow(
                {
                    "timestamp_seconds": time.time(),
                    "mode": mode,
                    "renderer": renderer,
                    "grid_size": grid_size,
                    "phosphene_radius": phosphene_radius,
                    "loop_fps": loop_fps,
                    "loop_ms": loop_ms,
                    "capture_ms": capture_ms,
                    "encode_ms": encode_ms,
                    "display_ms": display_ms,
                }
            )

            print(
                f"mode={mode_display} | fps={loop_fps:.1f} | loop={loop_ms:.1f} ms | capture={capture_ms:.1f} ms | encode={encode_ms:.1f} ms | display={display_ms:.1f} ms",
                end="\r",
            )

            if key == ord("+") or key == ord("="):
                grid_size = min(grid_size + 4, 128)
            if key == ord("-"):
                grid_size = max(grid_size - 4, 4)
            if key == ord("1"):
                mode = 'basic'
            if key == ord("2"):
                mode = 'edge_enhanced'
            if key == ord("3"):
                mode = 'hed'
            if key == ord("4"):
                mode = 'hybrid'
            if key == ord("p"):
                renderer = 'pixel'
            if key == ord("o"):
                renderer = 'phosphene'
            if key == ord("["):
                phosphene_radius = max(phosphene_radius - 1, 1)
            if key == ord("]"):
                phosphene_radius = min(phosphene_radius + 1, 30)
            if key == ord("q"):
                break
    finally:
        log_file.close()
        print(f"\nSaved timing data to {log_path}")
        webcam.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
