from reportlab.pdfgen import canvas
import os


def create_pdf(
    filename,
    user_email,
    prediction,
    confidence
):

    folder = "reports"

    if not os.path.exists(folder):
        os.makedirs(folder)


    file_path = os.path.join(
        folder,
        filename
    )


    pdf = canvas.Canvas(file_path)

    pdf.drawString(
        100,
        750,
        "Solar Safe Panel Report"
    )

    pdf.drawString(
        100,
        700,
        f"User: {user_email}"
    )

    pdf.drawString(
        100,
        650,
        f"Prediction: {prediction}"
    )

    pdf.drawString(
        100,
        600,
        f"Confidence: {confidence}"
    )

    pdf.save()


    return file_path