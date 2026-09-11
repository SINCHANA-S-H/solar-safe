import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import sys
from pathlib import Path
import numpy as np
import tensorflow as tf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FINAL_MODEL_PATH, CLASS_NAMES, TEST_DIR
from preprocessing import ImagePreprocessor
from focal_loss import FocalLoss

model = tf.keras.models.load_model(FINAL_MODEL_PATH, compile=False, custom_objects={"FocalLoss": FocalLoss})

print("=" * 70)
print("PART 1: IN-DISTRIBUTION TEST (RAW DATASET TEST SET - 5 SAMPLES PER CLASS)")
print("=" * 70)

for cls in ["Normal", "Hotspot", "Cell_Crack"]:
    cls_dir = TEST_DIR / cls
    images = sorted(list(cls_dir.glob("*.jpg")))[:5]
    print(f"\n--- CLASS: {cls} ---")
    for img_p in images:
        arr = ImagePreprocessor.preprocess(img_p)
        batch = ImagePreprocessor.prepare_batch(arr)
        preds = model.predict(batch, verbose=0)[0]
        pred_idx = int(np.argmax(preds))
        pred_cls = CLASS_NAMES[pred_idx]
        conf = float(preds[pred_idx] * 100)
        norm_p = float(preds[CLASS_NAMES.index("Normal")] * 100)
        hs_p = float(preds[CLASS_NAMES.index("Hotspot")] * 100)
        cc_p = float(preds[CLASS_NAMES.index("Cell_Crack")] * 100)

        print(f"Filename: {img_p.name}")
        print(f"Actual: {cls}")
        print(f"Predicted: {pred_cls}")
        print(f"Confidence: {conf:.2f}%")
        print(f"Probabilities:")
        print(f"  Normal: {norm_p:.2f}%")
        print(f"  Hotspot: {hs_p:.2f}%")
        print(f"  Cell_Crack: {cc_p:.2f}%\n")

print("=" * 70)
print("PART 2: EXTERNAL TEST (REAL-WORLD IMAGES)")
print("=" * 70)

external_images = [
    ("backend/uploads/87466936-2b8b-406f-8cf9-778142d4bdd3.png", "Thermal Whole-Panel (Hotspot Module)"),
    ("ai/outputs/crop_hs_cell.png", "Thermal Isolated Hotspot Cell (from 87466936)"),
    ("ai/outputs/crop_norm_cell.png", "Thermal Isolated Normal Cell (from 87466936)"),
    ("C:/Users/sinch/.gemini/antigravity-ide/brain/e71b2c74-a3bb-44b7-b705-fd0702cc3f51/scratch/chatgpt_sep10.png", "External Normal Solar Panel"),
]

for img_path_str, desc in external_images:
    p = Path(img_path_str)
    if not p.exists():
        print(f"File not found: {p}")
        continue
    arr = ImagePreprocessor.preprocess(p)
    batch = ImagePreprocessor.prepare_batch(arr)
    preds = model.predict(batch, verbose=0)[0]
    pred_idx = int(np.argmax(preds))
    pred_cls = CLASS_NAMES[pred_idx]
    conf = float(preds[pred_idx] * 100)
    norm_p = float(preds[CLASS_NAMES.index("Normal")] * 100)
    hs_p = float(preds[CLASS_NAMES.index("Hotspot")] * 100)
    cc_p = float(preds[CLASS_NAMES.index("Cell_Crack")] * 100)

    print(f"Filename: {p.name}")
    print(f"Description: {desc}")
    print(f"Predicted: {pred_cls}")
    print(f"Confidence: {conf:.2f}%")
    print(f"Probabilities:")
    print(f"  Normal: {norm_p:.2f}%")
    print(f"  Hotspot: {hs_p:.2f}%")
    print(f"  Cell_Crack: {cc_p:.2f}%\n")
