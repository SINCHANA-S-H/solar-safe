"""
preprocessing.py
----------------
Image preprocessing functions for the SolarSafe AI model using PIL.
"""

import numpy as np
from PIL import Image
from typing import Union
from pathlib import Path

from config import IMG_SIZE


class ImagePreprocessor:
    """
    Handles image preprocessing before prediction or training.
    """

    @staticmethod
    def preprocess(image_path: Union[str, Path]) -> np.ndarray:
        """
        Reads and preprocesses a single image using PIL.

        Parameters:
            image_path (str or Path): Path to the image.

        Returns:
            numpy.ndarray: Processed image array with shape (224, 224, 3) in float32 [0, 255].
        """
        path_obj = Path(image_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Unable to load image: {image_path}")

        # Open image and convert to RGB
        img = Image.open(path_obj).convert("RGB")

        # Resize image to target (224, 224)
        img = img.resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)

        # Convert to numpy float32 array
        img_array = np.array(img, dtype=np.float32)

        return img_array

    @staticmethod
    def prepare_batch(image: np.ndarray) -> np.ndarray:
        """
        Adds batch dimension.

        (224,224,3) -> (1,224,224,3)
        """
        return np.expand_dims(image, axis=0)


if __name__ == "__main__":
    print("Image Preprocessor Ready")