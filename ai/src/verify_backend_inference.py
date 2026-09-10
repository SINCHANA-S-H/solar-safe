import numpy as np
import tensorflow as tf
from pathlib import Path
from PIL import Image

MODEL_PATH = Path('ai/models/solar_safe_model.keras')
IMAGE_SIZE = (224, 224)
CLASS_NAMES = ['Cell_Crack', 'Hotspot', 'Normal']

model = tf.keras.models.load_model(MODEL_PATH, compile=False)

def predict_image(image_path: str):
    image = Image.open(image_path).convert('RGB')
    image = image.resize(IMAGE_SIZE, Image.Resampling.BILINEAR)
    image_array = np.array(image, dtype=np.float32)
    image_array = np.expand_dims(image_array, axis=0)
    predictions = model.predict(image_array, verbose=0)[0]
    predicted_index = int(np.argmax(predictions))
    predicted_class = CLASS_NAMES[predicted_index]
    confidence = float(predictions[predicted_index] * 100)
    probabilities = {
        CLASS_NAMES[i]: float(predictions[i] * 100)
        for i in range(len(CLASS_NAMES))
    }
    return {
        'prediction': predicted_class,
        'confidence': confidence,
        'probabilities': probabilities
    }

sample = 'C:/Users/sinch/.gemini/antigravity-ide/brain/e71b2c74-a3bb-44b7-b705-fd0702cc3f51/scratch/chatgpt_sep10.png'
out = predict_image(sample)
print('=' * 60)
print('SIMULATED BACKEND OUTPUT:')
print('Prediction    :', out['prediction'])
print('Confidence    :', f"{out['confidence']:.2f}%")
print('Probabilities :')
for k, v in out['probabilities'].items():
    print(f'  {k:<12}: {v:.2f}%')
print('=' * 60)
