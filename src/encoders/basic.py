import cv2
import numpy as np


def grayscale_image(image: np.ndarray) -> np.ndarray:
    """
    Converts a BGR OpenCV image to grayscale.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def pixelate_image(image: np.ndarray, grid_size: int = 32) -> np.ndarray:
    """
    Simulates low-resolution prosthetic vision by converting the image
    to grayscale, shrinking it, and scaling it back up.

    Higher grid_size = more detail.
    Lower grid_size = more pixelated.
    """
    gray = grayscale_image(image)

    height, width = gray.shape[:2]


    small = cv2.resize(gray, (grid_size, grid_size), interpolation=cv2.INTER_LINEAR)
    pixelated = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)

    return pixelated