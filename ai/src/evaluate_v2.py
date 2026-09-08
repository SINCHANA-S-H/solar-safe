"""
evaluate_v2.py
--------------
SolarSafe AI V2 — Multi-Model Evaluation Script.

Evaluates V1, V2-A, and V2-B on the EXACT SAME independent test set.
Uses identical preprocessing (image_dataset_from_directory, shuffle=False)
to ensure results are scientifically comparable.

Outputs:
  - Per-model metrics.json, classification_report.txt, confusion_matrix.png
  - ai/outputs/experiments/v2/model_comparison.csv (side-by-side table)
  - ai/outputs/experiments/v2/hard_cell_crack_comparison.csv
    (tracks the original 60 V1 Cell_Crack→Normal errors across models)

Verification:
  - Re-evaluates V1 to confirm ~80.00% accuracy before accepting comparison.
  - Raises a warning if V1 results deviate >2% from known baseline.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import json
import csv
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import (
    classification_report, confusion_matrix, ConfusionMatrixDisplay
)

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    TEST_DIR, IMG_SIZE, BATCH_SIZE, CLASS_NAMES,
    OUTPUTS_DIR, CHECKPOINT_DIR,
)
from focal_loss import FocalLoss

# ============================================================
# PATHS
# ============================================================

EXPERIMENTS_DIR = OUTPUTS_DIR / "experiments" / "v2"
BASELINE_DIR    = OUTPUTS_DIR / "baseline_v1"

MODEL_REGISTRY = {
    "V1_Baseline": {
        "path": CHECKPOINT_DIR / "best_model.keras",
        "out_dir": BASELINE_DIR,
        "label": "V1 Baseline",
    },
    "V2_A": {
        "path": EXPERIMENTS_DIR / "v2_a_augmentation" / "best_model_v2a.keras",
        "out_dir": EXPERIMENTS_DIR / "v2_a_augmentation",
        "label": "V2-A Augmentation",
    },
    "V2_B": {
        "path": EXPERIMENTS_DIR / "v2_b_focal" / "best_model_v2b.keras",
        "out_dir": EXPERIMENTS_DIR / "v2_b_focal",
        "label": "V2-B Focal Loss",
    },
}

# ============================================================
# SHARED TEST DATASET
# ============================================================

def load_test_dataset():
    """Load test dataset with shuffle=False for deterministic evaluation."""
    ds = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )
    assert ds.class_names == CLASS_NAMES, (
        f"Test class order mismatch!\n"
        f"  Expected: {CLASS_NAMES}\n"
        f"  Detected: {ds.class_names}"
    )
    print(f"[OK] Test class order: {ds.class_names}")
    return ds


# ============================================================
# EVALUATE ONE MODEL
# ============================================================

def evaluate_model(name: str, model_path: Path, test_ds, out_dir: Path) -> dict:
    """Evaluate a single model on the test dataset.

    Args:
        name: Model name string.
        model_path: Path to the .keras model file.
        test_ds: Shared test dataset (deterministic, no shuffle).
        out_dir: Directory to save this model's evaluation outputs.

    Returns:
        Dict of metrics for comparison.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'=' * 60}")
    print(f"Evaluating: {name}")
    print(f"  Model path: {model_path}")
    print(f"{'=' * 60}")

    if not model_path.exists():
        print(f"[SKIP] Model not found: {model_path}")
        return None

    # Load model — custom objects for Focal Loss compatibility
    model = tf.keras.models.load_model(
        str(model_path),
        custom_objects={"FocalLoss": FocalLoss},
    )

    # ---- Evaluate ----
    loss, accuracy = model.evaluate(test_ds, verbose=0)
    print(f"  Test Loss     : {loss:.4f}")
    print(f"  Test Accuracy : {accuracy * 100:.2f}%")

    # ---- Predictions ----
    preds_prob = model.predict(test_ds, verbose=0)
    y_pred = np.argmax(preds_prob, axis=1)

    y_true = []
    for _, labels in test_ds:
        y_true.extend(np.argmax(labels.numpy(), axis=1))
    y_true = np.array(y_true)

    # ---- File paths (for hard error analysis) ----
    file_paths = test_ds.file_paths

    # ---- Classification report ----
    report_str = classification_report(
        y_true, y_pred, target_names=CLASS_NAMES, digits=4
    )
    report_dict = classification_report(
        y_true, y_pred, target_names=CLASS_NAMES, output_dict=True
    )
    print("\n" + report_str)

    # Save classification report
    report_path = out_dir / "classification_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"SolarSafe AI — {name} Evaluation\n")
        f.write("=" * 60 + "\n")
        f.write(f"Test Loss     : {loss:.4f}\n")
        f.write(f"Test Accuracy : {accuracy * 100:.2f}%\n\n")
        f.write(report_str)
    print(f"[OK] Classification report saved: {report_path}")

    # ---- Confusion matrix ----
    cm = confusion_matrix(y_true, y_pred)
    print(f"Confusion Matrix:\n{cm}")

    fig, ax = plt.subplots(figsize=(8, 7))
    ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=CLASS_NAMES,
    ).plot(cmap="Blues", ax=ax, colorbar=False)
    ax.set_title(f"SolarSafe AI — {name}", fontsize=13, pad=12)
    plt.tight_layout()
    cm_path = out_dir / "confusion_matrix.png"
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"[OK] Confusion matrix saved: {cm_path}")

    # ---- Build structured metrics ----
    metrics = {
        "model": name,
        "model_path": str(model_path),
        "test_loss": float(loss),
        "test_accuracy": float(accuracy),
        "macro_precision": float(report_dict["macro avg"]["precision"]),
        "macro_recall":    float(report_dict["macro avg"]["recall"]),
        "macro_f1":        float(report_dict["macro avg"]["f1-score"]),
        "weighted_precision": float(report_dict["weighted avg"]["precision"]),
        "weighted_recall":    float(report_dict["weighted avg"]["recall"]),
        "weighted_f1":        float(report_dict["weighted avg"]["f1-score"]),
        "per_class": {
            cls: {
                "precision": float(report_dict[cls]["precision"]),
                "recall":    float(report_dict[cls]["recall"]),
                "f1":        float(report_dict[cls]["f1-score"]),
                "support":   int(report_dict[cls]["support"]),
            }
            for cls in CLASS_NAMES
        },
        "confusion_matrix": cm.tolist(),
        "file_paths": file_paths,  # kept in memory, not written to JSON
        "y_pred": y_pred.tolist(),
        "y_pred_probs": preds_prob.tolist(),
        "y_true": y_true.tolist(),
    }

    # Save metrics JSON (without file_paths and raw pred arrays for cleanliness)
    metrics_clean = {k: v for k, v in metrics.items()
                     if k not in ("file_paths", "y_pred", "y_pred_probs", "y_true")}
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_clean, f, indent=4)
    print(f"[OK] Metrics saved: {metrics_path}")

    return metrics


# ============================================================
# V1 CONSISTENCY VERIFICATION
# ============================================================

def verify_v1_consistency(v1_metrics: dict):
    """Warn if re-evaluated V1 deviates significantly from known baseline."""
    expected_acc = 0.8000
    actual_acc   = v1_metrics["test_accuracy"]
    tolerance    = 0.02   # 2% tolerance

    print(f"\n--- V1 Consistency Verification ---")
    print(f"  Expected accuracy : {expected_acc:.4f}")
    print(f"  Actual accuracy   : {actual_acc:.4f}")

    if abs(actual_acc - expected_acc) > tolerance:
        print(f"\n[WARNING] V1 accuracy deviated > {tolerance*100:.0f}% from baseline!")
        print("  Possible causes: model path, class order, preprocessing mismatch.")
        print("  STOPPING comparison — investigate before proceeding.")
        raise RuntimeError(
            f"V1 re-evaluation mismatch: expected ~{expected_acc:.4f}, got {actual_acc:.4f}"
        )

    # Check Cell_Crack recall
    expected_cc_recall = 0.7200
    actual_cc_recall   = v1_metrics["per_class"]["Cell_Crack"]["recall"]
    if abs(actual_cc_recall - expected_cc_recall) > tolerance:
        print(f"\n[WARNING] V1 Cell_Crack recall deviated from baseline!")
        print(f"  Expected: {expected_cc_recall:.4f}, Got: {actual_cc_recall:.4f}")
    else:
        print(f"  Cell_Crack recall: {actual_cc_recall:.4f} — consistent with baseline")

    print(f"[OK] V1 consistency check passed. Proceeding with comparison.")


# ============================================================
# HARD CELL_CRACK COMPARISON
# ============================================================

def build_hard_cc_comparison(results: dict):
    """Track the original 60 V1 Cell_Crack→Normal errors across models.

    Identifies the exact file paths where V1 predicted Cell_Crack as Normal,
    then checks what V2-A and V2-B predict on those same images.

    Args:
        results: Dict mapping model_key -> metrics dict (with file_paths, y_pred etc.)

    Returns:
        Path to saved hard_cell_crack_comparison.csv
    """
    v1 = results.get("V1_Baseline")
    if v1 is None:
        print("[SKIP] V1 results unavailable for hard CC comparison.")
        return None

    file_paths = v1["file_paths"]
    y_pred_v1  = v1["y_pred"]
    y_true_v1  = v1["y_true"]
    probs_v1   = v1["y_pred_probs"]

    # Find indices where actual=Cell_Crack and V1 predicted Normal
    CC_IDX     = CLASS_NAMES.index("Cell_Crack")
    NORMAL_IDX = CLASS_NAMES.index("Normal")

    hard_indices = [
        i for i, (yt, yp) in enumerate(zip(y_true_v1, y_pred_v1))
        if yt == CC_IDX and yp == NORMAL_IDX
    ]
    print(f"\n--- Hard Cell_Crack Error Recovery Analysis ---")
    print(f"  V1 Cell_Crack→Normal errors (hard set): {len(hard_indices)}")

    rows = []
    recovered_v2a = 0
    recovered_v2b = 0

    v2a = results.get("V2_A")
    v2b = results.get("V2_B")

    for i in hard_indices:
        fp = Path(file_paths[i]).name
        v1_pred  = CLASS_NAMES[y_pred_v1[i]]
        v1_conf  = float(max(probs_v1[i]))

        # V2-A
        if v2a:
            v2a_pred = CLASS_NAMES[v2a["y_pred"][i]]
            v2a_conf = float(max(v2a["y_pred_probs"][i]))
            if v2a_pred == "Cell_Crack":
                recovered_v2a += 1
        else:
            v2a_pred, v2a_conf = "N/A", 0.0

        # V2-B
        if v2b:
            v2b_pred = CLASS_NAMES[v2b["y_pred"][i]]
            v2b_conf = float(max(v2b["y_pred_probs"][i]))
            if v2b_pred == "Cell_Crack":
                recovered_v2b += 1
        else:
            v2b_pred, v2b_conf = "N/A", 0.0

        rows.append({
            "filename":         fp,
            "actual_class":     "Cell_Crack",
            "v1_prediction":    v1_pred,
            "v1_confidence":    f"{v1_conf:.4f}",
            "v2a_prediction":   v2a_pred,
            "v2a_confidence":   f"{v2a_conf:.4f}",
            "v2b_prediction":   v2b_pred,
            "v2b_confidence":   f"{v2b_conf:.4f}",
        })

    print(f"  V2-A recovered : {recovered_v2a} / {len(hard_indices)}")
    print(f"  V2-B recovered : {recovered_v2b} / {len(hard_indices)}")

    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXPERIMENTS_DIR / "hard_cell_crack_comparison.csv"
    fieldnames = [
        "filename", "actual_class",
        "v1_prediction", "v1_confidence",
        "v2a_prediction", "v2a_confidence",
        "v2b_prediction", "v2b_confidence",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Hard CC comparison saved: {out_path}")
    return out_path, recovered_v2a, recovered_v2b, len(hard_indices)


# ============================================================
# MODEL COMPARISON CSV + TABLE
# ============================================================

def build_comparison_csv(results: dict):
    """Generate model_comparison.csv with side-by-side metrics."""
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXPERIMENTS_DIR / "model_comparison.csv"

    fieldnames = [
        "model", "accuracy", "loss",
        "macro_precision", "macro_recall", "macro_f1",
        "weighted_precision", "weighted_recall", "weighted_f1",
        "cell_crack_precision", "cell_crack_recall", "cell_crack_f1",
        "hotspot_precision", "hotspot_recall", "hotspot_f1",
        "normal_precision", "normal_recall", "normal_f1",
        "cell_crack_pred_as_normal",
    ]

    rows = []
    for key, r in results.items():
        if r is None:
            continue
        cm = r["confusion_matrix"]
        # Cell_Crack row: cm[0][2] = CC predicted as Normal
        cc_as_normal = cm[0][2] if len(cm) > 0 else "N/A"
        row = {
            "model": r["model"],
            "accuracy":  f"{r['test_accuracy']:.4f}",
            "loss":      f"{r['test_loss']:.4f}",
            "macro_precision": f"{r['macro_precision']:.4f}",
            "macro_recall":    f"{r['macro_recall']:.4f}",
            "macro_f1":        f"{r['macro_f1']:.4f}",
            "weighted_precision": f"{r['weighted_precision']:.4f}",
            "weighted_recall":    f"{r['weighted_recall']:.4f}",
            "weighted_f1":        f"{r['weighted_f1']:.4f}",
            "cell_crack_precision": f"{r['per_class']['Cell_Crack']['precision']:.4f}",
            "cell_crack_recall":    f"{r['per_class']['Cell_Crack']['recall']:.4f}",
            "cell_crack_f1":        f"{r['per_class']['Cell_Crack']['f1']:.4f}",
            "hotspot_precision": f"{r['per_class']['Hotspot']['precision']:.4f}",
            "hotspot_recall":    f"{r['per_class']['Hotspot']['recall']:.4f}",
            "hotspot_f1":        f"{r['per_class']['Hotspot']['f1']:.4f}",
            "normal_precision": f"{r['per_class']['Normal']['precision']:.4f}",
            "normal_recall":    f"{r['per_class']['Normal']['recall']:.4f}",
            "normal_f1":        f"{r['per_class']['Normal']['f1']:.4f}",
            "cell_crack_pred_as_normal": cc_as_normal,
        }
        rows.append(row)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[OK] Model comparison CSV saved: {out_path}")

    # Print comparison table
    print("\n" + "=" * 100)
    print("MODEL COMPARISON TABLE")
    print("=" * 100)
    header = f"{'Model':<25} {'Acc':>7} {'Macro_F1':>10} {'WtF1':>8} {'CC_Rec':>8} {'CC_F1':>8} {'CC→Nrm':>8}"
    print(header)
    print("-" * 100)
    for r in rows:
        print(
            f"{r['model']:<25} "
            f"{r['accuracy']:>7} "
            f"{r['macro_f1']:>10} "
            f"{r['weighted_f1']:>8} "
            f"{r['cell_crack_recall']:>8} "
            f"{r['cell_crack_f1']:>8} "
            f"{r['cell_crack_pred_as_normal']:>8}"
        )
    print("=" * 100)

    return out_path


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("SolarSafe AI V2 — Multi-Model Evaluation")
    print("=" * 65)

    # Load shared test dataset ONCE
    print("\nLoading test dataset (shared for all models)...")
    test_ds = load_test_dataset()

    results = {}

    # ---- Evaluate all models ----
    for key, info in MODEL_REGISTRY.items():
        metrics = evaluate_model(
            name=info["label"],
            model_path=info["path"],
            test_ds=test_ds,
            out_dir=info["out_dir"],
        )
        results[key] = metrics

    # ---- V1 consistency verification ----
    if results["V1_Baseline"] is not None:
        verify_v1_consistency(results["V1_Baseline"])

    # ---- Hard Cell_Crack comparison ----
    hard_result = build_hard_cc_comparison(results)

    # ---- Comparison CSV ----
    build_comparison_csv(results)

    print("\n[DONE] evaluate_v2.py complete.")
    return results, hard_result


if __name__ == "__main__":
    main()
