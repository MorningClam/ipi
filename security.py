from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import uuid
import models, schemas

SECRET_KEY = "a_very_secret_key_for_your_app"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours instead of 30 minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_user(db: Session, user: schemas.UserCreate):
    # Generate a UUID for the user ID
    user_id = str(uuid.uuid4())
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        id=user_id,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        profile_picture_url=""
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user