"""
train_v2.py
-----------
SolarSafe AI V2 — Controlled Experiment Training Script.

Supports two experiments selectable via --experiment flag:

  python train_v2.py --experiment v2a   # V2-A: CE + improved augmentation
  python train_v2.py --experiment v2b   # V2-B: Focal Loss + improved augmentation

Key improvements over V1:
  - More precise augmentation (smaller rotation, added translation, reduced zoom)
  - Deeper fine-tuning: top 50 MobileNetV2 layers (vs V1's top 30)
  - Lower fine-tuning LR: 5e-6 (vs V1's 1e-5)
  - More fine-tune epochs: 25 max with EarlyStopping
  - V2-B uses FocalLoss(gamma=2.0, alpha=[0.4,0.4,0.2]) WITHOUT class_weight dict
    to avoid double-weighting (class_weight alpha is already handled inside focal loss)
  - V2-A retains balanced class_weight dict with standard CE

V1 files are NEVER modified by this script.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import sys
import json
import argparse
import numpy as np
import tensorflow as tf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau, CSVLogger
)
from tensorflow.keras.optimizers import Adam

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    TRAIN_DIR, VALIDATION_DIR, IMG_SIZE, BATCH_SIZE,
    RANDOM_SEED, CLASS_NAMES, NUM_CLASSES, OUTPUTS_DIR,
)
from focal_loss import FocalLoss

# ============================================================
# EXPERIMENT CONFIGURATION
# ============================================================

# Experiment output dirs
EXPERIMENTS_DIR = OUTPUTS_DIR / "experiments" / "v2"

EXPERIMENT_CONFIGS = {
    "v2a": {
        "experiment_name": "V2-A Augmentation + CrossEntropy",
        "output_dir": EXPERIMENTS_DIR / "v2_a_augmentation",
        "model_filename": "best_model_v2a.keras",
        "loss": "categorical_crossentropy",
        "use_class_weights": True,
        "focal_loss_params": None,
        "augmentation": {
            "random_flip": "horizontal_and_vertical",
            "random_rotation": 0.05,
            "random_translation_height": 0.05,
            "random_translation_width": 0.05,
            "random_zoom": 0.08,
            "random_contrast": 0.10,
        },
    },
    "v2b": {
        "experiment_name": "V2-B Augmentation + Focal Loss",
        "output_dir": EXPERIMENTS_DIR / "v2_b_focal",
        "model_filename": "best_model_v2b.keras",
        "loss": "focal_loss",
        "use_class_weights": False,   # Focal alpha handles weighting — no double-weight
        "focal_loss_params": {
            "gamma": 2.0,
            "alpha": [0.4, 0.4, 0.2],   # Cell_Crack, Hotspot, Normal
        },
        "augmentation": {
            "random_flip": "horizontal_and_vertical",
            "random_rotation": 0.05,
            "random_translation_height": 0.05,
            "random_translation_width": 0.05,
            "random_zoom": 0.08,
            "random_contrast": 0.10,
        },
    },
}

# Training hyperparameters (shared)
PHASE1_EPOCHS = 8
PHASE2_MAX_EPOCHS = 25
PHASE1_LR = 1e-4
PHASE2_LR = 5e-6
FINE_TUNE_UNFREEZE_TOP = 50
EARLY_STOP_PATIENCE = 7
REDUCE_LR_PATIENCE = 4
REDUCE_LR_FACTOR = 0.3
MIN_LR = 1e-8


# ============================================================
# BUILD V2 MODEL
# ============================================================

def build_v2_model(augmentation_config: dict):
    """Build MobileNetV2 model with V2-specific targeted augmentation.

    Augmentation is applied inside the model graph (only active during training=True).
    Validates at test time without augmentation — identical to V1's approach.

    Args:
        augmentation_config: Dict with augmentation parameters.

    Returns:
        (model, base_model) tuple.
    """
    tf.random.set_seed(RANDOM_SEED)

    # ---- Targeted augmentation (less aggressive than V1) ----
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip(augmentation_config["random_flip"]),
        layers.RandomRotation(augmentation_config["random_rotation"]),
        layers.RandomTranslation(
            height_factor=augmentation_config["random_translation_height"],
            width_factor=augmentation_config["random_translation_width"],
        ),
        layers.RandomZoom(augmentation_config["random_zoom"]),
        layers.RandomContrast(augmentation_config["random_contrast"]),
    ], name="data_augmentation_v2")

    # ---- MobileNetV2 backbone ----
    base_model = MobileNetV2(
        input_shape=(IMG_SIZE, IMG_SIZE, 3),
        include_top=False,
        weights="imagenet",
    )
    base_model.trainable = False   # Frozen for Phase 1

    # ---- Functional API ----
    inputs = layers.Input(shape=(IMG_SIZE, IMG_SIZE, 3), name="input_layer")
    x = data_augmentation(inputs, training=None)   # training=None: Keras handles train/test
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D(name="gap")(x)
    x = layers.BatchNormalization(name="bn_head")(x)
    x = layers.Dropout(0.4, name="dropout_1")(x)
    x = layers.Dense(
        256,
        activation="relu",
        kernel_regularizer=tf.keras.regularizers.l2(0.001),
        name="dense_head",
    )(x)
    x = layers.BatchNormalization(name="bn_dense")(x)
    x = layers.Dropout(0.3, name="dropout_2")(x)
    outputs = layers.Dense(NUM_CLASSES, activation="softmax", name="output")(x)

    model = models.Model(inputs, outputs, name="SolarSafe_V2")
    return model, base_model


# ============================================================
# DATASETS
# ============================================================

def load_datasets():
    train_ds = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=RANDOM_SEED,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        VALIDATION_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )
    return train_ds, val_ds


def verify_class_order(ds, name: str):
    detected = ds.class_names
    assert detected == CLASS_NAMES, (
        f"[ERROR] {name} class order mismatch!\n"
        f"  Expected: {CLASS_NAMES}\n"
        f"  Detected: {detected}"
    )
    print(f"[OK] {name} class order: {detected}")


def get_class_weights(train_ds):
    labels = []
    for _, y in train_ds.unbatch():
        labels.append(int(np.argmax(y.numpy())))
    labels = np.array(labels)
    weights = compute_class_weight(
        class_weight="balanced",
        classes=np.unique(labels),
        y=labels,
    )
    return {int(c): float(w) for c, w in enumerate(weights)}


# ============================================================
# CALLBACKS
# ============================================================

def build_callbacks(out_dir: Path, model_filename: str, csv_filename: str):
    out_dir.mkdir(parents=True, exist_ok=True)
    return [
        ModelCheckpoint(
            filepath=str(out_dir / model_filename),
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1,
        ),
        EarlyStopping(
            monitor="val_loss",
            patience=EARLY_STOP_PATIENCE,
            restore_best_weights=True,
            verbose=1,
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=REDUCE_LR_FACTOR,
            patience=REDUCE_LR_PATIENCE,
            min_lr=MIN_LR,
            verbose=1,
        ),
        CSVLogger(str(out_dir / csv_filename), append=False),
    ]


# ============================================================
# TRAINING PLOT
# ============================================================

def save_training_plot(history_p1, history_p2, out_dir: Path, title: str):
    acc1  = history_p1.history.get("accuracy", [])
    vacc1 = history_p1.history.get("val_accuracy", [])
    loss1  = history_p1.history.get("loss", [])
    vloss1 = history_p1.history.get("val_loss", [])

    acc2  = history_p2.history.get("accuracy", [])
    vacc2 = history_p2.history.get("val_accuracy", [])
    loss2  = history_p2.history.get("loss", [])
    vloss2 = history_p2.history.get("val_loss", [])

    all_acc   = acc1 + acc2
    all_vacc  = vacc1 + vacc2
    all_loss  = loss1 + loss2
    all_vloss = vloss1 + vloss2
    n_epochs  = len(all_acc)
    phase_boundary = len(acc1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(title, fontsize=13, fontweight="bold")

    epochs = range(1, n_epochs + 1)

    # Accuracy
    ax1.plot(epochs, all_acc,  label="Train Accuracy",  color="#2196F3")
    ax1.plot(epochs, all_vacc, label="Val Accuracy",    color="#FF9800", linestyle="--")
    ax1.axvline(x=phase_boundary + 0.5, color="gray", linestyle=":", linewidth=1.5, label="Fine-tune start")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Accuracy")
    ax1.set_title("Accuracy")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Loss
    ax2.plot(epochs, all_loss,  label="Train Loss",  color="#4CAF50")
    ax2.plot(epochs, all_vloss, label="Val Loss",    color="#F44336", linestyle="--")
    ax2.axvline(x=phase_boundary + 0.5, color="gray", linestyle=":", linewidth=1.5, label="Fine-tune start")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Loss")
    ax2.set_title("Loss")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    out_path = out_dir / "training_plot.png"
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[OK] Training plot saved: {out_path}")


# ============================================================
# SAVE TRAINING HISTORY
# ============================================================

def save_history_json(history_p1, history_p2, out_dir: Path, total_phase1_epochs: int):
    merged = {"phase_1": {}, "phase_2": {}}
    for k, v in history_p1.history.items():
        merged["phase_1"][k] = [float(x) for x in v]
    for k, v in history_p2.history.items():
        merged["phase_2"][k] = [float(x) for x in v]
    merged["phase_1_epochs_completed"] = len(history_p1.history.get("loss", []))
    merged["phase_2_epochs_completed"] = len(history_p2.history.get("loss", []))

    hist_path = out_dir / "training_history.json"
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=4)
    print(f"[OK] Training history saved: {hist_path}")


# ============================================================
# SAVE CONFIG JSON
# ============================================================

def save_config(cfg: dict, experiment_cfg: dict, out_dir: Path,
                class_weights: dict, python_ver: str, tf_ver: str):
    import platform
    config_record = {
        "experiment_name": experiment_cfg["experiment_name"],
        "random_seed": RANDOM_SEED,
        "python_version": python_ver,
        "tensorflow_version": tf_ver,
        "dataset_paths": {
            "train": str(TRAIN_DIR),
            "validation": str(VALIDATION_DIR),
        },
        "class_names": CLASS_NAMES,
        "class_index_order": {n: i for i, n in enumerate(CLASS_NAMES)},
        "image_size": IMG_SIZE,
        "batch_size": BATCH_SIZE,
        "architecture": "MobileNetV2 (ImageNet pretrained) + custom head",
        "fine_tuning_layers_unfrozen": FINE_TUNE_UNFREEZE_TOP,
        "optimizer": "Adam",
        "learning_rates": {
            "phase_1": PHASE1_LR,
            "phase_2": PHASE2_LR,
        },
        "phase_1_planned_epochs": PHASE1_EPOCHS,
        "phase_2_max_epochs": PHASE2_MAX_EPOCHS,
        "early_stopping_patience": EARLY_STOP_PATIENCE,
        "reduce_lr_patience": REDUCE_LR_PATIENCE,
        "reduce_lr_factor": REDUCE_LR_FACTOR,
        "min_lr": MIN_LR,
        "loss_function": experiment_cfg["loss"],
        "focal_loss_parameters": experiment_cfg.get("focal_loss_params"),
        "class_weights_strategy": (
            "sklearn balanced class_weight" if experiment_cfg["use_class_weights"]
            else "None (focal loss alpha handles weighting)"
        ),
        "class_weights_values": class_weights if experiment_cfg["use_class_weights"] else "N/A",
        "augmentation_settings": experiment_cfg["augmentation"],
    }
    config_path = out_dir / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config_record, f, indent=4)
    print(f"[OK] Config saved: {config_path}")


# ============================================================
# MAIN TRAINING ENTRY POINT
# ============================================================

def train(experiment_key: str):
    import sys, platform

    if experiment_key not in EXPERIMENT_CONFIGS:
        print(f"[ERROR] Unknown experiment: {experiment_key}")
        print(f"        Choose from: {list(EXPERIMENT_CONFIGS.keys())}")
        sys.exit(1)

    cfg = EXPERIMENT_CONFIGS[experiment_key]
    out_dir = cfg["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    python_ver = sys.version
    tf_ver = tf.__version__

    print("=" * 65)
    print(f"SolarSafe AI — {cfg['experiment_name']}")
    print("=" * 65)
    print(f"  Python     : {python_ver[:20]}")
    print(f"  TensorFlow : {tf_ver}")
    print(f"  Seed       : {RANDOM_SEED}")
    print(f"  Output dir : {out_dir}")

    # Seeds
    tf.random.set_seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # ---- Load datasets ----
    print("\nLoading datasets...")
    train_ds, val_ds = load_datasets()
    verify_class_order(train_ds, "Train")
    verify_class_order(val_ds,   "Validation")

    train_ds = train_ds.prefetch(tf.data.AUTOTUNE)
    val_ds   = val_ds.prefetch(tf.data.AUTOTUNE)

    # ---- Class weights ----
    if cfg["use_class_weights"]:
        print("\nComputing balanced class weights...")
        class_weights = get_class_weights(train_ds)
        for idx, w in class_weights.items():
            print(f"  {CLASS_NAMES[idx]:12}: {w:.4f}")
    else:
        class_weights = None
        print("\nClass weights: disabled (focal loss alpha handles weighting)")

    # ---- Build model ----
    print("\nBuilding V2 model...")
    model, base_model = build_v2_model(cfg["augmentation"])
    print(f"  MobileNetV2 base layers: {len(base_model.layers)}")

    # ---- Loss function ----
    if cfg["loss"] == "focal_loss":
        fp = cfg["focal_loss_params"]
        loss_fn = FocalLoss(gamma=fp["gamma"], alpha=fp["alpha"])
        print(f"\nLoss: FocalLoss(gamma={fp['gamma']}, alpha={fp['alpha']})")
    else:
        loss_fn = "categorical_crossentropy"
        print(f"\nLoss: categorical_crossentropy")

    # ---- Save config before training ----
    save_config(cfg, cfg, out_dir, class_weights or {}, python_ver, tf_ver)

    # ---- Callbacks ----
    callbacks = build_callbacks(
        out_dir, cfg["model_filename"], "training_log.csv"
    )

    # ==========================================================
    # PHASE 1: Head-only training (backbone frozen)
    # ==========================================================
    print(f"\n{'=' * 50}")
    print(f"PHASE 1 — HEAD TRAINING (Backbone Frozen)")
    print(f"  Epochs: {PHASE1_EPOCHS}  |  LR: {PHASE1_LR}")
    print(f"{'=' * 50}")

    model.compile(
        optimizer=Adam(learning_rate=PHASE1_LR),
        loss=loss_fn,
        metrics=["accuracy"],
    )

    history_p1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=PHASE1_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    # ==========================================================
    # PHASE 2: Fine-tuning top 50 layers
    # ==========================================================
    print(f"\n{'=' * 50}")
    print(f"PHASE 2 — FINE-TUNING (Top {FINE_TUNE_UNFREEZE_TOP} layers)")
    print(f"  Max epochs: {PHASE2_MAX_EPOCHS}  |  LR: {PHASE2_LR}")
    print(f"{'=' * 50}")

    base_model.trainable = True
    # Freeze all layers except the top FINE_TUNE_UNFREEZE_TOP
    for layer in base_model.layers[:-FINE_TUNE_UNFREEZE_TOP]:
        layer.trainable = False

    # Count trainable vs frozen
    trainable_count = sum(1 for l in base_model.layers if l.trainable)
    frozen_count = len(base_model.layers) - trainable_count
    print(f"  Base model — trainable: {trainable_count}, frozen: {frozen_count}")

    model.compile(
        optimizer=Adam(learning_rate=PHASE2_LR),
        loss=loss_fn,
        metrics=["accuracy"],
    )

    history_p2 = model.fit(
        train_ds,
        validation_data=val_ds,
        initial_epoch=PHASE1_EPOCHS,
        epochs=PHASE1_EPOCHS + PHASE2_MAX_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    # ---- Save training artifacts ----
    save_history_json(history_p1, history_p2, out_dir, PHASE1_EPOCHS)
    save_training_plot(
        history_p1, history_p2, out_dir,
        f"SolarSafe AI — {cfg['experiment_name']}"
    )

    # ---- Print final validation metrics ----
    p2_vacc = history_p2.history.get("val_accuracy", [])
    p2_vloss = history_p2.history.get("val_loss", [])
    if p2_vacc:
        print(f"\n  Best Phase 2 val_accuracy : {max(p2_vacc):.4f}")
        print(f"  Final Phase 2 val_loss    : {p2_vloss[-1]:.4f}")

    # Verify model file saved
    model_path = out_dir / cfg["model_filename"]
    if model_path.exists():
        print(f"\n[OK] Best model saved: {model_path}")
    else:
        print(f"\n[WARN] Best model not found at {model_path} — saving current model as fallback")
        model.save(str(model_path))

    print(f"\n[DONE] {cfg['experiment_name']} training complete.")
    return model_path


# ============================================================
# CLI ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SolarSafe AI V2 Training Script"
    )
    parser.add_argument(
        "--experiment",
        type=str,
        required=True,
        choices=["v2a", "v2b"],
        help="Experiment to run: v2a (CrossEntropy) or v2b (Focal Loss)",
    )
    args = parser.parse_args()
    train(args.experiment)
