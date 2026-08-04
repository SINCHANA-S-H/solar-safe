from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta


SECRET_KEY = "solar-safe-secret"
ALGORITHM = "HS256"


pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def hash_password(password):
    return pwd_context.hash(password)


def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)


def create_token(data):

    expire = datetime.utcnow() + timedelta(hours=1)

    data.update({
        "exp": expire
    })

    return jwt.encode(
        data,
        SECRET_KEY,
        algorithm=ALGORITHM
    )