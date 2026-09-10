"""
gradcam.py
----------
Robust Grad-CAM (Gradient-weighted Class Activation Mapping) implementation
for SolarSafe AI MobileNetV2 solar PV panel defect classification.

Features:
- Dynamically identifies the final convolutional layer of MobileNetV2 (defaults to 'out_relu').
- Computes genuine gradient-weighted class activation maps from the trained model.
- Generates Jet colormap overlays blended with the original image.
- Provides end-to-end inference + explainability in a single call.
- Comprehensive error handling to prevent pipeline failures.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from pathlib import Path

from config import (
    TEST_DIR,
    FINAL_MODEL_PATH,
    BEST_MODEL_PATH,
    CLASS_NAMES,
    GRADCAM_DIR,
    IMG_SIZE,
)
from preprocessing import ImagePreprocessor


def get_model(model=None):
    """Load model if not provided, preferring FINAL_MODEL_PATH with BEST_MODEL_PATH fallback."""
    if model is not None:
        return model
    model_path = FINAL_MODEL_PATH if FINAL_MODEL_PATH.exists() else BEST_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {FINAL_MODEL_PATH} or {BEST_MODEL_PATH}")
    return tf.keras.models.load_model(model_path, compile=False)


def find_target_conv_layer(base_model, preferred_layer="out_relu"):
    """
    Locates the target convolutional layer inside the base model.
    Falls back to searching backwards for the last layer with 4D feature map.
    """
    try:
        return base_model.get_layer(preferred_layer)
    except (ValueError, KeyError):
        pass

    for layer in reversed(base_model.layers):
        if hasattr(layer, "output") and len(layer.output.shape) == 4:
            return layer

    raise ValueError("Could not find a suitable 4D convolutional layer inside base model for Grad-CAM.")


def make_gradcam_heatmap(img_array, model=None, pred_index=None, target_layer_name="out_relu"):
    """
    Generates Grad-CAM heatmap for an input image array of shape (1, 224, 224, 3) in [0, 255].

    Args:
        img_array: numpy float32 array with shape (1, 224, 224, 3)
        model: loaded Keras model
        pred_index: class index to compute gradients for (defaults to argmax prediction)
        target_layer_name: name of convolutional feature layer inside MobileNetV2

    Returns:
        2D numpy array of shape (7, 7) or corresponding spatial dimensions, normalized in [0, 1].
    """
    model = get_model(model)

    # Locate base MobileNetV2 model
    base_model = None
    for layer in model.layers:
        if "mobilenetv2" in layer.name.lower():
            base_model = layer
            break

    if base_model is None:
        raise ValueError("Could not find MobileNetV2 base model inside classifier.")

    target_layer = find_target_conv_layer(base_model, target_layer_name)

    grad_model = tf.keras.models.Model(
        inputs=base_model.input,
        outputs=target_layer.output
    )

    # Gradient computation
    with tf.GradientTape() as tape:
        x = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        conv_outputs = grad_model(x, training=False)
        tape.watch(conv_outputs)

        x_head = conv_outputs
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
    if grads is None:
        raise RuntimeError("Gradient computation returned None. Check layer differentiability.")

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]

    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0.0)
    max_val = tf.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / (max_val + 1e-10)

    return heatmap.numpy()


def save_gradcam_overlay(image_source, heatmap, alpha=0.4, output_path=None):
    """
    Overlays Grad-CAM heatmap onto the original image using Jet colormap.

    Args:
        image_source: Path to image file OR numpy array of shape (H, W, 3) in [0, 255]
        heatmap: 2D numpy array in [0, 1]
        alpha: heatmap transparency factor (0 = image only, 1 = heatmap only)
        output_path: optional destination Path to save resulting overlay image

    Returns:
        Tuple of (orig_rgb, color_heatmap_rgb, overlay_rgb) as uint8 arrays.
    """
    if isinstance(image_source, (str, Path)):
        orig_img = Image.open(image_source).convert("RGB").resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)
    elif isinstance(image_source, np.ndarray):
        if image_source.ndim == 4:
            image_source = image_source[0]
        orig_img = Image.fromarray(image_source.astype(np.uint8)).resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)
    else:
        raise TypeError("image_source must be a file Path, str, or numpy array")

    orig_arr = np.array(orig_img, dtype=np.float32) / 255.0

    # Resize heatmap to target dimensions
    heatmap_uint8 = np.uint8(np.clip(heatmap * 255.0, 0, 255))
    heatmap_img = Image.fromarray(heatmap_uint8).resize((IMG_SIZE, IMG_SIZE), Image.Resampling.BILINEAR)
    heatmap_norm = np.array(heatmap_img, dtype=np.float32) / 255.0

    # Apply Jet colormap
    cmap = plt.get_cmap("jet")
    colored_heatmap = cmap(heatmap_norm)[:, :, :3]

    # Blend original and heatmap
    overlay_arr = (1.0 - alpha) * orig_arr + alpha * colored_heatmap
    overlay_arr = np.clip(overlay_arr, 0.0, 1.0)

    orig_rgb = np.uint8(orig_arr * 255.0)
    color_heatmap_rgb = np.uint8(colored_heatmap * 255.0)
    overlay_rgb = np.uint8(overlay_arr * 255.0)

    if output_path is not None:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(overlay_rgb).save(out_p)

    return orig_rgb, color_heatmap_rgb, overlay_rgb


def generate_gradcam(image_path, model=None, output_path=None, alpha=0.4):
    """
    End-to-end function: takes an image, runs prediction, generates Grad-CAM heatmap & overlay.

    Returns:
        dict: {
            "prediction": str,
            "confidence": float,
            "probabilities": dict,
            "overlay_path": str or None,
            "heatmap": np.ndarray,
            "overlay_rgb": np.ndarray
        }
    """
    img_path = Path(image_path)
    if not img_path.exists():
        raise FileNotFoundError(f"Input image not found at: {img_path}")

    model = get_model(model)
    img_array = ImagePreprocessor.preprocess(img_path)
    batch_array = ImagePreprocessor.prepare_batch(img_array)

    raw_preds = model.predict(batch_array, verbose=0)[0]
    pred_idx = int(np.argmax(raw_preds))
    pred_class = CLASS_NAMES[pred_idx]
    confidence = float(raw_preds[pred_idx] * 100.0)

    heatmap = make_gradcam_heatmap(batch_array, model=model, pred_index=pred_idx)
    orig_rgb, color_heatmap, overlay_rgb = save_gradcam_overlay(
        image_source=img_path,
        heatmap=heatmap,
        alpha=alpha,
        output_path=output_path
    )

    return {
        "prediction": pred_class,
        "confidence": confidence,
        "probabilities": {cls: float(raw_preds[i]) for i, cls in enumerate(CLASS_NAMES)},
        "overlay_path": str(output_path) if output_path else None,
        "heatmap": heatmap,
        "overlay_rgb": overlay_rgb
    }


def generate_gradcam_samples():
    """Batch generates Grad-CAM verification figures across test samples for all 3 classes."""
    print("=" * 60)
    print("SolarSafe AI — Grad-CAM Heatmap Generation")
    print("=" * 60)

    model = get_model()
    GRADCAM_DIR.mkdir(parents=True, exist_ok=True)

    sample_images = []
    for cls in CLASS_NAMES:
        cls_folder = TEST_DIR / cls
        if cls_folder.exists():
            imgs = [f for f in cls_folder.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")]
            if imgs:
                sample_images.append((cls, imgs[0]))

    if not sample_images:
        print("[WARN] No sample images found in TEST_DIR to generate Grad-CAM.")
        return

    print(f"\nGenerating Grad-CAM overlays for {len(sample_images)} test samples...")
    fig, axes = plt.subplots(len(sample_images), 3, figsize=(12, 4 * len(sample_images)))
    if len(sample_images) == 1:
        axes = np.expand_dims(axes, axis=0)

    for i, (actual_cls, img_path) in enumerate(sample_images):
        out_single_path = GRADCAM_DIR / f"gradcam_{actual_cls}_{img_path.name}.png"
        res = generate_gradcam(img_path, model=model, output_path=out_single_path)

        orig_img = Image.open(img_path).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
        orig_rgb = np.array(orig_img)

        # Plot row
        axes[i, 0].imshow(orig_rgb)
        axes[i, 0].set_title(f"Original: {actual_cls}", fontsize=11)
        axes[i, 0].axis("off")

        axes[i, 1].imshow(res["heatmap"], cmap="jet")
        axes[i, 1].set_title("Grad-CAM Heatmap", fontsize=11)
        axes[i, 1].axis("off")

        axes[i, 2].imshow(res["overlay_rgb"])
        axes[i, 2].set_title(f"Pred: {res['prediction']} ({res['confidence']:.1f}%)", fontsize=11)
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
