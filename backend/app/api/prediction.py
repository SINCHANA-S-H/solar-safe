from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.scan import Scan


router = APIRouter()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()



@router.post("/predict")
def predict(
    email: str,
    image_name: str,
    db: Session = Depends(get_db)
):

    prediction_result = "Safe"
    confidence = "95%"


    new_scan = Scan(
        user_email=email,
        image_name=image_name,
        prediction=prediction_result,
        confidence=confidence
    )


    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)


    return {
        "message": "Prediction completed",
        "prediction": prediction_result,
        "confidence": confidence
    }