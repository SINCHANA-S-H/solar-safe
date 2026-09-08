"""
data_loader.py
----------------
Handles dataset loading and validation.

Responsibilities:
1. Validate dataset structure
2. Read class names
3. Count images in each class
"""

from pathlib import Path
from config import TRAIN_DIR, VALIDATION_DIR, TEST_DIR


class DataLoader:
    """
    Utility class for loading and validating
    the solar panel dataset.
    """

    def __init__(self):
        self.train_dir = TRAIN_DIR
        self.validation_dir = VALIDATION_DIR
        self.test_dir = TEST_DIR

    # --------------------------------------------------
    # Check Folder Exists
    # --------------------------------------------------

    def check_directory(self, directory: Path) -> bool:
        """
        Returns True if directory exists.
        """

        return directory.exists()

    # --------------------------------------------------
    # Get Class Names
    # --------------------------------------------------

    def get_classes(self):
        """
        Reads class names from the train folder.

        Example:
        Normal
        Hotspot
        Cell_Crack
        """

        if not self.check_directory(self.train_dir):
            return []

        classes = [
            folder.name
            for folder in self.train_dir.iterdir()
            if folder.is_dir()
        ]

        classes.sort()

        return classes

    # --------------------------------------------------
    # Count Images
    # --------------------------------------------------

    def count_images(self, directory: Path):

        image_extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp"
        )

        total = 0

        for class_folder in directory.iterdir():

            if class_folder.is_dir():

                total += len([
                    image
                    for image in class_folder.iterdir()
                    if image.suffix.lower() in image_extensions
                ])

        return total

    # --------------------------------------------------
    # Dataset Summary
    # --------------------------------------------------

    def dataset_summary(self):

        print("\n========== DATASET SUMMARY ==========\n")

        print(f"Training Images     : {self.count_images(self.train_dir)}")
        print(f"Validation Images  : {self.count_images(self.validation_dir)}")
        print(f"Testing Images     : {self.count_images(self.test_dir)}")

        print("\nClasses:")

        for cls in self.get_classes():
            print(f"• {cls}")

        print("\n=====================================\n")


if __name__ == "__main__":

    loader = DataLoader()

    loader.dataset_summary()