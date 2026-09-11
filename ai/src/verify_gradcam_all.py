import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gradcam
from config import TEST_DIR, GRADCAM_DIR

GRADCAM_DIR.mkdir(parents=True, exist_ok=True)

test_cases = {
    "Normal": sorted(list((TEST_DIR / "Normal").glob("*.jpg")))[0],
    "Hotspot": sorted(list((TEST_DIR / "Hotspot").glob("*.jpg")))[0],
    "Cell_Crack": sorted(list((TEST_DIR / "Cell_Crack").glob("*.jpg")))[2],
}

print("=" * 65)
print("TESTING GRAD-CAM ON ALL 3 CLASSES")
print("=" * 65)

for cls, img_p in test_cases.items():
    out_p = GRADCAM_DIR / f"gradcam_verify_{cls}.png"
    result = gradcam.generate_gradcam(img_p, output_path=out_p)
    pred = result["prediction"]
    conf = result["confidence"]
    hm = result["heatmap"]
    print(f"Class: {cls:<12} | Pred: {pred:<12} | Conf: {conf:.2f}% | Heatmap min/max: {hm.min():.2f}/{hm.max():.2f} | Saved: {out_p.name} ({out_p.exists()})")
