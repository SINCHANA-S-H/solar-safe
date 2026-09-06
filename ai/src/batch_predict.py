"""
batch_predict.py
----------------
Batch prediction test script for SolarSafe AI.
Selects sample images from the test set across all classes, runs inference,
verifies predictions against actual ground truth labels, and reports accuracy.

Usage:
  python ai/src/batch_predict.py --samples 10
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import json
import random
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path

from config import TEST_DIR, BEST_MODEL_PATH, CLASS_NAMES, PREDICTIONS_DIR
from preprocessing import ImagePreprocessor


def run_batch_predict(num_samples=10):
    print("=" * 60)
    print(f"SolarSafe AI — Batch Prediction Test ({num_samples} samples)")
    print("=" * 60)

    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at: {BEST_MODEL_PATH}")

    print(f"Loading model from: {BEST_MODEL_PATH}")
    model = tf.keras.models.load_model(BEST_MODEL_PATH)

    # Collect test images per class
    class_test_images = {}
    for cls in CLASS_NAMES:
        cls_folder = TEST_DIR / cls
        if cls_folder.exists():
            imgs = [f for f in cls_folder.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")]
            class_test_images[cls] = imgs

    # Sample images evenly across classes
    sampled_items = []
    samples_per_class = max(1, num_samples // len(CLASS_NAMES))

    for cls in CLASS_NAMES:
        imgs = class_test_images.get(cls, [])
        if imgs:
            chosen = random.sample(imgs, min(len(imgs), samples_per_class))
            for img_path in chosen:
                sampled_items.append((cls, img_path))

    # If we need more samples to hit num_samples
    remaining_needed = num_samples - len(sampled_items)
    if remaining_needed > 0:
        all_remaining = []
        for cls in CLASS_NAMES:
            for p in class_test_images.get(cls, []):
                if (cls, p) not in sampled_items:
                    all_remaining.append((cls, p))
        if all_remaining:
            sampled_items.extend(random.sample(all_remaining, min(len(all_remaining), remaining_needed)))

    print(f"Selected {len(sampled_items)} test images for evaluation.\n")

    results = []
    correct_count = 0

    header = f"{'Actual Class':<15} | {'Predicted Class':<15} | {'Confidence':<10} | {'Status':<10} | {'Filename'}"
    print(header)
    print("-" * len(header))

    for actual_cls, img_path in sampled_items:
        img_array = ImagePreprocessor.preprocess(img_path)
        batch_array = ImagePreprocessor.prepare_batch(img_array)

        preds = model.predict(batch_array, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        pred_cls = CLASS_NAMES[pred_idx]
        confidence = float(preds[pred_idx] * 100)

        is_correct = (actual_cls == pred_cls)
        if is_correct:
            correct_count += 1
            status = "MATCH [OK]"
        else:
            status = "MISMATCH [X]"

        print(f"{actual_cls:<15} | {pred_cls:<15} | {confidence:>9.2f}% | {status:<10} | {img_path.name}")

        results.append({
            "filename": img_path.name,
            "actual_class": actual_cls,
            "predicted_class": pred_cls,
            "confidence": confidence,
            "correct": is_correct,
            "probabilities": {cls: float(score) for cls, score in zip(CLASS_NAMES, preds)}
        })

    accuracy = (correct_count / len(sampled_items)) * 100 if sampled_items else 0.0
    print("-" * len(header))
    print(f"\nBatch Accuracy: {correct_count}/{len(sampled_items)} ({accuracy:.2f}%)")

    PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_json = PREDICTIONS_DIR / "batch_predictions.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "total_samples": len(sampled_items),
            "correct_samples": correct_count,
            "batch_accuracy": accuracy,
            "results": results
        }, f, indent=4)

    print(f"Saved batch prediction results to: {out_json}")


def main():
    parser = argparse.ArgumentParser(description="SolarSafe AI - Batch Prediction Test")
    parser.add_argument("--samples", type=int, default=10, help="Number of test samples to predict")
    args = parser.parse_args()

    run_batch_predict(args.samples)


if __name__ == "__main__":
    main()
