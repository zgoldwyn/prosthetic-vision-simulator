import cv2

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
    while True:

        success, frame = webcam.read()
        if not success:
            print("Could not read frame")
            break
        start_time = cv2.getTickCount()
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

        end_time = cv2.getTickCount()
        processing_time = (end_time - start_time) / cv2.getTickFrequency()
        latency_ms = processing_time * 1000
        fps = 1 / processing_time

        current_time = cv2.getTickCount()
        frame_time = (current_time - previous_frame_time) / cv2.getTickFrequency()
        previous_frame_time = current_time
        loop_fps = 1 / frame_time



        mode_display = {
            'basic': 'Grayscale',
            'edge_enhanced': 'Canny Edge',
            'hed': 'HED Edge',
            'hybrid': 'Hybrid HED + Gray',
        }.get(mode, mode)
        cv2.putText(
            pixelated,
            f"FPS: {loop_fps:.1f} | Latency: {latency_ms:.1f} ms | Grid: {grid_size}x{grid_size} | Mode: {mode_display}",
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )



        cv2.imshow("Grayscale Pixelated Prosthetic Vision", pixelated)


        key = cv2.waitKey(1) & 0xFF
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
        if key == ord("q"):
            break
    webcam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
