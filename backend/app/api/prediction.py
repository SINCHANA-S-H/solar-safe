from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid

from app.database.database import SessionLocal
from app.models.scan import Scan
from app.services.ml_predictor import predict_image


router = APIRouter()


# Upload directory
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/predict")
def predict(
    email: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Validate image type
    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/jpg"
    }

    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are allowed"
        )

    # Create a unique filename
    file_extension = Path(image.filename).suffix.lower()

    if not file_extension:
        file_extension = ".jpg"

    saved_filename = f"{uuid.uuid4()}{file_extension}"

    image_path = UPLOAD_DIR / saved_filename

    try:

        # Save uploaded image
        with image_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Run ML prediction
        result = predict_image(str(image_path))

        prediction_result = result["prediction"]
        confidence = result["confidence"]

        # Save scan history
        new_scan = Scan(
            user_email=email,
            image_name=saved_filename,
            prediction=prediction_result,
            confidence=f"{confidence:.2f}%"
        )

        db.add(new_scan)
        db.commit()
        db.refresh(new_scan)

        return {
            "message": "Prediction completed",
            "prediction": prediction_result,
            "confidence": round(confidence, 2),
            "probabilities": result["probabilities"],
            "image_name": saved_filename
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

    finally:
        image.file.close()