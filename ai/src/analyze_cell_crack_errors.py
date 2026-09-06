"""
analyze_cell_crack_errors.py
-----------------------------
Phase 3 Error Analysis Script for SolarSafe AI:
1. Evaluates all Cell_Crack images in the test set using TF-native preprocessing
   (tf.io.read_file + tf.image.decode_image + tf.image.resize) — identical to
   evaluate.py's image_dataset_from_directory pipeline — to guarantee consistent,
   reproducible predictions.
2. Generates prediction_consistency_check.csv comparing per-image predictions
   from image_dataset_from_directory vs individual TF-native file loading.
3. Identifies misclassified Cell_Crack images (predicted as Normal or Hotspot).
4. Exports misclassified_samples.csv with filenames, predictions, confidence,
   and raw probabilities.
5. Generates cell_crack_error_analysis.png visualizing correct vs misclassified
   Cell_Crack thermal images alongside their Grad-CAM overlays.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import csv
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from pathlib import Path

from config import (
    TEST_DIR,
    BEST_MODEL_PATH,
    CLASS_NAMES,
    EVALUATION_DIR,
    IMG_SIZE,
)
from gradcam import make_gradcam_heatmap, save_gradcam_overlay


# ---------------------------------------------------------------------------
# TF-native preprocessing — 100% identical to image_dataset_from_directory
# ---------------------------------------------------------------------------
def tf_load_image(image_path: Path) -> np.ndarray:
    """Load and resize a single image using TensorFlow's native pipeline.

    This is functionally identical to how image_dataset_from_directory decodes
    images internally (tf.io.read_file -> tf.image.decode_image -> tf.image.resize
    with bilinear interpolation).  Using this instead of PIL ensures per-image
    predictions match the confusion matrix produced by evaluate.py exactly.

    Args:
        image_path: Path to the image file.

    Returns:
        A float32 numpy array of shape (1, IMG_SIZE[0], IMG_SIZE[1], 3) ready
        for model.predict().
    """
    img_bytes = tf.io.read_file(str(image_path))
    img = tf.image.decode_image(img_bytes, channels=3, expand_animations=False)
    img = tf.image.resize(img, (IMG_SIZE, IMG_SIZE), method="bilinear")
    return np.expand_dims(img.numpy(), axis=0)


def run_cell_crack_error_analysis():
    print("=" * 60)
    print("SolarSafe AI — Cell_Crack Error Analysis & Diagnosis")
    print("=" * 60)

    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at: {BEST_MODEL_PATH}")

    print(f"Loading model from: {BEST_MODEL_PATH}")
    model = tf.keras.models.load_model(BEST_MODEL_PATH)

    # ------------------------------------------------------------------
    # Step 1: Run image_dataset_from_directory on full test set (same as
    # evaluate.py) to capture the ground-truth per-file prediction labels.
    # ------------------------------------------------------------------
    print("\n[Step 1] Running image_dataset_from_directory on test set "
          "(mirrors evaluate.py)...")
    test_dataset = tf.keras.utils.image_dataset_from_directory(
        TEST_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=16,
        shuffle=False,
    )
    tf_file_paths = test_dataset.file_paths
    all_preds = model.predict(test_dataset, verbose=0)
    eval_pred_map = {
        p: CLASS_NAMES[int(np.argmax(all_preds[i]))]
        for i, p in enumerate(tf_file_paths)
    }
    eval_conf_map = {
        p: float(np.max(all_preds[i]))
        for i, p in enumerate(tf_file_paths)
    }

    # ------------------------------------------------------------------
    # Step 2: Load Cell_Crack images individually using TF-native pipeline
    # and compare to image_dataset_from_directory predictions.
    # ------------------------------------------------------------------
    cell_crack_dir = TEST_DIR / "Cell_Crack"
    if not cell_crack_dir.exists():
        raise FileNotFoundError(
            f"Cell_Crack test folder not found at: {cell_crack_dir}"
        )

    image_paths = sorted(
        f for f in cell_crack_dir.iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")
    )
    print(f"\nFound {len(image_paths)} test images for class 'Cell_Crack'.")

    # ------------------------------------------------------------------
    # Step 3: Per-image inference + consistency check + CSV export
    # ------------------------------------------------------------------
    EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

    consistency_records = []
    misclassified_records = []
    correct_samples = []
    misclassified_normal_samples = []

    print("\n[Step 2] Running per-image TF-native inference & consistency check...")

    for img_path in image_paths:
        batch_arr = tf_load_image(img_path)
        preds = model.predict(batch_arr, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        pred_cls = CLASS_NAMES[pred_idx]
        confidence = float(preds[pred_idx])

        # Map path to what image_dataset_from_directory recorded
        img_path_str = str(img_path.resolve())
        eval_cls = eval_pred_map.get(img_path_str, "N/A")
        eval_conf = eval_conf_map.get(img_path_str, float("nan"))
        match_status = "MATCH" if pred_cls == eval_cls else "DIFFERENT"

        consistency_records.append({
            "filename": img_path.name,
            "actual_class": "Cell_Crack",
            "evaluate_predicted_class": eval_cls,
            "analysis_predicted_class": pred_cls,
            "evaluate_confidence": f"{eval_conf:.6f}",
            "analysis_confidence": f"{confidence:.6f}",
            "match_status": match_status,
        })

        record = {
            "filename": img_path.name,
            "actual_class": "Cell_Crack",
            "predicted_class": pred_cls,
            "confidence": f"{confidence * 100:.2f}%",
            "prob_Cell_Crack": f"{preds[0]:.6f}",
            "prob_Hotspot": f"{preds[1]:.6f}",
            "prob_Normal": f"{preds[2]:.6f}",
            "path": img_path,
        }

        if pred_cls != "Cell_Crack":
            misclassified_records.append(record)
            if pred_cls == "Normal":
                misclassified_normal_samples.append((img_path, record, preds))
        else:
            correct_samples.append((img_path, record, preds))

    # ------------------------------------------------------------------
    # Consistency summary
    # ------------------------------------------------------------------
    total_tested = len(consistency_records)
    matching = sum(1 for r in consistency_records if r["match_status"] == "MATCH")
    different = total_tested - matching

    print(f"\n{'=' * 50}")
    print(f"CONSISTENCY CHECK RESULTS")
    print(f"{'=' * 50}")
    print(f"  TOTAL TESTED          : {total_tested}")
    print(f"  NUMBER MATCHING       : {matching}")
    print(f"  NUMBER DIFFERENT      : {different}")

    if different > 0:
        print(f"\n  [WARNING] {different} image(s) have different predictions "
              f"between the two methods!")
        for r in consistency_records:
            if r["match_status"] == "DIFFERENT":
                print(f"    {r['filename']}: evaluate={r['evaluate_predicted_class']}, "
                      f"analysis={r['analysis_predicted_class']}")
    else:
        print(f"\n  [OK] All {total_tested} Cell_Crack predictions are consistent "
              f"with evaluate.py output.")

    # ------------------------------------------------------------------
    # Save prediction_consistency_check.csv
    # ------------------------------------------------------------------
    consistency_csv_path = EVALUATION_DIR / "prediction_consistency_check.csv"
    consistency_fieldnames = [
        "filename",
        "actual_class",
        "evaluate_predicted_class",
        "analysis_predicted_class",
        "evaluate_confidence",
        "analysis_confidence",
        "match_status",
    ]
    with open(consistency_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=consistency_fieldnames)
        writer.writeheader()
        writer.writerows(consistency_records)
    print(f"\n[OK] Saved prediction consistency CSV to:\n  {consistency_csv_path}")

    # ------------------------------------------------------------------
    # Analysis Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * 50}")
    print(f"ANALYSIS SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Total Cell_Crack Test Samples : {total_tested}")
    print(f"  Correctly Predicted           : {len(correct_samples)}")
    print(f"  Total Misclassified           : {len(misclassified_records)}")
    miss_hotspot = sum(1 for r in misclassified_records if r["predicted_class"] == "Hotspot")
    miss_normal = sum(1 for r in misclassified_records if r["predicted_class"] == "Normal")
    print(f"  Misclassified as 'Hotspot'   : {miss_hotspot}")
    print(f"  Misclassified as 'Normal'    : {miss_normal}")

    # ------------------------------------------------------------------
    # Save misclassified_samples.csv
    # ------------------------------------------------------------------
    csv_path = EVALUATION_DIR / "misclassified_samples.csv"
    fieldnames = [
        "filename",
        "actual_class",
        "predicted_class",
        "confidence",
        "prob_Cell_Crack",
        "prob_Hotspot",
        "prob_Normal",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in misclassified_records:
            row = {k: rec[k] for k in fieldnames}
            writer.writerow(row)
    print(f"[OK] Saved misclassified records to CSV:\n  {csv_path}")

    # ------------------------------------------------------------------
    # Visual Summary: cell_crack_error_analysis.png
    # ------------------------------------------------------------------
    num_pairs = min(4, len(correct_samples), len(misclassified_normal_samples))
    if num_pairs == 0:
        print("Warning: Insufficient samples for side-by-side visual analysis.")
        return

    print(f"\n[Step 3] Generating Grad-CAM error analysis figure "
          f"({num_pairs} sample pairs)...")

    fig, axes = plt.subplots(num_pairs * 2, 3, figsize=(13, 3.5 * num_pairs * 2))

    for idx in range(num_pairs):
        # Correct sample
        corr_img_path, corr_rec, _ = correct_samples[idx]
        corr_arr = tf_load_image(corr_img_path)
        corr_heatmap = make_gradcam_heatmap(corr_arr, model, pred_index=0)
        c_orig, c_heat, c_overlay = save_gradcam_overlay(corr_img_path, corr_heatmap)

        r_corr = idx * 2
        axes[r_corr, 0].imshow(c_orig)
        axes[r_corr, 0].set_title(
            f"[CORRECT] Actual: Cell_Crack\nFile: {corr_img_path.name}",
            fontsize=10, color="green")
        axes[r_corr, 0].axis("off")

        axes[r_corr, 1].imshow(c_heat)
        axes[r_corr, 1].set_title("Grad-CAM Heatmap (Cell_Crack)", fontsize=10)
        axes[r_corr, 1].axis("off")

        axes[r_corr, 2].imshow(c_overlay)
        axes[r_corr, 2].set_title(
            f"Pred: Cell_Crack ({corr_rec['confidence']})\n"
            f"Normal prob: {corr_rec['prob_Normal']}",
            fontsize=10)
        axes[r_corr, 2].axis("off")

        # Misclassified sample (predicted as Normal)
        err_img_path, err_rec, _ = misclassified_normal_samples[idx]
        err_arr = tf_load_image(err_img_path)
        err_heatmap = make_gradcam_heatmap(err_arr, model, pred_index=2)
        e_orig, e_heat, e_overlay = save_gradcam_overlay(err_img_path, err_heatmap)

        r_err = idx * 2 + 1
        axes[r_err, 0].imshow(e_orig)
        axes[r_err, 0].set_title(
            f"[MISCLASSIFIED] Actual: Cell_Crack\nFile: {err_img_path.name}",
            fontsize=10, color="red")
        axes[r_err, 0].axis("off")

        axes[r_err, 1].imshow(e_heat)
        axes[r_err, 1].set_title("Grad-CAM Heatmap (Normal Score)", fontsize=10)
        axes[r_err, 1].axis("off")

        axes[r_err, 2].imshow(e_overlay)
        axes[r_err, 2].set_title(
            f"Pred: NORMAL ({err_rec['confidence']})\n"
            f"Cell_Crack prob: {err_rec['prob_Cell_Crack']}",
            fontsize=10)
        axes[r_err, 2].axis("off")

    plt.tight_layout()
    analysis_plot_path = EVALUATION_DIR / "cell_crack_error_analysis.png"
    plt.savefig(analysis_plot_path, dpi=300)
    plt.close()

    print(f"[OK] Saved visual error analysis plot to:\n  {analysis_plot_path}")
    print("\nCell_Crack Error Analysis complete.")


if __name__ == "__main__":
    run_cell_crack_error_analysis()
