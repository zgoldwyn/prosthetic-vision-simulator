from pathlib import Path

import cv2
import numpy as np
HED_INPUT_SIZE = (256, 192)
_HED_NET = None

def edge_enhanced_image(image: np.ndarray, grid_size: int = 64) -> np.ndarray:
    """
    Edge-enhanced mode with white edges on a black background.
    """
    if grid_size < 1:
        raise ValueError("grid_size must be at least 1")

    height, width = image.shape[:2]

    # Detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)

    # Threshold edges to pure white
    _, white_edges = cv2.threshold(edges, 1, 255, cv2.THRESH_BINARY)

    # Pixelation
    small = cv2.resize(white_edges, (grid_size, grid_size), interpolation=cv2.INTER_AREA)
    pixelated = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)

    return pixelated


def get_hed_net():
    """
    Lazily loads the HED Caffe model once and reuses it for every frame.
    Loading the model inside the webcam loop causes very high latency.
    """
    global _HED_NET

    if _HED_NET is None:
        model_dir = Path(__file__).resolve().parents[1] / "models" / "HED"
        prototxt_path = model_dir / "deploy.prototxt"
        weights_path = model_dir / "hed_pretrained_bsds.caffemodel"

        if not prototxt_path.exists():
            raise FileNotFoundError(f"Missing HED prototxt file: {prototxt_path}")

        if not weights_path.exists():
            raise FileNotFoundError(f"Missing HED weights file: {weights_path}")

        _HED_NET = cv2.dnn.readNetFromCaffe(str(prototxt_path), str(weights_path))

    return _HED_NET


def hed_edge_detection(image: np.ndarray, grid_size: int = 64) -> np.ndarray:
    """
    Learned edge detection using the HED Caffe model.

    This is slower than Canny but can produce more meaningful object boundaries.
    The model is loaded once through get_hed_net() and reused across frames.
    """
    if grid_size < 1:
        raise ValueError("grid_size must be at least 1")

    height, width = image.shape[:2]
    hed_net = get_hed_net()

    small_image = cv2.resize(image, HED_INPUT_SIZE, interpolation=cv2.INTER_AREA)

    blob = cv2.dnn.blobFromImage(
        small_image,
        scalefactor=1.0,
        size=HED_INPUT_SIZE,
        mean=(78.4263377603, 87.7689143711, 114.895888225),
        swapRB=False,
        crop=False,
    )

    hed_net.setInput(blob)
    hed_edges = hed_net.forward()[0, 0]

    hed_edges = cv2.resize(hed_edges, (width, height), interpolation=cv2.INTER_LINEAR)
    hed_edges = np.clip(hed_edges * 255.0, 0, 255).astype(np.uint8)

    small = cv2.resize(hed_edges, (grid_size, grid_size), interpolation=cv2.INTER_AREA)
    pixelated = cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)

    return pixelated

