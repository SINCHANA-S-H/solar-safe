"""
evaluate.py
-----------
Comprehensive evaluation script for SolarSafe AI model.
Evaluates model on the independent test dataset:
- Accuracy & Loss
- Per-class Precision, Recall, F1-Score
- Macro and Weighted Averages
- Confusion Matrix Visualization
- Detailed Metrics Export (JSON & TXT)
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import json
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay

from config import (
    TEST_DIR,
    IMG_SIZE,
    BATCH_SIZE,
    CLASS_NAMES,
    BEST_MODEL_PATH,
    FINAL_MODEL_PATH,
    EVALUATION_DIR,
    REPORTS_DIR,
    CONFUSION_MATRIX,
    CLASSIFICATION_REPORT,
)


def evaluate_model():
    print("=" * 60)
    print("SolarSafe AI — Model Evaluation")
    print("=" * 60)

    print(f"\nLoading test dataset from: {TEST_DIR}\n")
    test_dataset = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    class_names = test_dataset.class_names
    print(f"Test Class Names: {class_names}")

    model_path = BEST_MODEL_PATH if BEST_MODEL_PATH.exists() else FINAL_MODEL_PATH
    print(f"\nLoading trained model from: {model_path}\n")
    model = tf.keras.models.load_model(model_path, compile=False)

    print("Evaluating model performance on test dataset...")
    loss, accuracy = model.evaluate(test_dataset, verbose=1)

    print("\nGenerating predictions...")
    predictions = model.predict(test_dataset, verbose=1)
    y_pred = np.argmax(predictions, axis=1)

    y_true = []
    for _, labels in test_dataset:
        y_true.extend(np.argmax(labels.numpy(), axis=1))
    y_true = np.array(y_true)

    # ---------------------------------------------------------
    # Classification Report
    # ---------------------------------------------------------
    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT")
    print("=" * 60)
    report_str = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        digits=4
    )
    print(report_str)

    report_dict = classification_report(
        y_true,
        y_pred,
        target_names=class_names,
        output_dict=True
    )

    # Save classification report txt
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(CLASSIFICATION_REPORT, "w", encoding="utf-8") as f:
        f.write("SolarSafe AI — Evaluation Classification Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"Test Loss    : {loss:.4f}\n")
        f.write(f"Test Accuracy: {accuracy * 100:.2f}%\n\n")
        f.write(report_str)

    # ---------------------------------------------------------
    # Confusion Matrix
    # ---------------------------------------------------------
    cm = confusion_matrix(y_true, y_pred)
    print("\nConfusion Matrix:")
    print(cm)

    fig, ax = plt.subplots(figsize=(8, 7))
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names,
    )
    disp.plot(cmap="Blues", ax=ax, colorbar=False)
    plt.title("SolarSafe AI — Confusion Matrix", fontsize=14, pad=15)
    plt.tight_layout()

    # Save in both EVALUATION_DIR and REPORTS_DIR
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)
    cm_path1 = CONFUSION_MATRIX
    cm_path2 = EVALUATION_DIR / "confusion_matrix.png"
    plt.savefig(cm_path1, dpi=300)
    plt.savefig(cm_path2, dpi=300)
    plt.close()

    print(f"\nSaved confusion matrix plot to:\n  - {cm_path1}\n  - {cm_path2}")

    # ---------------------------------------------------------
    # Save Metrics JSON
    # ---------------------------------------------------------
    metrics_summary = {
        "test_loss": float(loss),
        "test_accuracy": float(accuracy),
        "per_class": {
            cls: {
                "precision": float(report_dict[cls]["precision"]),
                "recall": float(report_dict[cls]["recall"]),
                "f1-score": float(report_dict[cls]["f1-score"]),
                "support": int(report_dict[cls]["support"]),
            }
            for cls in class_names
        },
        "macro_avg": report_dict["macro avg"],
        "weighted_avg": report_dict["weighted avg"],
        "confusion_matrix": cm.tolist()
    }

    metrics_json_path = EVALUATION_DIR / "metrics.json"
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=4)

    print(f"Saved evaluation metrics JSON to: {metrics_json_path}")
    print("\nModel evaluation completed successfully.")


if __name__ == "__main__":
    evaluate_model()