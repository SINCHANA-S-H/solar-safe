import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image


# Path to the trained Solar-Safe model
BASE_DIR = Path(__file__).resolve().parents[3]
MODEL_PATH = BASE_DIR / "ai" / "models" / "solar_safe_model.keras"

# Model configuration
IMAGE_SIZE = (224, 224)

CLASS_NAMES = [
    "Cell_Crack",
    "Hotspot",
    "Normal"
]


# Load the model once when the backend starts
model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)


def predict_image(image_path: str):
    """
    Predict the condition of a solar-panel image.
    """

    image = Image.open(image_path).convert("RGB")

    image = image.resize(
        IMAGE_SIZE,
        Image.Resampling.BILINEAR
    )

    image_array = np.array(
        image,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    predictions = model.predict(
        image_array,
        verbose=0
    )[0]

    predicted_index = int(
        np.argmax(predictions)
    )

    predicted_class = CLASS_NAMES[predicted_index]

    confidence = float(
        predictions[predicted_index] * 100
    )

    probabilities = {
        CLASS_NAMES[i]: float(predictions[i] * 100)
        for i in range(len(CLASS_NAMES))
    }

    return {
        "prediction": predicted_class,
        "confidence": confidence,
        "probabilities": probabilities
    }