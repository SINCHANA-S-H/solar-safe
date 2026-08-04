from sqlalchemy import Column, Integer, String
from app.database.database import Base


class Scan(Base):

    __tablename__ = "scans"

    id = Column(Integer, primary_key=True)

    user_email = Column(String)

    image_name = Column(String)

    prediction = Column(String)

    confidence = Column(String)