"""
evaluate_full_test_set.py
-------------------------
Evaluates the model on the full test set (all 1480 images).
Produces classification report, confusion matrix, accuracy,
precision, recall, F1 for every class, and transition rates:
Hotspot -> Cell_Crack, Hotspot -> Normal, Cell_Crack -> Normal, Cell_Crack -> Hotspot.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import sys
from pathlib import Path
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FINAL_MODEL_PATH, CLASS_NAMES, TEST_DIR, IMG_SIZE

def main():
    print(f"Evaluating Model: {FINAL_MODEL_PATH}")
    model = tf.keras.models.load_model(FINAL_MODEL_PATH, compile=False)

    test_dataset = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=64,
        shuffle=False,
    )

    y_true = []
    y_pred = []

    for images, labels in test_dataset:
        preds = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        y_pred.extend(np.argmax(preds, axis=1))

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    print("\n" + "=" * 65)
    print("FULL TEST SET EVALUATION (1480 IMAGES)")
    print("=" * 65)
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=4))

    cm = confusion_matrix(y_true, y_pred)
    print("CONFUSION MATRIX:")
    print(f"{'Actual':<15} | " + " | ".join([f"Pred {c:<10}" for c in CLASS_NAMES]))
    print("-" * 65)
    for idx, actual in enumerate(CLASS_NAMES):
        print(f"{actual:<15} | " + " | ".join([f"{cm[idx][j]:<15}" for j in range(len(CLASS_NAMES))]))

    total_hs = cm[1].sum()
    hs_to_cc = cm[1][0] / total_hs * 100
    hs_to_norm = cm[1][2] / total_hs * 100

    total_cc = cm[0].sum()
    cc_to_norm = cm[0][2] / total_cc * 100
    cc_to_hs = cm[0][1] / total_cc * 100

    print("\nTRANSITION ERROR RATES:")
    print(f"  Hotspot -> Cell_Crack rate : {hs_to_cc:.2f}% ({cm[1][0]}/{total_hs})")
    print(f"  Hotspot -> Normal rate     : {hs_to_norm:.2f}% ({cm[1][2]}/{total_hs})")
    print(f"  Cell_Crack -> Normal rate  : {cc_to_norm:.2f}% ({cm[0][2]}/{total_cc})")
    print(f"  Cell_Crack -> Hotspot rate : {cc_to_hs:.2f}% ({cm[0][1]}/{total_cc})")

if __name__ == "__main__":
    main()
