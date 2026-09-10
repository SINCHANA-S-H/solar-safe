"""
run_final_verification.py
-------------------------
Executes the final test verification on feature-ai:
- Tests at least 5 Normal, 5 Hotspot, and 5 Cell_Crack images
- Records Actual, Predicted, Confidence, and all probabilities
- Generates Confusion Matrix, Classification Report, Precision, Recall, F1
- Tests Grad-CAM on Normal, Hotspot, and Cell_Crack images
- Verifies heatmaps and overlay files
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "src"))

from config import FINAL_MODEL_PATH, TEST_DIR, CLASS_NAMES, GRADCAM_DIR
from preprocessing import ImagePreprocessor
from gradcam import get_model, generate_gradcam

def run_final_test():
    print("=" * 75)
    print("SOLARSAFE AI — FINAL MODEL & GRAD-CAM VERIFICATION")
    print("=" * 75)

    model = get_model()
    print(f"Loaded Model: {FINAL_MODEL_PATH}")
    print(f"Classes: {CLASS_NAMES}")

    samples_per_class = 5
    selected_samples = []

    for cls in CLASS_NAMES:
        cls_dir = TEST_DIR / cls
        images = sorted([f for f in cls_dir.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")])
        if len(images) < samples_per_class:
            raise RuntimeError(f"Not enough test images in {cls_dir}")
        for img in images[:samples_per_class]:
            selected_samples.append((cls, img))

    print(f"\nTotal Test Samples: {len(selected_samples)} ({samples_per_class} per class)\n")

    y_true = []
    y_pred = []
    records = []

    print("-" * 75)
    print(f"{'#':<3} | {'Filename':<28} | {'Actual':<11} | {'Predicted':<11} | {'Conf':<8} | {'Probabilities (CC / HS / Norm)'}")
    print("-" * 75)

    for idx, (actual_cls, img_path) in enumerate(selected_samples, 1):
        img_arr = ImagePreprocessor.preprocess(img_path)
        batch = ImagePreprocessor.prepare_batch(img_arr)
        preds = model.predict(batch, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        pred_cls = CLASS_NAMES[pred_idx]
        conf = float(preds[pred_idx] * 100)

        y_true.append(actual_cls)
        y_pred.append(pred_cls)

        prob_str = f"{preds[0]*100:5.1f}% / {preds[1]*100:5.1f}% / {preds[2]*100:5.1f}%"
        print(f"{idx:<3} | {img_path.name[:28]:<28} | {actual_cls:<11} | {pred_cls:<11} | {conf:6.2f}% | {prob_str}")

        records.append({
            "idx": idx,
            "filename": img_path.name,
            "actual": actual_cls,
            "predicted": pred_cls,
            "confidence": conf,
            "probs": {cls: float(preds[i]) for i, cls in enumerate(CLASS_NAMES)},
            "path": img_path
        })

    print("-" * 75)

    # Metrics
    cm = confusion_matrix(y_true, y_pred, labels=CLASS_NAMES)
    report = classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=4)
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=CLASS_NAMES, zero_division=0)
    acc = np.mean(np.array(y_true) == np.array(y_pred)) * 100

    print("\n" + "=" * 75)
    print(f"OVERALL ACCURACY: {acc:.2f}% ({sum(np.array(y_true) == np.array(y_pred))}/{len(y_true)})")
    print("=" * 75)

    print("\nPER-CLASS METRICS:")
    print(f"{'Class':<15} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support'}")
    print("-" * 60)
    for i, cls in enumerate(CLASS_NAMES):
        print(f"{cls:<15} | {precision[i]:<10.4f} | {recall[i]:<10.4f} | {f1[i]:<10.4f} | {support[i]}")

    print("\nCONFUSION MATRIX:")
    print(f"{'':<18} Predicted")
    print(f"{'':<18} {'  '.join([f'{c:>12}' for c in CLASS_NAMES])}")
    for idx, actual in enumerate(CLASS_NAMES):
        row_str = "  ".join([f"{cm[idx][j]:>12}" for j in range(len(CLASS_NAMES))])
        print(f"Actual {actual:<11} {row_str}")

    print("\n" + "=" * 75)
    print("CLASSIFICATION REPORT:")
    print("=" * 75)
    print(report)

    # Grad-CAM Tests
    print("\n" + "=" * 75)
    print("GRAD-CAM VERIFICATION ON TEST SAMPLES")
    print("=" * 75)

    GRADCAM_DIR.mkdir(parents=True, exist_ok=True)
    for cls in CLASS_NAMES:
        cls_samples = [s for s in records if s["actual"] == cls]
        sample = cls_samples[0]
        out_overlay = GRADCAM_DIR / f"final_test_gradcam_{cls}_{sample['filename']}.png"

        print(f"\nTesting Grad-CAM for {cls}:")
        print(f"  Input: {sample['path']}")
        res = generate_gradcam(sample["path"], model=model, output_path=out_overlay)
        print(f"  Predicted: {res['prediction']} ({res['confidence']:.2f}%)")
        print(f"  Heatmap Shape: {res['heatmap'].shape}, Min: {res['heatmap'].min():.4f}, Max: {res['heatmap'].max():.4f}")
        print(f"  Overlay Saved: {out_overlay.name} (exists={out_overlay.exists()}, size={out_overlay.stat().st_size} bytes)")
        assert out_overlay.exists() and out_overlay.stat().st_size > 1000, "Grad-CAM file failed to write properly"
        assert res["heatmap"].shape == (7, 7), f"Unexpected heatmap shape {res['heatmap'].shape}"

    print("\n" + "=" * 75)
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY WITH ZERO ERRORS!")
    print("=" * 75)

if __name__ == "__main__":
    run_final_test()
