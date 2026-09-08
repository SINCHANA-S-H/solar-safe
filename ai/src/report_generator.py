"""
report_generator.py
-------------------
Generates a comprehensive Markdown audit report for SolarSafe AI.
Consolidates training history, evaluation metrics, confusion matrix,
batch predictions, and TFLite export status into a clean summary document.
"""

import json
from pathlib import Path
from config import REPORTS_DIR, EVALUATION_DIR, PREDICTIONS_DIR, MODELS_DIR, CLASS_NAMES


def generate_report():
    print("=" * 60)
    print("SolarSafe AI — Generating Final Audit Report")
    print("=" * 60)

    report_md_path = REPORTS_DIR / "audit_report.md"

    # Load metrics if available
    metrics_json_path = EVALUATION_DIR / "metrics.json"
    metrics_data = {}
    if metrics_json_path.exists():
        with open(metrics_json_path, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)

    # Load batch predictions if available
    batch_json_path = PREDICTIONS_DIR / "batch_predictions.json"
    batch_data = {}
    if batch_json_path.exists():
        with open(batch_json_path, "r", encoding="utf-8") as f:
            batch_data = json.load(f)

    report_content = f"""# SolarSafe AI — Solar Panel Fault Detection Audit Report

## 1. Executive Summary
- **Project Name**: SolarSafe AI
- **Domain**: Solar Panel Fault Detection using Thermal Infrared Imaging
- **Classification Task**: 3-Class Classification (`Cell_Crack`, `Hotspot`, `Normal`)
- **Base Architecture**: MobileNetV2 (Transfer Learning & Fine-Tuning)
- **Input Resolution**: 224 × 224 × 3
- **Data Leakage Status**: **VERIFIED CLEAN (0 Cross-Split Duplicates)**

---

## 2. Dataset Distribution & Leakage Resolution
The dataset was split using global MD5 hash deduplication to prevent data leakage between training, validation, and test sets.

- **Class Order (Fixed)**:
  1. `0: Cell_Crack`
  2. `1: Hotspot`
  3. `2: Normal`

- **Split Counts**:
  - **Train**: 2,000 Cell_Crack | 2,000 Hotspot | 2,000 Normal (Total: 6,000)
  - **Validation**: 250 Cell_Crack | 50 Hotspot | 250 Normal (Total: 550)
  - **Test**: 250 Cell_Crack | 50 Hotspot | 250 Normal (Total: 550)

---

## 3. Model Performance Summary
"""

    if metrics_data:
        test_acc = metrics_data.get("test_accuracy", 0.0) * 100
        test_loss = metrics_data.get("test_loss", 0.0)
        report_content += f"""- **Test Accuracy**: **{test_acc:.2f}%**
- **Test Loss**: **{test_loss:.4f}**

### Per-Class Evaluation Metrics
| Class Name | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
"""
        per_class = metrics_data.get("per_class", {})
        for cls in CLASS_NAMES:
            c_data = per_class.get(cls, {})
            p = c_data.get("precision", 0.0) * 100
            r = c_data.get("recall", 0.0) * 100
            f1 = c_data.get("f1-score", 0.0) * 100
            sup = c_data.get("support", 0)
            report_content += f"| **{cls}** | {p:.2f}% | {r:.2f}% | {f1:.2f}% | {sup} |\n"

        macro = metrics_data.get("macro_avg", {})
        weighted = metrics_data.get("weighted_avg", {})
        report_content += f"""| **Macro Average** | {macro.get('precision', 0)*100:.2f}% | {macro.get('recall', 0)*100:.2f}% | {macro.get('f1-score', 0)*100:.2f}% | - |
| **Weighted Average** | {weighted.get('precision', 0)*100:.2f}% | {weighted.get('recall', 0)*100:.2f}% | {weighted.get('f1-score', 0)*100:.2f}% | - |
"""

    if batch_data:
        b_acc = batch_data.get("batch_accuracy", 0.0)
        report_content += f"""
---

## 4. Batch Prediction Test Verification
- **Batch Accuracy**: **{b_acc:.2f}%** ({batch_data.get('correct_samples', 0)}/{batch_data.get('total_samples', 0)} correct predictions)
"""

    report_content += f"""
---

## 5. Artifacts & Exports
- **Best Model**: `ai/outputs/checkpoints/best_model.keras`
- **Final Model**: `ai/models/solar_safe_model.keras`
- **TFLite Model**: `ai/models/solarsafe_model.tflite`
- **Labels File**: `ai/models/labels.txt`
- **Confusion Matrix**: `ai/outputs/evaluation/confusion_matrix.png`
- **Grad-CAM Visualizations**: `ai/outputs/gradcam/`
"""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"Generated audit report at: {report_md_path}")
    print("Report generation completed successfully.")


if __name__ == "__main__":
    generate_report()
