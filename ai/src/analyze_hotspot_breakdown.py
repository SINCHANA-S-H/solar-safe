"""
analyze_hotspot_breakdown.py
----------------------------
Analyzes predictions on test/Hotspot by original Raptor Maps raw class:
Cell vs Cell-Multi vs Hot-Spot vs Hot-Spot-Multi.
"""

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import hashlib
from pathlib import Path
import json
from collections import defaultdict
import numpy as np
import tensorflow as tf
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import FINAL_MODEL_PATH, CLASS_NAMES
from preprocessing import ImagePreprocessor

def main():
    model = tf.keras.models.load_model(FINAL_MODEL_PATH, compile=False)

    with open("ai/dataset/raw/eor/module_metadata.json") as f:
        meta = json.load(f)

    # Map raw image hashes to raw anomaly class
    raw_hash_to_class = {}
    for p in Path("ai/dataset/raw/eor/images").glob("*.jpg"):
        with open(p, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        raw_hash_to_class[h] = meta.get(p.stem, {}).get("anomaly_class", "Unknown")

    # Evaluate test/Hotspot
    breakdown = defaultdict(lambda: defaultdict(int))

    for img_p in sorted((Path("ai/dataset/test/Hotspot")).glob("*.jpg")):
        with open(img_p, "rb") as f:
            h = hashlib.md5(f.read()).hexdigest()
        raw_cls = raw_hash_to_class.get(h, "Unknown")

        batch = ImagePreprocessor.prepare_batch(ImagePreprocessor.preprocess(img_p))
        pred = model.predict(batch, verbose=0)[0]
        pred_cls = CLASS_NAMES[np.argmax(pred)]

        breakdown[raw_cls][pred_cls] += 1

    print("\n" + "=" * 65)
    print("PREDICTIONS FOR test/Hotspot BY ORIGINAL RAW ANOMALY CLASS")
    print("=" * 65)
    for raw_cls, preds in breakdown.items():
        total = sum(preds.values())
        print(f"\nRaw Class: {raw_cls} (Total: {total})")
        for p_cls, count in sorted(preds.items()):
            print(f"  Pred {p_cls:<10}: {count:>3} ({count/total*100:.1f}%)")

if __name__ == "__main__":
    main()
