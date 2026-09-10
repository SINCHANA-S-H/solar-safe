"""
train.py
---------
Two-stage MobileNetV2 training pipeline for SolarSafe AI:
1. Load Train & Validation Datasets
2. Verify Datasets & Class Names
3. Phase 1: Train Top Classification Head (Frozen Backbone)
4. Phase 2: Fine-tune Upper MobileNetV2 Layers
5. Save Best and Final Models
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import tensorflow as tf
from sklearn.utils.class_weight import compute_class_weight

from tensorflow.keras.callbacks import (
    ModelCheckpoint,
    EarlyStopping,
    ReduceLROnPlateau,
    CSVLogger,
)
from tensorflow.keras.optimizers import Adam

from model import build_model
from config import (
    TRAIN_DIR,
    VALIDATION_DIR,
    IMG_SIZE,
    BATCH_SIZE,
    RANDOM_SEED,
    CLASS_NAMES,
    INITIAL_EPOCHS,
    FINE_TUNE_EPOCHS,
    INITIAL_LEARNING_RATE,
    FINE_TUNE_LEARNING_RATE,
    BEST_MODEL_PATH,
    FINAL_MODEL_PATH,
    CSV_LOG_PATH,
    PATIENCE,
    LR_PATIENCE,
    MIN_LR,
)


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_datasets():
    train_dataset = tf.keras.utils.image_dataset_from_directory(
        TRAIN_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=RANDOM_SEED,
    )

    validation_dataset = tf.keras.utils.image_dataset_from_directory(
        VALIDATION_DIR,
        labels="inferred",
        label_mode="categorical",
        image_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        shuffle=False,
    )

    return train_dataset, validation_dataset


# ==========================================================
# VERIFY DATASET
# ==========================================================

def verify_dataset(train_dataset, validation_dataset, class_names):
    """
    Verifies dataset class names and structure consistency.
    """
    print("\n--- Verifying Dataset ---")
    print(f"Detected Train Classes : {train_dataset.class_names}")
    print(f"Detected Val Classes   : {validation_dataset.class_names}")
    print(f"Expected Class Order   : {class_names}")

    assert train_dataset.class_names == class_names, "Train class names mismatch!"
    assert validation_dataset.class_names == class_names, "Validation class names mismatch!"
    print("Dataset verification passed successfully.\n")


# ==========================================================
# OPTIMIZE DATASET
# ==========================================================

def optimize_dataset(dataset):
    return dataset.prefetch(tf.data.AUTOTUNE)


# ==========================================================
# COMPUTE CLASS WEIGHTS
# ==========================================================

def get_class_weights(dataset):
    labels = []
    for _, y in dataset.unbatch():
        labels.append(np.argmax(y.numpy()))

    labels = np.array(labels)
    classes = np.unique(labels)

    weights = compute_class_weight(
        class_weight="balanced",
        classes=classes,
        y=labels,
    )

    class_weights = {
        int(cls): float(weight)
        for cls, weight in zip(classes, weights)
    }

    return class_weights


# ==========================================================
# BUILD CALLBACKS
# ==========================================================

def get_callbacks():
    checkpoint = ModelCheckpoint(
        filepath=BEST_MODEL_PATH,
        monitor="val_accuracy",
        save_best_only=True,
        verbose=1,
    )

    early_stop = EarlyStopping(
        monitor="val_loss",
        patience=PATIENCE,
        restore_best_weights=True,
        verbose=1,
    )

    reduce_lr = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.2,
        patience=LR_PATIENCE,
        min_lr=MIN_LR,
        verbose=1,
    )

    csv_logger = CSVLogger(
        CSV_LOG_PATH,
        append=False,
    )

    return [checkpoint, early_stop, reduce_lr, csv_logger]


# ==========================================================
# COMPILE MODEL
# ==========================================================

def compile_model():
    model, base_model = build_model()

    model.compile(
        optimizer=Adam(learning_rate=INITIAL_LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model, base_model


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SolarSafe AI Training")
    print("=" * 60)

    print("\nLoading datasets...\n")
    train_dataset, validation_dataset = load_datasets()

    class_names = train_dataset.class_names

    # Verify dataset structure and class order
    verify_dataset(train_dataset, validation_dataset, CLASS_NAMES)

    train_dataset = optimize_dataset(train_dataset)
    validation_dataset = optimize_dataset(validation_dataset)

    print("Calculating Class Weights...\n")
    class_weights = get_class_weights(train_dataset)

    for index, weight in class_weights.items():
        print(f"{class_names[index]:15} : {weight:.3f}")

    print("\nBuilding MobileNetV2 Model...\n")
    model, base_model = compile_model()
    model.summary()

    callbacks = get_callbacks()

    print("\n==============================")
    print("PHASE 1 : FEATURE EXTRACTION")
    print("==============================\n")

    history_phase1 = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=INITIAL_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    print("\n==============================")
    print("PHASE 2 : FINE TUNING")
    print("==============================\n")

    base_model.trainable = True

    # Unfreeze only the top 30 layers
    for layer in base_model.layers[:-30]:
        layer.trainable = False

    model.compile(
        optimizer=Adam(learning_rate=FINE_TUNE_LEARNING_RATE),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    history_phase2 = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        initial_epoch=INITIAL_EPOCHS,
        epochs=INITIAL_EPOCHS + FINE_TUNE_EPOCHS,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    print("\nTraining Completed Successfully.")

    # Ensure final model has the best checkpoint weights
    if BEST_MODEL_PATH.exists():
        import shutil
        shutil.copy2(BEST_MODEL_PATH, FINAL_MODEL_PATH)
        print(f"\nCopied best checkpoint to Final Model: {FINAL_MODEL_PATH}")
    else:
        model.save(FINAL_MODEL_PATH)
        print(f"\nFinal Model Saved At: {FINAL_MODEL_PATH}")
    print(f"Best Model Saved At : {BEST_MODEL_PATH}")

    print("\nEvaluating Model on Validation Set...\n")
    loss, accuracy = model.evaluate(validation_dataset)

    print(f"\nValidation Loss     : {loss:.4f}")
    print(f"Validation Accuracy : {accuracy * 100:.2f}%")