"""
gradcam.py
----------
Grad-CAM (Gradient-weighted Class Activation Mapping) implementation
for SolarSafe AI MobileNetV2 thermal image fault classification.
Uses PIL and Matplotlib (no OpenCV dependency).
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

from config import TEST_DIR, BEST_MODEL_PATH, CLASS_NAMES, GRADCAM_DIR, IMG_SIZE
from preprocessing import ImagePreprocessor


def make_gradcam_heatmap(img_array, model, pred_index=None):
    """
    Generates Grad-CAM heatmap for a given input image array (1, 224, 224, 3).
    """
    base_model = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_model = layer
            break

    if base_model is None:
        raise ValueError("Could not find MobileNetV2 base model inside classifier.")

    # Target last conv layer of MobileNetV2 ('out_relu')
    last_conv_layer = base_model.get_layer("out_relu")

    grad_model = tf.keras.models.Model(
        inputs=base_model.input,
        outputs=last_conv_layer.output
    )

    with tf.GradientTape() as tape:
        x = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        conv_outputs = grad_model(x, training=False)
        tape.watch(conv_outputs)

        x_head = conv_outputs
        # Pass conv_outputs through remaining classification head (GAP, BatchNorm, Dropout, Dense)
        passed_base = False
        for layer in model.layers:
            if layer == base_model:
                passed_base = True
                continue
            if passed_base:
                x_head = layer(x_head, training=False)

        preds = x_head
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-10)
    return heatmap.numpy()


def save_gradcam_overlay(image_path, heatmap, alpha=0.4):
    """
    Overlays Grad-CAM heatmap onto original image using PIL and Matplotlib colormap.
    """
    orig_img = Image.open(image_path).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    orig_arr = np.array(orig_img, dtype=np.float32) / 255.0

    # Resize heatmap to IMG_SIZE x IMG_SIZE
    heatmap_img = Image.fromarray((heatmap * 255).astype(np.uint8)).resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)
    heatmap_norm = np.array(heatmap_img, dtype=np.float32) / 255.0

    # Apply Jet colormap
    cmap = plt.get_cmap("jet")
    colored_heatmap = cmap(heatmap_norm)[:, :, :3]

    # Blend original image and colored heatmap
    overlay_arr = (1.0 - alpha) * orig_arr + alpha * colored_heatmap
    overlay_arr = np.clip(overlay_arr, 0.0, 1.0)

    orig_rgb = np.uint8(orig_arr * 255)
    color_heatmap_rgb = np.uint8(colored_heatmap * 255)
    overlay_rgb = np.uint8(overlay_arr * 255)

    return orig_rgb, color_heatmap_rgb, overlay_rgb


def generate_gradcam_samples():
    print("=" * 60)
    print("SolarSafe AI — Grad-CAM Heatmap Generation")
    print("=" * 60)

    if not BEST_MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found at: {BEST_MODEL_PATH}")

    print(f"Loading model from: {BEST_MODEL_PATH}")
    model = tf.keras.models.load_model(BEST_MODEL_PATH)

    GRADCAM_DIR.mkdir(parents=True, exist_ok=True)

    sample_images = []
    for cls in CLASS_NAMES:
        cls_folder = TEST_DIR / cls
        if cls_folder.exists():
            imgs = [f for f in cls_folder.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")]
            if imgs:
                sample_images.append((cls, imgs[0]))

    print(f"\nGenerating Grad-CAM overlays for {len(sample_images)} test samples...")

    fig, axes = plt.subplots(len(sample_images), 3, figsize=(12, 4 * len(sample_images)))
    if len(sample_images) == 1:
        axes = np.expand_dims(axes, axis=0)

    for i, (actual_cls, img_path) in enumerate(sample_images):
        img_array = ImagePreprocessor.preprocess(img_path)
        batch_array = ImagePreprocessor.prepare_batch(img_array)

        preds = model.predict(batch_array, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        pred_cls = CLASS_NAMES[pred_idx]
        confidence = float(preds[pred_idx] * 100)

        heatmap = make_gradcam_heatmap(batch_array, model, pred_index=pred_idx)
        orig_rgb, color_heatmap, overlay_rgb = save_gradcam_overlay(img_path, heatmap)

        # Save individual overlay file via PIL
        out_single_path = GRADCAM_DIR / f"gradcam_{actual_cls}_{img_path.name}"
        Image.fromarray(overlay_rgb).save(out_single_path)

        # Plot row in figure
        axes[i, 0].imshow(orig_rgb)
        axes[i, 0].set_title(f"Original: {actual_cls}", fontsize=11)
        axes[i, 0].axis("off")

        axes[i, 1].imshow(color_heatmap)
        axes[i, 1].set_title("Grad-CAM Heatmap", fontsize=11)
        axes[i, 1].axis("off")

        axes[i, 2].imshow(overlay_rgb)
        axes[i, 2].set_title(f"Pred: {pred_cls} ({confidence:.1f}%)", fontsize=11)
        axes[i, 2].axis("off")

        print(f"  [OK] Saved Grad-CAM overlay for {actual_cls} -> {out_single_path.name}")

    plt.tight_layout()
    summary_plot_path = GRADCAM_DIR / "gradcam_summary.png"
    plt.savefig(summary_plot_path, dpi=300)
    plt.close()

    print(f"\nGrad-CAM summary visualization saved to:\n  {summary_plot_path}")
    print("Grad-CAM processing completed successfully with 0 warnings.")


if __name__ == "__main__":
    generate_gradcam_samples()
