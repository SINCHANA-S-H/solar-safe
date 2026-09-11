"""
test_model.py
-------------
Reusable model verification and inference test script for SolarSafe AI.

Usage:
    python test_model.py <image_path>
    python test_model.py --test-suite
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import sys
import argparse
from pathlib import Path
import numpy as np
import tensorflow as tf
from PIL import Image

# Ensure ai/src is in python path
BASE_DIR = Path(__file__).resolve().parent
AI_DIR = BASE_DIR / "ai"
SRC_DIR = AI_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import FINAL_MODEL_PATH, BEST_MODEL_PATH, TEST_DIR, CLASS_NAMES, IMG_SIZE
from preprocessing import ImagePreprocessor
from focal_loss import FocalLoss


def get_active_model_path():
    """Returns the path to the best available model."""
    # Check experiment models first if available
    exp_b = AI_DIR / "outputs" / "experiments" / "v2" / "v2_b_focal" / "best_model_v2b.keras"
    if exp_b.exists():
        return exp_b
    if FINAL_MODEL_PATH.exists():
        return FINAL_MODEL_PATH
    if BEST_MODEL_PATH.exists():
        return BEST_MODEL_PATH
    raise FileNotFoundError(f"No trained model found at {FINAL_MODEL_PATH}, {BEST_MODEL_PATH}, or {exp_b}")


def load_model(custom_path=None):
    model_path = Path(custom_path) if custom_path else get_active_model_path()
    custom_objects = {"FocalLoss": FocalLoss}
    try:
        model = tf.keras.models.load_model(model_path, compile=False, custom_objects=custom_objects)
    except Exception:
        model = tf.keras.models.load_model(model_path, compile=False)
    return model, model_path


def infer_actual_class(image_path: Path) -> str:
    """Infers ground-truth class from filename or directory structure if present."""
    path_str = str(image_path).lower()
    for cls in CLASS_NAMES:
        if cls.lower() in path_str or cls.lower().replace("_", "") in path_str:
            return cls
    return "Unknown (External Image)"


def test_single_image(image_path, model=None, model_path=None):
    img_path = Path(image_path)
    if not img_path.exists():
        print(f"Error: File not found at {img_path}")
        sys.exit(1)

    if model is None:
        model, model_path = load_model()

    # Preprocessing
    img_array = ImagePreprocessor.preprocess(img_path)
    batch_array = ImagePreprocessor.prepare_batch(img_array)

    # Prediction
    raw_preds = model.predict(batch_array, verbose=0)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred_class = CLASS_NAMES[pred_idx]
    confidence = float(raw_preds[pred_idx] * 100)

    # Class-wise probabilities
    prob_dict = {cls: float(raw_preds[i] * 100) for i, cls in enumerate(CLASS_NAMES)}

    actual_class = infer_actual_class(img_path)

    # Exact format required by STEP 15:
    print(f"Image:\n{img_path.name}\n")
    print(f"Actual class:\n{actual_class}\n")
    print(f"Prediction:\n{pred_class}\n")
    print(f"Confidence:\n{confidence:.2f}%\n")
    print(f"Normal:\n{prob_dict.get('Normal', 0.0):.2f}%\n")
    print(f"Hotspot:\n{prob_dict.get('Hotspot', 0.0):.2f}%\n")
    print(f"Cell_Crack:\n{prob_dict.get('Cell_Crack', 0.0):.2f}%")

    return {
        "image": img_path.name,
        "actual": actual_class,
        "prediction": pred_class,
        "confidence": confidence,
        "probabilities": prob_dict,
    }


def main():
    parser = argparse.ArgumentParser(description="SolarSafe AI - Model Test Script")
    parser.add_argument("image_path", nargs="?", type=str, help="Path to solar panel image")
    parser.add_argument("--model", type=str, default=None, help="Optional path to model file")
    args = parser.parse_args()

    if not args.image_path:
        print("Usage: python test_model.py <image_path>")
        sys.exit(1)

    test_single_image(args.image_path, model_path=args.model)


if __name__ == "__main__":
    main()
