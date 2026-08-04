from fastapi import FastAPI

# Database
from app.database.database import engine, Base

# Import models so tables are created
from app.models import user, scan

# API routers
from app.api import auth
from app.api import prediction
from app.api import history
from app.api import report
from app.api import chatbot


app = FastAPI(
    title="Solar Safe API",
    description="Solar Panel Safety Backend",
    version="1.0"
)


# Create database tables
Base.metadata.create_all(bind=engine)


# Register API routes
app.include_router(auth.router)
app.include_router(prediction.router)
app.include_router(history.router)
app.include_router(report.router)
app.include_router(chatbot.router)


@app.get("/")
def home():
    return {
        "message": "Solar Safe Backend Running"
    }