"""
backup_v1_baseline.py
----------------------
Creates a preserved, read-only copy of V1 baseline artifacts.
Does NOT modify or delete any original V1 files.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import json
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
BASELINE_DIR = OUTPUTS_DIR / "baseline_v1"

# Source paths (original V1 artifacts)
V1_MODEL_SRC     = OUTPUTS_DIR / "checkpoints" / "best_model.keras"
V1_CM_SRC        = OUTPUTS_DIR / "evaluation" / "confusion_matrix.png"
V1_REPORT_SRC    = OUTPUTS_DIR / "reports" / "classification_report.txt"
V1_METRICS_SRC   = OUTPUTS_DIR / "evaluation" / "metrics.json"

def backup():
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------
    # Copy V1 model
    # ---------------------------------------------------------------
    dst_model = BASELINE_DIR / "best_model_v1.keras"
    if not V1_MODEL_SRC.exists():
        print(f"[ERROR] V1 model not found at: {V1_MODEL_SRC}")
        sys.exit(1)
    shutil.copy2(V1_MODEL_SRC, dst_model)
    print(f"[OK] Copied V1 model: {dst_model}")

    # ---------------------------------------------------------------
    # Copy confusion matrix
    # ---------------------------------------------------------------
    dst_cm = BASELINE_DIR / "confusion_matrix_v1.png"
    if V1_CM_SRC.exists():
        shutil.copy2(V1_CM_SRC, dst_cm)
        print(f"[OK] Copied V1 confusion matrix: {dst_cm}")
    else:
        print(f"[WARN] Confusion matrix not found at {V1_CM_SRC}, skipping.")

    # ---------------------------------------------------------------
    # Copy classification report
    # ---------------------------------------------------------------
    dst_report = BASELINE_DIR / "classification_report_v1.txt"
    if V1_REPORT_SRC.exists():
        shutil.copy2(V1_REPORT_SRC, dst_report)
        print(f"[OK] Copied V1 classification report: {dst_report}")
    else:
        print(f"[WARN] Classification report not found at {V1_REPORT_SRC}, skipping.")

    # ---------------------------------------------------------------
    # Write baseline_metrics.json from verified V1 results
    # ---------------------------------------------------------------
    if V1_METRICS_SRC.exists():
        shutil.copy2(V1_METRICS_SRC, BASELINE_DIR / "metrics_raw_v1.json")

    baseline_metrics = {
        "experiment": "V1_Baseline",
        "model": "MobileNetV2",
        "source": "Verified independent test evaluation",
        "test_accuracy": 0.8000,
        "test_loss": 0.8431,
        "macro_f1": 0.7685,
        "weighted_f1": 0.8013,
        "per_class": {
            "Cell_Crack": {
                "precision": 0.9184,
                "recall": 0.7200,
                "f1": 0.8072,
                "support": 250
            },
            "Hotspot": {
                "precision": 0.6000,
                "recall": 0.7800,
                "f1": 0.6783,
                "support": 50
            },
            "Normal": {
                "precision": 0.7647,
                "recall": 0.8840,
                "f1": 0.8200,
                "support": 250
            }
        },
        "confusion_matrix": [
            [180, 10, 60],
            [3, 39, 8],
            [13, 16, 221]
        ],
        "class_order": ["Cell_Crack", "Hotspot", "Normal"],
        "notes": "60 Cell_Crack images misclassified as Normal. Primary V2 improvement target."
    }

    metrics_path = BASELINE_DIR / "baseline_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(baseline_metrics, f, indent=4)
    print(f"[OK] Saved baseline_metrics.json: {metrics_path}")

    # ---------------------------------------------------------------
    # Verify originals still intact
    # ---------------------------------------------------------------
    print("\n--- Verifying V1 originals are intact ---")
    assert V1_MODEL_SRC.exists(), "CRITICAL: V1 original model was deleted!"
    print(f"[OK] Original V1 model exists: {V1_MODEL_SRC} ({V1_MODEL_SRC.stat().st_size / 1e6:.1f} MB)")
    assert dst_model.exists(), "CRITICAL: V1 baseline copy missing!"
    print(f"[OK] Baseline copy exists: {dst_model} ({dst_model.stat().st_size / 1e6:.1f} MB)")

    print("\n[DONE] V1 baseline backup complete.")
    print(f"       Baseline directory: {BASELINE_DIR}")


if __name__ == "__main__":
    backup()
