import cv2
import numpy as np


def show_image(title: str, image: np.ndarray) -> None:
    """
    Opens an OpenCV window and displays an image until the user presses any key.
    """
    cv2.imshow(title, image)

    cv2.waitKey(0)
    cv2.destroyAllWindows()