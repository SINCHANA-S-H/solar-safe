"""
export_tflite.py
----------------
Exports trained Keras model to TensorFlow Lite (.tflite) format.
Generates labels.txt file and validates TFLite model inference on test images.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import sys
import numpy as np
import tensorflow as tf
from pathlib import Path

from config import (
    BEST_MODEL_PATH,
    FINAL_MODEL_PATH,
    TFLITE_MODEL_PATH,
    LABELS_TXT_PATH,
    CLASS_NAMES,
    TEST_DIR,
)
from preprocessing import ImagePreprocessor


def export_tflite():
    print("=" * 60)
    print("SolarSafe AI — TensorFlow Lite Export")
    print("=" * 60)

    model_path = BEST_MODEL_PATH if BEST_MODEL_PATH.exists() else FINAL_MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    print(f"Loading Keras model from: {model_path}")
    keras_model = tf.keras.models.load_model(model_path)

    # ---------------------------------------------------------
    # Generate labels.txt
    # ---------------------------------------------------------
    print(f"\nWriting class labels to: {LABELS_TXT_PATH}")
    LABELS_TXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LABELS_TXT_PATH, "w", encoding="utf-8") as f:
        for cls in CLASS_NAMES:
            f.write(f"{cls}\n")

    print("Verified labels.txt content:")
    with open(LABELS_TXT_PATH, "r", encoding="utf-8") as f:
        print(f.read())

    # ---------------------------------------------------------
    # Convert to TFLite
    # ---------------------------------------------------------
    print("Converting Keras model to TFLite format...")
    converter = tf.lite.TFLiteConverter.from_keras_model(keras_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    TFLITE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(TFLITE_MODEL_PATH, "wb") as f:
        f.write(tflite_model)

    size_mb = TFLITE_MODEL_PATH.stat().st_size / (1024 * 1024)
    print(f"\nSuccessfully exported TFLite model to:\n  {TFLITE_MODEL_PATH} ({size_mb:.2f} MB)")

    # ---------------------------------------------------------
    # Test TFLite Model Inference
    # ---------------------------------------------------------
    print("\nValidating TFLite model inference...")
    interpreter = tf.lite.Interpreter(model_path=str(TFLITE_MODEL_PATH))
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"  TFLite Input Shape : {input_details[0]['shape']}")
    print(f"  TFLite Input Type  : {input_details[0]['dtype']}")
    print(f"  TFLite Output Shape: {output_details[0]['shape']}")

    # Pick a sample image from test set
    sample_image_path = None
    for cls in CLASS_NAMES:
        cls_dir = TEST_DIR / cls
        if cls_dir.exists():
            imgs = [f for f in cls_dir.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp")]
            if imgs:
                sample_image_path = imgs[0]
                break

    if sample_image_path:
        print(f"\nTesting TFLite inference on sample image: {sample_image_path.name}")
        img_array = ImagePreprocessor.preprocess(sample_image_path)
        batch_array = ImagePreprocessor.prepare_batch(img_array)

        # Keras prediction
        keras_pred = keras_model.predict(batch_array, verbose=0)[0]
        keras_cls = CLASS_NAMES[np.argmax(keras_pred)]

        # TFLite prediction
        interpreter.set_tensor(input_details[0]['index'], batch_array)
        interpreter.invoke()
        tflite_pred = interpreter.get_tensor(output_details[0]['index'])[0]
        tflite_cls = CLASS_NAMES[np.argmax(tflite_pred)]

        print(f"  Keras Model Prediction : {keras_cls} ({np.max(keras_pred)*100:.2f}%)")
        print(f"  TFLite Model Prediction: {tflite_cls} ({np.max(tflite_pred)*100:.2f}%)")

        if keras_cls == tflite_cls:
            print("  [OK] Keras and TFLite model predictions match perfectly!")
        else:
            print("  [WARNING] Prediction mismatch between Keras and TFLite!")

    print("\nTFLite export process completed successfully.")


if __name__ == "__main__":
    export_tflite()
