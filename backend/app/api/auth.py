from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.utils.auth import hash_password, verify_password, create_token


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Signup API
@router.post("/signup")
def signup(
    username: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    hashed_password = hash_password(password)


    new_user = User(
        username=username,
        email=email,
        password=hashed_password
    )


    db.add(new_user)
    db.commit()
    db.refresh(new_user)


    return {
        "message": "Signup successful",
        "username": new_user.username
    }



# Login API
@router.post("/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == email
    ).first()


    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )


    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Wrong password"
        )


    token = create_token({
        "email": user.email
    })


    return {
        "message": "Login successful",
        "access_token": token
    }