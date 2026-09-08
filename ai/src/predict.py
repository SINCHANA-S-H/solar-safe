"""
predict.py
----------
Predict fault type for a single thermal solar panel image.
Usage:
  python ai/src/predict.py --image path/to/image.jpg
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import sys
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path

from config import BEST_MODEL_PATH, CLASS_NAMES
from preprocessing import ImagePreprocessor


def load_solar_model():
    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at: {BEST_MODEL_PATH}")
    return tf.keras.models.load_model(BEST_MODEL_PATH)


def predict_image(image_path, model=None):
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found at: {img_path}")

    if model is None:
        model = load_solar_model()

    # Preprocess image to shape (224, 224, 3) in float32 [0, 255]
    img_array = ImagePreprocessor.preprocess(img_path)

    # Add batch dimension -> (1, 224, 224, 3)
    batch_array = ImagePreprocessor.prepare_batch(img_array)

    # Prediction (model handles MobileNetV2 preprocess_input internally)
    predictions = model.predict(batch_array, verbose=0)[0]

    predicted_index = int(np.argmax(predictions))
    predicted_class = CLASS_NAMES[predicted_index]
    confidence = float(predictions[predicted_index] * 100)

    print("\n" + "=" * 50)
    print("SOLARSAFE AI — PREDICTION REPORT")
    print("=" * 50)
    print(f"Image Path  : {img_path.resolve()}")
    print(f"Prediction  : {predicted_class}")
    print(f"Confidence  : {confidence:.2f}%\n")

    print("All Class Probabilities:")
    print("-" * 50)
    ranking = sorted(zip(CLASS_NAMES, predictions), key=lambda x: x[1], reverse=True)
    for cls, score in ranking:
        print(f"  {cls:<15} : {score * 100:>6.2f}%")
    print("=" * 50 + "\n")

    return {
        "image_path": str(img_path),
        "predicted_class": predicted_class,
        "confidence": confidence,
        "probabilities": {cls: float(score) for cls, score in zip(CLASS_NAMES, predictions)}
    }


def main():
    parser = argparse.ArgumentParser(description="SolarSafe AI - Single Image Fault Prediction")
    parser.add_argument("--image", type=str, help="Path to input thermal image")
    args = parser.parse_args()

    image_path = args.image
    if not image_path:
        image_path = input("Enter thermal image path: ").strip().strip('"')

    if not image_path:
        print("Error: No image path provided.")
        sys.exit(1)

    predict_image(image_path)


if __name__ == "__main__":
    main()