"""
gradcam_v2.py
-------------
SolarSafe AI V2 — Grad-CAM Comparison Script.

Generates side-by-side Grad-CAM visualizations comparing:
  V1 | V2-A | V2-B

For four image categories:
  1. Correctly classified Cell_Crack
  2. Hard Cell_Crack (V1 predicted as Normal)
  3. Normal (correctly classified)
  4. Hotspot (correctly classified)

Output:
  ai/outputs/experiments/v2/gradcam_comparison/
    cell_crack_correct_comparison.png
    cell_crack_hard_comparison.png
    normal_comparison.png
    hotspot_comparison.png

Each figure shows:
  [Original] [V1 Grad-CAM] [V2-A Grad-CAM] [V2-B Grad-CAM]
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import sys
import numpy as np
import tensorflow as tf

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from pathlib import Path
from PIL import Image


# ============================================================
# PROJECT IMPORTS
# ============================================================

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    TEST_DIR,
    IMG_SIZE,
    BATCH_SIZE,
    CLASS_NAMES,
    OUTPUTS_DIR,
    CHECKPOINT_DIR,
)

from focal_loss import FocalLoss


# ============================================================
# PATHS
# ============================================================

EXPERIMENTS_DIR = OUTPUTS_DIR / "experiments" / "v2"

GRADCAM_OUT_DIR = (
    EXPERIMENTS_DIR
    / "gradcam_comparison"
)

MODEL_PATHS = {
    "V1": CHECKPOINT_DIR / "best_model.keras",

    "V2-A": (
        EXPERIMENTS_DIR
        / "v2_a_augmentation"
        / "best_model_v2a.keras"
    ),

    "V2-B": (
        EXPERIMENTS_DIR
        / "v2_b_focal"
        / "best_model_v2b.keras"
    ),
}

SAMPLES_PER_CATEGORY = 4


# ============================================================
# TF-NATIVE IMAGE LOADER
# Matches image_dataset_from_directory preprocessing
# ============================================================

def tf_load_image(image_path: Path) -> np.ndarray:
    """
    Load an image using TensorFlow.

    Returns:
        numpy array of shape:
        (IMG_SIZE, IMG_SIZE, 3)
    """

    img_bytes = tf.io.read_file(str(image_path))

    img = tf.image.decode_image(
        img_bytes,
        channels=3,
        expand_animations=False,
    )

    img = tf.image.resize(
        img,
        (IMG_SIZE, IMG_SIZE),
        method="bilinear",
    )

    return img.numpy()


def load_batch(image_path: Path) -> np.ndarray:
    """
    Return image as batch.

    Shape:
        (1, IMG_SIZE, IMG_SIZE, 3)
    """

    img = tf_load_image(image_path)

    return np.expand_dims(img, axis=0)


# ============================================================
# MODEL INSPECTION
# ============================================================

def find_mobilenet_backbone(model):
    """
    Find the nested MobileNetV2 backbone inside
    the complete classification model.
    """

    # First try using the layer name
    for layer in model.layers:

        if (
            hasattr(layer, "layers")
            and "mobilenet" in layer.name.lower()
        ):
            return layer

    # Fallback:
    # find a nested Keras model containing MobileNet-style layers
    for layer in model.layers:

        if isinstance(layer, tf.keras.Model):

            layer_names = [
                sublayer.name.lower()
                for sublayer in layer.layers
            ]

            if any(
                "block_" in name
                or "out_relu" in name
                for name in layer_names
            ):
                return layer

    raise ValueError(
        "Could not find MobileNetV2 backbone "
        "inside the model."
    )


def find_target_layer(
    base_model,
    preferred_name="out_relu",
):
    """
    Find the target layer for Grad-CAM.

    First preference:
        out_relu

    Otherwise:
        last Conv2D / DepthwiseConv2D layer.
    """

    # Try preferred layer
    try:

        return base_model.get_layer(preferred_name)

    except ValueError:
        pass

    # Fallback:
    # search backwards for convolutional layer
    for layer in reversed(base_model.layers):

        if isinstance(
            layer,
            (
                tf.keras.layers.Conv2D,
                tf.keras.layers.DepthwiseConv2D,
            ),
        ):

            return layer

    raise ValueError(
        "Could not find a suitable convolutional "
        "layer for Grad-CAM."
    )


# ============================================================
# GRAD-CAM IMPLEMENTATION
# ============================================================

def make_gradcam_heatmap(
    img_array: np.ndarray,
    model,
    pred_index: int = None,
) -> np.ndarray:
    """
    Generate Grad-CAM heatmap.

    This implementation supports a classification model
    containing a nested MobileNetV2 backbone.

    Args:
        img_array:
            Image batch with shape:
            (1, H, W, 3)

        model:
            Full trained Keras model.

        pred_index:
            Class index for Grad-CAM.

            If None, use predicted class.

    Returns:
        Heatmap as float32 numpy array
        normalized to range [0, 1].
    """

    # --------------------------------------------------------
    # Find MobileNetV2 backbone
    # --------------------------------------------------------

    base_model = find_mobilenet_backbone(model)

    # --------------------------------------------------------
    # Find target convolution layer
    # --------------------------------------------------------

    target_layer = find_target_layer(
        base_model,
        preferred_name="out_relu",
    )

    # --------------------------------------------------------
    # Find backbone position in the outer model
    # --------------------------------------------------------

    backbone_index = None

    for i, layer in enumerate(model.layers):

        if layer is base_model:

            backbone_index = i
            break

    if backbone_index is None:

        raise ValueError(
            "Could not locate MobileNetV2 backbone "
            "inside outer model."
        )

    # --------------------------------------------------------
    # Layers after MobileNetV2
    #
    # These are the classifier layers.
    # --------------------------------------------------------

    classifier_layers = model.layers[
        backbone_index + 1:
    ]

    # --------------------------------------------------------
    # Build model ONLY from MobileNet input
    #
    # Output:
    #   1. target convolution activation
    #   2. MobileNet feature output
    #
    # This avoids mixing nested-model tensors with
    # outer-model inputs.
    # --------------------------------------------------------

    grad_model = tf.keras.Model(

        inputs=base_model.input,

        outputs=[
            target_layer.output,
            base_model.output,
        ],

    )

    # --------------------------------------------------------
    # Prepare image
    # --------------------------------------------------------

    img_tensor = tf.cast(
        img_array,
        tf.float32,
    )

    # --------------------------------------------------------
    # Forward pass and gradient calculation
    # --------------------------------------------------------

    with tf.GradientTape() as tape:

        # Run MobileNetV2
        conv_outputs, features = grad_model(
            img_tensor,
            training=False,
        )

        # Important:
        # Watch convolution activations
        tape.watch(conv_outputs)

        # ----------------------------------------------------
        # Pass backbone features through remaining
        # classifier layers
        # ----------------------------------------------------

        x = features

        for layer in classifier_layers:

            x = layer(
                x,
                training=False,
            )

        predictions = x

        # ----------------------------------------------------
        # Determine target class
        # ----------------------------------------------------

        if pred_index is None:

            pred_index = int(
                tf.argmax(
                    predictions[0]
                )
            )

        # Score for selected class
        class_score = predictions[
            :,
            pred_index
        ]

    # --------------------------------------------------------
    # Calculate gradients
    # --------------------------------------------------------

    grads = tape.gradient(
        class_score,
        conv_outputs,
    )

    if grads is None:

        raise ValueError(
            "Gradients are None. "
            "Unable to compute Grad-CAM."
        )

    # --------------------------------------------------------
    # Global average pooling of gradients
    # --------------------------------------------------------

    pooled_grads = tf.reduce_mean(

        grads,

        axis=(
            0,
            1,
            2,
        ),

    )

    # --------------------------------------------------------
    # Remove batch dimension
    # --------------------------------------------------------

    conv_outputs = conv_outputs[0]

    # --------------------------------------------------------
    # Weight feature maps
    # --------------------------------------------------------

    heatmap = tf.reduce_sum(

        conv_outputs
        * pooled_grads,

        axis=-1,

    )

    # --------------------------------------------------------
    # ReLU
    # --------------------------------------------------------

    heatmap = tf.nn.relu(
        heatmap
    )

    heatmap = heatmap.numpy()

    # --------------------------------------------------------
    # Normalize heatmap
    # --------------------------------------------------------

    max_value = np.max(
        heatmap
    )

    if max_value > 0:

        heatmap = (
            heatmap
            / max_value
        )

    return heatmap.astype(
        np.float32
    )


# ============================================================
# HEATMAP OVERLAY
# ============================================================

def overlay_heatmap(
    original_img_path: Path,
    heatmap: np.ndarray,
    alpha: float = 0.45,
):
    """
    Create original image, colored heatmap,
    and Grad-CAM overlay.

    Returns:
        orig_arr,
        heatmap_colored,
        overlay
    """

    orig = Image.open(
        original_img_path
    ).convert(
        "RGB"
    ).resize(
        (
            IMG_SIZE,
            IMG_SIZE,
        )
    )

    orig_arr = np.array(
        orig,
        dtype=np.uint8,
    )

    # Resize heatmap
    heatmap_uint8 = (
        heatmap * 255
    ).astype(
        np.uint8
    )

    heatmap_resized = np.array(

        Image.fromarray(
            heatmap_uint8
        ).resize(

            (
                IMG_SIZE,
                IMG_SIZE,
            ),

            Image.Resampling.BILINEAR,

        )

    ).astype(
        np.float32
    ) / 255.0

    # --------------------------------------------------------
    # Colorize heatmap
    # --------------------------------------------------------

    colormap = plt.get_cmap(
        "jet"
    )

    heatmap_colored = (

        colormap(
            heatmap_resized
        )[
            :,
            :,
            :3,
        ]

        * 255

    ).astype(
        np.uint8
    )

    # --------------------------------------------------------
    # Blend
    # --------------------------------------------------------

    overlay = (

        alpha
        * heatmap_colored

        +

        (1 - alpha)
        * orig_arr

    ).clip(
        0,
        255,
    ).astype(
        np.uint8
    )

    return (
        orig_arr,
        heatmap_colored,
        overlay,
    )


# ============================================================
# SAMPLE COLLECTION
# ============================================================

def collect_samples(
    test_ds,
    models: dict,
    category: str,
    n: int = 4,
):
    """
    Collect samples for comparison.

    Categories:

    correct_cc
        Actual Cell_Crack
        All models predict Cell_Crack

    hard_cc
        Actual Cell_Crack
        V1 predicts Normal

    normal
        Actual Normal
        V1 predicts Normal

    hotspot
        Actual Hotspot
        V1 predicts Hotspot
    """

    file_paths = test_ds.file_paths

    y_true_all = []

    preds_all = {
        label: []
        for label in models
    }

    # --------------------------------------------------------
    # Get true labels
    # --------------------------------------------------------

    for _, labels in test_ds:

        y_true_all.extend(

            np.argmax(
                labels.numpy(),
                axis=1,
            )

        )

    # --------------------------------------------------------
    # Get predictions for each model
    # --------------------------------------------------------

    for label, model in models.items():

        probs = model.predict(
            test_ds,
            verbose=0,
        )

        preds_all[label] = np.argmax(
            probs,
            axis=1,
        ).tolist()

    y_true_all = np.array(
        y_true_all
    )

    # --------------------------------------------------------
    # Class indices
    # --------------------------------------------------------

    CC_IDX = CLASS_NAMES.index(
        "Cell_Crack"
    )

    NR_IDX = CLASS_NAMES.index(
        "Normal"
    )

    HS_IDX = CLASS_NAMES.index(
        "Hotspot"
    )

    samples = []

    # --------------------------------------------------------
    # Select samples
    # --------------------------------------------------------

    for i, (
        fp,
        yt,
    ) in enumerate(
        zip(
            file_paths,
            y_true_all,
        )
    ):

        if len(samples) >= n:

            break

        v1_pred = preds_all[
            "V1"
        ][i]

        # ----------------------------------------------------
        # Category selection
        # ----------------------------------------------------

        if category == "correct_cc":

            if not (
                yt == CC_IDX
                and all(
                    preds_all[key][i]
                    == CC_IDX
                    for key in models
                )
            ):

                continue

        elif category == "hard_cc":

            if not (
                yt == CC_IDX
                and v1_pred == NR_IDX
            ):

                continue

        elif category == "normal":

            if not (
                yt == NR_IDX
                and v1_pred == NR_IDX
            ):

                continue

        elif category == "hotspot":

            if not (
                yt == HS_IDX
                and v1_pred == HS_IDX
            ):

                continue

        else:

            raise ValueError(
                f"Unknown category: {category}"
            )

        # ----------------------------------------------------
        # Store predictions
        # ----------------------------------------------------

        per_model = {

            label: (

                preds_all[label][i],

                CLASS_NAMES[
                    preds_all[label][i]
                ],

            )

            for label in models

        }

        samples.append(

            (
                Path(fp),
                CLASS_NAMES[yt],
                per_model,
            )

        )

    return samples


# ============================================================
# PLOT GENERATION
# ============================================================

def generate_comparison_figure(
    samples: list,
    models: dict,
    category_title: str,
    out_path: Path,
    heatmap_class_idx: int = None,
):
    """
    Generate Grad-CAM comparison figure.

    Layout:

        Original
        V1 Grad-CAM
        V2-A Grad-CAM
        V2-B Grad-CAM
    """

    if not samples:

        print(
            f"[SKIP] No samples found for category: "
            f"{category_title}"
        )

        return

    model_labels = list(
        models.keys()
    )

    n_rows = len(
        samples
    )

    n_cols = (
        1
        + len(model_labels)
    )

    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    fig, axes = plt.subplots(

        n_rows,
        n_cols,

        figsize=(
            4 * n_cols,
            3.5 * n_rows,
        ),

        squeeze=False,

    )

    fig.suptitle(

        "SolarSafe AI — Grad-CAM Comparison\n"
        f"{category_title}",

        fontsize=12,

        fontweight="bold",

        y=1.01,

    )

    # --------------------------------------------------------
    # Process samples
    # --------------------------------------------------------

    for row_idx, (
        img_path,
        actual_cls,
        per_model,
    ) in enumerate(
        samples
    ):

        img_batch = load_batch(
            img_path
        )

        # ----------------------------------------------------
        # Original image
        # ----------------------------------------------------

        ax = axes[
            row_idx,
            0,
        ]

        orig_arr = np.array(

            Image.open(
                img_path
            ).convert(
                "RGB"
            ).resize(
                (
                    IMG_SIZE,
                    IMG_SIZE,
                )
            )

        )

        ax.imshow(
            orig_arr
        )

        ax.set_title(

            f"Original\n"
            f"Actual: {actual_cls}",

            fontsize=8,

            color="black",

        )

        ax.axis(
            "off"
        )

        # ----------------------------------------------------
        # Grad-CAM for each model
        # ----------------------------------------------------

        for col_idx, label in enumerate(
            model_labels
        ):

            model = models[
                label
            ]

            if heatmap_class_idx is not None:

                pred_idx_for_cam = (
                    heatmap_class_idx
                )

            else:

                pred_idx_for_cam = (
                    per_model[label][0]
                )

            try:

                heatmap = make_gradcam_heatmap(

                    img_batch,

                    model,

                    pred_index=pred_idx_for_cam,

                )

                _, _, overlay = overlay_heatmap(

                    img_path,

                    heatmap,

                )

            except Exception as e:

                print(

                    f"  [WARN] Grad-CAM failed for "
                    f"{label}/{img_path.name}: {e}"

                )

                overlay = orig_arr.copy()

            # ------------------------------------------------
            # Prediction label
            # ------------------------------------------------

            pred_cls = per_model[
                label
            ][1]

            correct = (
                pred_cls
                == actual_cls
            )

            color = (
                "green"
                if correct
                else "red"
            )

            # ------------------------------------------------
            # Plot
            # ------------------------------------------------

            ax = axes[
                row_idx,
                col_idx + 1,
            ]

            ax.imshow(
                overlay
            )

            ax.set_title(

                f"{label}\n"
                f"Pred: {pred_cls}",

                fontsize=8,

                color=color,

                fontweight=(
                    "normal"
                    if correct
                    else "bold"
                ),

            )

            ax.axis(
                "off"
            )

    # --------------------------------------------------------
    # Save figure
    # --------------------------------------------------------

    plt.tight_layout()

    out_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    plt.savefig(

        out_path,

        dpi=150,

        bbox_inches="tight",

    )

    plt.close()

    print(
        f"[OK] Saved Grad-CAM figure: "
        f"{out_path}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "=" * 65
    )

    print(
        "SolarSafe AI V2 — Grad-CAM Comparison"
    )

    print(
        "=" * 65
    )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    GRADCAM_OUT_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    # --------------------------------------------------------
    # Load models
    # --------------------------------------------------------

    models = {}

    for label, path in MODEL_PATHS.items():

        if path.exists():

            print(
                f"Loading {label} from {path}..."
            )

            models[label] = tf.keras.models.load_model(

                str(path),

                custom_objects={
                    "FocalLoss": FocalLoss
                },

            )

            print(
                f"[OK] {label} loaded."
            )

        else:

            print(
                f"[SKIP] {label} model not found: "
                f"{path}"
            )

    if not models:

        print(
            "[ERROR] No models found. "
            "Run training first."
        )

        return

    # --------------------------------------------------------
    # Load test dataset
    # --------------------------------------------------------

    print(
        "\nLoading test dataset..."
    )

    test_ds = (
        tf.keras.utils.image_dataset_from_directory(

            TEST_DIR,

            labels="inferred",

            label_mode="categorical",

            image_size=(
                IMG_SIZE,
                IMG_SIZE,
            ),

            batch_size=BATCH_SIZE,

            shuffle=False,

        )
    )

    assert (
        test_ds.class_names
        == CLASS_NAMES
    ), (
        f"Class mismatch: "
        f"{test_ds.class_names}"
    )

    print(
        f"[OK] Class order: "
        f"{test_ds.class_names}"
    )

    # --------------------------------------------------------
    # Class indices
    # --------------------------------------------------------

    CC_IDX = CLASS_NAMES.index(
        "Cell_Crack"
    )

    NR_IDX = CLASS_NAMES.index(
        "Normal"
    )

    HS_IDX = CLASS_NAMES.index(
        "Hotspot"
    )

    # --------------------------------------------------------
    # Categories
    # --------------------------------------------------------

    categories = [

        (
            "correct_cc",

            "Correct Cell_Crack "
            "(all models correct)",

            CC_IDX,

            GRADCAM_OUT_DIR
            / "cell_crack_correct_comparison.png",
        ),

        (
            "hard_cc",

            "Hard Cell_Crack "
            "(V1 misclassified as Normal)",

            CC_IDX,

            GRADCAM_OUT_DIR
            / "cell_crack_hard_comparison.png",
        ),

        (
            "normal",

            "Normal "
            "(correctly classified)",

            NR_IDX,

            GRADCAM_OUT_DIR
            / "normal_comparison.png",
        ),

        (
            "hotspot",

            "Hotspot "
            "(correctly classified)",

            HS_IDX,

            GRADCAM_OUT_DIR
            / "hotspot_comparison.png",
        ),

    ]

    # --------------------------------------------------------
    # Generate comparisons
    # --------------------------------------------------------

    for (
        cat_key,
        cat_title,
        cam_cls_idx,
        out_path,
    ) in categories:

        print(
            f"\n--- Category: "
            f"{cat_title} ---"
        )

        samples = collect_samples(

            test_ds=test_ds,

            models=models,

            category=cat_key,

            n=SAMPLES_PER_CATEGORY,

        )

        print(
            f"  Found "
            f"{len(samples)} samples."
        )

        generate_comparison_figure(

            samples=samples,

            models=models,

            category_title=cat_title,

            out_path=out_path,

            heatmap_class_idx=cam_cls_idx,

        )

    print(

        f"\n[DONE] Grad-CAM comparison complete. "
        f"Output: {GRADCAM_OUT_DIR}"

    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()