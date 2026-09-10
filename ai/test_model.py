"""
test_model.py
-------------
Comprehensive AI Model Verification and Inference Test Script for SolarSafe.

Capabilities:
1. Single Image Prediction:
   python ai/test_model.py --image path/to/image.jpg
2. Full Test Suite Evaluation:
   python ai/test_model.py --test-suite
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import sys
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix

# Add ai/src to Python path
SRC_DIR = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SRC_DIR))

from config import FINAL_MODEL_PATH, BEST_MODEL_PATH, TEST_DIR, CLASS_NAMES, IMG_SIZE
from preprocessing import ImagePreprocessor


def load_model():
    model_path = FINAL_MODEL_PATH if FINAL_MODEL_PATH.exists() else BEST_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {FINAL_MODEL_PATH} or {BEST_MODEL_PATH}")
    print(f"[INFO] Loaded model: {model_path}")
    return tf.keras.models.load_model(model_path, compile=False)


def predict_single(image_path, model=None):
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Image not found: {img_path}")

    if model is None:
        model = load_model()

    img_array = ImagePreprocessor.preprocess(img_path)
    batch_array = ImagePreprocessor.prepare_batch(img_array)

    raw_preds = model.predict(batch_array, verbose=0)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred_class = CLASS_NAMES[pred_idx]
    confidence = float(raw_preds[pred_idx] * 100)

    print("\n" + "=" * 55)
    print("SOLARSAFE AI — PREDICTION REPORT")
    print("=" * 55)
    print(f"Image       : {img_path.name}")
    print(f"Prediction  : {pred_class}")
    print(f"Confidence  : {confidence:.2f}%\n")
    print("Class Probabilities:")
    for cls, score in zip(CLASS_NAMES, raw_preds):
        print(f"  {cls:<15}: {score:.4f} ({score * 100:.2f}%)")
    print("=" * 55 + "\n")

    return {
        "prediction": pred_class,
        "confidence": confidence,
        "probabilities": {cls: float(raw_preds[i]) for i, cls in enumerate(CLASS_NAMES)}
    }


def run_evaluation_suite(model=None, samples_per_class=10):
    if model is None:
        model = load_model()

    print("\n" + "=" * 65)
    print(f"SOLARSAFE AI — EVALUATION TEST SUITE ({samples_per_class} per class)")
    print("=" * 65)

    y_true = []
    y_pred = []
    results = []

    for class_name in CLASS_NAMES:
        class_folder = TEST_DIR / class_name
        if not class_folder.exists():
            print(f"[WARN] Test folder missing: {class_folder}")
            continue

        images = [f for f in class_folder.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")]
        selected = images[:samples_per_class]

        for img_path in selected:
            img_array = ImagePreprocessor.preprocess(img_path)
            batch_array = ImagePreprocessor.prepare_batch(img_array)
            preds = model.predict(batch_array, verbose=0)[0]
            pred_idx = int(np.argmax(preds))
            pred_cls = CLASS_NAMES[pred_idx]
            conf = float(preds[pred_idx] * 100)

            y_true.append(class_name)
            y_pred.append(pred_cls)
            status = "PASS [OK]" if pred_cls == class_name else "FAIL [X]"

            results.append({
                "file": img_path.name,
                "actual": class_name,
                "pred": pred_cls,
                "conf": conf,
                "status": status,
                "probs": preds
            })

    header = f"{'Filename':<32} | {'Actual':<12} | {'Predicted':<12} | {'Confidence':<10} | {'Status'}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['file'][:32]:<32} | {r['actual']:<12} | {r['pred']:<12} | {r['conf']:>9.2f}% | {r['status']}")
    print("-" * len(header))

    # Overall Accuracy
    correct = sum(1 for r in results if r["actual"] == r["pred"])
    total = len(results)
    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"\nTest Suite Accuracy: {correct}/{total} ({accuracy:.2f}%)\n")

    # Classification Report
    print("=" * 65)
    print("CLASSIFICATION REPORT")
    print("=" * 65)
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=4))

    # Confusion Matrix
    print("=" * 65)
    print("CONFUSION MATRIX")
    print("=" * 65)
    cm = confusion_matrix(y_true, y_pred, labels=CLASS_NAMES)
    print(f"{'':<18} Predicted")
    print(f"{'':<18} {'  '.join([f'{c:>10}' for c in CLASS_NAMES])}")
    for idx, actual in enumerate(CLASS_NAMES):
        row_str = "  ".join([f"{cm[idx][j]:>10}" for j in range(len(CLASS_NAMES))])
        print(f"Actual {actual:<11} {row_str}")
    print("=" * 65 + "\n")

    return results, cm


def main():
    parser = argparse.ArgumentParser(description="SolarSafe AI - Model Verification & Test")
    parser.add_argument("--image", type=str, help="Path to solar panel image for single prediction")
    parser.add_argument("--test-suite", action="store_true", help="Run comprehensive evaluation on test suite")
    parser.add_argument("--samples", type=int, default=15, help="Samples per class for test suite")
    args = parser.parse_args()

    if args.image:
        predict_single(args.image)
    else:
        run_evaluation_suite(samples_per_class=args.samples)


if __name__ == "__main__":
    main()
