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


@router.get("/history")
def history(
    email: str,
    db: Session = Depends(get_db)
):

    scans = db.query(Scan).filter(
        Scan.user_email == email
    ).all()

    return scans