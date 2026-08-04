from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.services.pdf_generator import create_pdf


router = APIRouter()


@router.post("/report")
def generate_report(
    email: str,
    prediction: str,
    confidence: str
):

    filename = "solar_report.pdf"


    file_path = create_pdf(
        filename,
        email,
        prediction,
        confidence
    )


    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )