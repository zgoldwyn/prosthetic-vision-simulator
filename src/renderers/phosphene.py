import cv2
import numpy as np


def render_phosphene_grid(
        encoded_image: np.ndarray,
        grid_size: int,
        output_width: int,
        output_height: int,
        phosphene_radius: int = 8,
) -> np.ndarray:
    """
    Render an encoded grayscale image as a simulated phosphene display.

    This approximates low-channel prosthetic vision by converting the image
    into a grid of soft circular light blobs instead of square pixels.

    Args:
        encoded_image: Grayscale or BGR encoded image.
        grid_size: Number of phosphene positions across width and height.
        output_width: Width of final rendered output.
        output_height: Height of final rendered output.
        phosphene_radius: Radius of each phosphene blob in pixels.

    Returns:
        Grayscale phosphene-rendered image.
    """
    if grid_size < 1:
        raise ValueError("grid_size must be at least 1")

    if phosphene_radius < 1:
        raise ValueError("phosphene_radius must be at least 1")

    if len(encoded_image.shape) == 3:
        gray = cv2.cvtColor(encoded_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = encoded_image

    low_res = cv2.resize(
        gray,
        (grid_size, grid_size),
        interpolation=cv2.INTER_AREA,
    )

    canvas = np.zeros((output_height, output_width), dtype=np.float32)

    cell_width = output_width / grid_size
    cell_height = output_height / grid_size

    for row in range(grid_size):
        for col in range(grid_size):
            brightness = low_res[row, col] / 255.0

            if brightness <= 0:
                continue

            center_x = int((col + 0.5) * cell_width)
            center_y = int((row + 0.5) * cell_height)

            cv2.circle(
                canvas,
                (center_x, center_y),
                phosphene_radius,
                float(brightness),
                thickness=-1,
                lineType=cv2.LINE_AA,
            )

    blur_size = phosphene_radius * 2 + 1
    if blur_size % 2 == 0:
        blur_size += 1

    canvas = cv2.GaussianBlur(
        canvas,
        (blur_size, blur_size),
        sigmaX=phosphene_radius / 2,
        sigmaY=phosphene_radius / 2,
    )

    max_value = canvas.max()
    if max_value > 0:
        canvas = canvas / max_value

    rendered = np.clip(canvas * 255, 0, 255).astype(np.uint8)

    return rendered