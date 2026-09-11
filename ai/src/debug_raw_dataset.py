"""
debug_raw_dataset.py
--------------------
Executes Step 2 and Step 6:
Tests 5 raw dataset images per class directly through the model.
Prints filename, properties (width, height, mode, channels, dtype, min, max),
actual class, predicted class, confidence, and all probabilities.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import sys
from pathlib import Path
from PIL import Image
import numpy as np
import tensorflow as tf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FINAL_MODEL_PATH, CLASS_NAMES, TEST_DIR
from preprocessing import ImagePreprocessor

def main():
    print(f"Loading Model: {FINAL_MODEL_PATH}")
    model = tf.keras.models.load_model(FINAL_MODEL_PATH, compile=False)
    print(f"Model Input Shape: {model.input_shape}, Output Shape: {model.output_shape}")
    print(f"Class Names: {CLASS_NAMES}")

    test_classes = ["Normal", "Hotspot", "Cell_Crack"]

    for cls in test_classes:
        cls_dir = TEST_DIR / cls
        img_files = sorted(list(cls_dir.glob("*.jpg")))[:5]
        print("\n" + "=" * 65)
        print(f"TESTING 5 RAW DATASET IMAGES FOR CLASS: {cls}")
        print("=" * 65)

        for p in img_files:
            im_raw = Image.open(p)
            arr_raw = np.array(im_raw)
            channels = 1 if im_raw.mode == "L" else len(im_raw.getbands())

            # Preprocessing
            img_arr = ImagePreprocessor.preprocess(p)
            batch = ImagePreprocessor.prepare_batch(img_arr)
            preds = model.predict(batch, verbose=0)[0]
            pred_idx = int(np.argmax(preds))
            pred_cls = CLASS_NAMES[pred_idx]
            conf = float(preds[pred_idx]) * 100

            cc_prob = float(preds[CLASS_NAMES.index("Cell_Crack")])
            hs_prob = float(preds[CLASS_NAMES.index("Hotspot")])
            norm_prob = float(preds[CLASS_NAMES.index("Normal")])

            print(f"\nFilename: {p.name}")
            print(f"Properties: {im_raw.width} x {im_raw.height}, mode={im_raw.mode}, channels={channels}, dtype={arr_raw.dtype}, min={arr_raw.min()}, max={arr_raw.max()}")
            print(f"Actual: {cls}")
            print(f"Predicted: {pred_cls}")
            print(f"Confidence: {conf:.2f}%")
            print("Probabilities:")
            print(f"  Normal:     {norm_prob:.4f} ({norm_prob*100:.2f}%)")
            print(f"  Hotspot:    {hs_prob:.4f} ({hs_prob*100:.2f}%)")
            print(f"  Cell_Crack: {cc_prob:.4f} ({cc_prob*100:.2f}%)")

if __name__ == "__main__":
    main()
