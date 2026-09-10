"""
config.py
----------
Central configuration file for the SolarSafe AI project.

Update project-wide settings here instead of changing them
throughout the code.
"""

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = BASE_DIR / "dataset"

RAW_DATASET_DIR = DATASET_DIR / "raw"

TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"
TEST_DIR = DATASET_DIR / "test"

MODELS_DIR = BASE_DIR / "models"

OUTPUTS_DIR = BASE_DIR / "outputs"


# ============================================================
# OUTPUT DIRECTORIES
# ============================================================

CHECKPOINT_DIR = OUTPUTS_DIR / "checkpoints"

GRAPHS_DIR = OUTPUTS_DIR / "graphs"

REPORTS_DIR = OUTPUTS_DIR / "reports"

PREDICTIONS_DIR = OUTPUTS_DIR / "predictions"

EVALUATION_DIR = OUTPUTS_DIR / "evaluation"

GRADCAM_DIR = OUTPUTS_DIR / "gradcam"


# ============================================================
# IMAGE SETTINGS
# ============================================================

IMG_SIZE = 224

IMAGE_SHAPE = (IMG_SIZE, IMG_SIZE)

CHANNELS = 3


# ============================================================
# DATASET SETTINGS
# ============================================================

CLASS_NAMES = [
    "Cell_Crack",
    "Hotspot",
    "Normal"
]

NUM_CLASSES = len(CLASS_NAMES)


# ============================================================
# TRAINING SETTINGS
# ============================================================

BATCH_SIZE = 32

INITIAL_EPOCHS = 4

FINE_TUNE_EPOCHS = 8

INITIAL_LEARNING_RATE = 1e-4

FINE_TUNE_LEARNING_RATE = 1e-5

RANDOM_SEED = 42


# ============================================================
# MODEL SETTINGS
# ============================================================

MODEL_NAME = "MobileNetV2"

DROPOUT_RATE = 0.4

DENSE_UNITS = 256

L2_REGULARIZATION = 0.001


# ============================================================
# BACKWARD COMPATIBILITY ALIASES
# ============================================================

IMAGE_SIZE = IMAGE_SHAPE

MODEL_DIR = MODELS_DIR

OUTPUT_DIR = OUTPUTS_DIR


# ============================================================
# MODEL OUTPUT FILES
# ============================================================

BEST_MODEL_PATH = CHECKPOINT_DIR / "best_model.keras"

FINAL_MODEL_PATH = MODELS_DIR / "solar_safe_model.keras"

TFLITE_MODEL_PATH = MODELS_DIR / "solarsafe_model.tflite"

LABELS_TXT_PATH = MODELS_DIR / "labels.txt"


# ============================================================
# TRAINING OUTPUT FILES
# ============================================================

HISTORY_CSV = REPORTS_DIR / "training_history.csv"

CLASS_INDEX_FILE = REPORTS_DIR / "class_indices.json"

CLASSIFICATION_REPORT = REPORTS_DIR / "classification_report.txt"

CONFUSION_MATRIX = REPORTS_DIR / "confusion_matrix.png"

ACCURACY_GRAPH = GRAPHS_DIR / "accuracy.png"

LOSS_GRAPH = GRAPHS_DIR / "loss.png"


# ============================================================
# GRAD-CAM OUTPUT
# ============================================================

GRADCAM_SUMMARY_PATH = GRADCAM_DIR / "gradcam_summary.png"


# ============================================================
# CALLBACK SETTINGS
# ============================================================

PATIENCE = 3

LR_PATIENCE = 2

MIN_LR = 1e-7

CSV_LOG_PATH = REPORTS_DIR / "training_history.csv"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

for folder in [
    MODELS_DIR,
    OUTPUTS_DIR,
    CHECKPOINT_DIR,
    GRAPHS_DIR,
    REPORTS_DIR,
    PREDICTIONS_DIR,
    EVALUATION_DIR,
    GRADCAM_DIR,
]:
    folder.mkdir(
        parents=True,
        exist_ok=True
    )

