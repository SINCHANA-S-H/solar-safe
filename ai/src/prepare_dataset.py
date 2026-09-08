
import json
import random
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_DIR = BASE_DIR / "dataset"
RAW_DIR = DATASET_DIR / "raw"

EOR_DIR = RAW_DIR / "eor"
EOR_METADATA_FILE = EOR_DIR / "module_metadata.json"

PVMD_DIR = RAW_DIR / "pvmd"

TRAIN_DIR = DATASET_DIR / "train"
VALIDATION_DIR = DATASET_DIR / "validation"
TEST_DIR = DATASET_DIR / "test"


# ============================================================
# CLASSES
# ============================================================

CLASS_NAMES: List[str] = [
    "Cell_Crack",
    "Hotspot",
    "Normal"
]


# ============================================================
# LABEL MAPPINGS
# ============================================================

EOR_LABEL_MAP: Dict[str, str] = {
    "No-Anomaly": "Normal",
    "Hot-Spot": "Hotspot",
    "Cell": "Cell_Crack",
}


PVMD_FOLDER_MAP: Dict[str, str] = {
    "Cracks": "Cell_Crack",
    "Hotspots": "Hotspot",
}


# ============================================================
# SETTINGS
# ============================================================

SUPPORTED_EXTENSIONS: Tuple[str, ...] = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp"
)

# Number of training images wanted per class AFTER oversampling
TRAIN_TARGET_COUNT = 2000

# Dataset split
TRAIN_RATIO = 0.80
VALIDATION_RATIO = 0.10
TEST_RATIO = 0.10

RANDOM_SEED = 42


# ============================================================
# CREATE DIRECTORIES
# ============================================================

def create_directories() -> None:

    # Remove old dataset splits
    for split_dir in (
        TRAIN_DIR,
        VALIDATION_DIR,
        TEST_DIR
    ):

        if split_dir.exists():
            shutil.rmtree(split_dir)

        for class_name in CLASS_NAMES:
            (
                split_dir / class_name
            ).mkdir(
                parents=True,
                exist_ok=True
            )


# ============================================================
# COPY IMAGE
# ============================================================

def copy_image(
    source_path: Path,
    destination_path: Path
) -> None:

    try:

        shutil.copy2(
            source_path,
            destination_path
        )

    except (FileNotFoundError, OSError) as error:

        print(
            f"Warning: Failed to copy "
            f"{source_path} -> {destination_path}: {error}"
        )


# ============================================================
# FILE HASH
# ============================================================

def compute_file_hash(
    file_path: Path
) -> str:

    hasher = hashlib.md5()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):

            hasher.update(chunk)

    return hasher.hexdigest()


# ============================================================
# READ EOR DATASET
# ============================================================

def read_eor_dataset() -> Dict[str, List[Path]]:

    class_images: Dict[str, List[Path]] = {
        class_name: []
        for class_name in CLASS_NAMES
    }

    if not EOR_METADATA_FILE.exists():

        print(
            f"Warning: EOR metadata file not found:\n"
            f"{EOR_METADATA_FILE}"
        )

        return class_images


    with open(
        EOR_METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as metadata_file:

        metadata = json.load(metadata_file)


    for image_id, info in metadata.items():

        if not isinstance(info, dict):
            continue

        raw_label = info.get("anomaly_class")

        image_filepath = info.get("image_filepath")

        if raw_label is None:
            continue

        if image_filepath is None:
            continue


        mapped_class = EOR_LABEL_MAP.get(raw_label)

        if mapped_class is None:
            continue


        image_path = EOR_DIR / image_filepath

        if image_path.exists():

            if image_path.suffix.lower() in SUPPORTED_EXTENSIONS:

                class_images[mapped_class].append(
                    image_path
                )


    return class_images


# ============================================================
# READ PVMD DATASET
# ============================================================

def read_pvmd_dataset() -> Dict[str, List[Path]]:

    class_images: Dict[str, List[Path]] = {
        class_name: []
        for class_name in CLASS_NAMES
    }


    for folder_name, mapped_class in PVMD_FOLDER_MAP.items():

        folder_path = PVMD_DIR / folder_name

        if not folder_path.exists():

            print(
                f"Warning: PVMD folder not found: "
                f"{folder_path}"
            )

            continue


        for file_path in folder_path.rglob("*"):

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            class_images[mapped_class].append(
                file_path
            )


    return class_images


# ============================================================
# GLOBAL DEDUPLICATION
# ============================================================

def get_unique_raw_images() -> Dict[str, List[Path]]:

    eor_data = read_eor_dataset()

    pvmd_data = read_pvmd_dataset()


    unique_data: Dict[str, List[Path]] = {
        class_name: []
        for class_name in CLASS_NAMES
    }


    # Keep track of hashes globally.
    #
    # This prevents the same physical image from
    # appearing in different datasets/splits.
    global_seen_hashes = set()


    # Process rare classes first.
    #
    # This ensures that if an identical image occurs
    # in multiple datasets, the rare class keeps it.
    processing_order = [
        "Hotspot",
        "Cell_Crack",
        "Normal"
    ]


    for class_name in processing_order:

        all_paths = (
            eor_data.get(class_name, [])
            +
            pvmd_data.get(class_name, [])
        )


        for image_path in all_paths:

            try:

                file_hash = compute_file_hash(
                    image_path
                )


                if file_hash in global_seen_hashes:
                    continue


                global_seen_hashes.add(
                    file_hash
                )


                unique_data[class_name].append(
                    image_path
                )


            except Exception as error:

                print(
                    f"Error reading "
                    f"{image_path}: {error}"
                )


    return unique_data


# ============================================================
# CALCULATE SPLIT COUNTS
# ============================================================

def calculate_split_counts(
    total_images: int
) -> Tuple[int, int, int]:

    if total_images < 3:

        return (
            total_images,
            0,
            0
        )


    validation_count = max(
        1,
        round(
            total_images * VALIDATION_RATIO
        )
    )


    test_count = max(
        1,
        round(
            total_images * TEST_RATIO
        )
    )


    train_count = (
        total_images
        - validation_count
        - test_count
    )


    # Make sure at least one image remains
    # for training.
    if train_count < 1:

        train_count = 1

        if validation_count > 1:
            validation_count -= 1

        elif test_count > 1:
            test_count -= 1


    return (
        train_count,
        validation_count,
        test_count
    )


# ============================================================
# CREATE TRAINING DATA
# ============================================================

def create_training_set(
    train_unique_images: List[Path]
) -> List[Path]:

    unique_count = len(
        train_unique_images
    )


    # If enough unique images exist,
    # simply use TRAIN_TARGET_COUNT.
    if unique_count >= TRAIN_TARGET_COUNT:

        return train_unique_images[
            :TRAIN_TARGET_COUNT
        ]


    # If not enough unique images exist,
    # oversample ONLY the training set.
    extra_needed = (
        TRAIN_TARGET_COUNT
        - unique_count
    )


    extra_images = random.choices(
        train_unique_images,
        k=extra_needed
    )


    return (
        train_unique_images
        +
        extra_images
    )


# ============================================================
# COPY SPLIT
# ============================================================

def copy_split(
    images: List[Path],
    destination_dir: Path,
    class_name: str
) -> None:

    for index, source_path in enumerate(images):

        destination_path = (
            destination_dir
            /
            class_name
            /
            f"{class_name}_{index:05d}"
            f"{source_path.suffix.lower()}"
        )


        copy_image(
            source_path,
            destination_path
        )


# ============================================================
# MAIN
# ============================================================

def main():

    random.seed(
        RANDOM_SEED
    )


    print("=" * 65)
    print("SolarSafe AI — Dataset Preparation")
    print("=" * 65)


    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    print("\nCreating dataset directories...")

    create_directories()


    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    print(
        "\nReading and globally "
        "deduplicating raw datasets..."
    )

    unique_data = get_unique_raw_images()


    print(
        "\nGlobally Unique Raw Dataset Counts "
        "(by MD5 hash):"
    )

    print("-" * 50)


    for class_name in CLASS_NAMES:

        print(
            f"{class_name:<15} : "
            f"{len(unique_data[class_name])} "
            f"unique images"
        )


    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    print(
        "\nCreating 80/10/10 train-validation-test split..."
    )


    split_counts = {}


    for class_name in CLASS_NAMES:

        images = unique_data[
            class_name
        ].copy()


        # Shuffle deterministically
        random.shuffle(
            images
        )


        total_images = len(
            images
        )


        # Calculate split sizes
        (
            train_unique_count,
            validation_count,
            test_count
        ) = calculate_split_counts(
            total_images
        )


        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Validation and test are selected FIRST.
        #
        # They are NEVER oversampled.
        # ----------------------------------------------------

        train_end = train_unique_count

        validation_end = (
            train_end
            +
            validation_count
        )


        train_unique_images = images[
            :train_end
        ]


        validation_images = images[
            train_end:validation_end
        ]


        test_images = images[
            validation_end:
        ]


        # ----------------------------------------------------
        # Oversample ONLY training
        # ----------------------------------------------------

        train_images = create_training_set(
            train_unique_images
        )


        # ----------------------------------------------------
        # Copy files
        # ----------------------------------------------------

        copy_split(
            train_images,
            TRAIN_DIR,
            class_name
        )


        copy_split(
            validation_images,
            VALIDATION_DIR,
            class_name
        )


        copy_split(
            test_images,
            TEST_DIR,
            class_name
        )


        split_counts[class_name] = {
            "unique_raw": total_images,
            "unique_train": len(
                train_unique_images
            ),
            "train": len(
                train_images
            ),
            "validation": len(
                validation_images
            ),
            "test": len(
                test_images
            )
        }


    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    print(
        "\nDataset Preparation Summary:"
    )


    header = (
        f"{'Class':<15}"
        f"{'Raw':>10}"
        f"{'Train':>10}"
        f"{'Val':>10}"
        f"{'Test':>10}"
        f"{'Total':>10}"
    )


    print(header)

    print("-" * len(header))


    for class_name in CLASS_NAMES:

        counts = split_counts[
            class_name
        ]


        total_created = (
            counts["train"]
            +
            counts["validation"]
            +
            counts["test"]
        )


        print(
            f"{class_name:<15}"
            f"{counts['unique_raw']:>10}"
            f"{counts['train']:>10}"
            f"{counts['validation']:>10}"
            f"{counts['test']:>10}"
            f"{total_created:>10}"
        )


    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    print(
        "\nImportant:"
    )

    print(
        "  • Validation images are NOT oversampled."
    )

    print(
        "  • Test images are NOT oversampled."
    )

    print(
        "  • Oversampling is applied ONLY to training."
    )

    print(
        "  • Exact duplicate files are removed globally."
    )

    print(
        "  • Train/validation/test contain no shared "
        "source-image hashes."
    )


    print(
        "\nDataset preparation completed successfully."
    )

    print("=" * 65)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()