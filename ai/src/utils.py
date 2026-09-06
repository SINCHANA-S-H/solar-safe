"""
utils.py
---------
Reusable helper functions used across the AI module.
"""

from pathlib import Path
import logging

# Import project configuration
from config import (
    MODEL_DIR,
    OUTPUT_DIR,
    TRAIN_DIR,
    VALIDATION_DIR,
    TEST_DIR
)


# ==========================================================
# Create Required Directories
# ==========================================================

def create_directories():
    """
    Creates all required project directories
    if they do not already exist.
    """

    directories = [
        MODEL_DIR,
        OUTPUT_DIR,
        TRAIN_DIR,
        VALIDATION_DIR,
        TEST_DIR
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("[OK] Project directories verified.")


# ==========================================================
# Configure Logging
# ==========================================================

def setup_logger():
    """
    Configures logging for the AI module.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    return logging.getLogger("SolarSafe")


# ==========================================================
# Count Images
# ==========================================================

def count_images(folder_path):
    """
    Counts image files inside a directory.
    """

    image_extensions = (".jpg", ".jpeg", ".png", ".bmp")

    return sum(
        1
        for file in Path(folder_path).iterdir()
        if file.suffix.lower() in image_extensions
    )


# ==========================================================
# Print Dataset Statistics
# ==========================================================

def print_dataset_statistics():
    """
    Displays the number of images
    in train, validation and test folders.
    """

    print("\n========== DATASET STATISTICS ==========\n")

    folders = {
        "Train": TRAIN_DIR,
        "Validation": VALIDATION_DIR,
        "Test": TEST_DIR
    }

    for folder_name, folder_path in folders.items():

        print(f"\n{folder_name}")

        if not folder_path.exists():
            print(" Folder does not exist.")
            continue

        for class_folder in folder_path.iterdir():

            if class_folder.is_dir():

                total = count_images(class_folder)

                print(f" {class_folder.name}: {total} images")

    print("\n========================================")


# ==========================================================
# Main (Testing)
# ==========================================================

if __name__ == "__main__":

    create_directories()

    logger = setup_logger()

    logger.info("Utilities loaded successfully.")

    print_dataset_statistics()