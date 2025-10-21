import os
from functools import wraps
import jwt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from fastapi import status
from fastapi.exceptions import HTTPException
from nicegui import app

import TEL.database.user as db_user
from TEL.model import UserInfo, Permission

load_dotenv()

# =============================================================================
# AUTHENTICATION SETUP
# =============================================================================

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> UserInfo | bool:
    user = db_user._get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

async def get_current_user(token: str) -> Optional[UserInfo]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = decode_access_token(token)       
        username = payload.get("sub")        
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = db_user.get_user_by_username(username=username)
    if user is None:
        raise credentials_exception
    return UserInfo.model_validate(user)

def refresh_token(token: str) -> None:
    expire_minutes = 15
    if ACCESS_TOKEN_EXPIRE_MINUTES/10 > expire_minutes:
        expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES/10
        
    payload = decode_access_token(token)
    username = payload.get('sub')
    expire_datetime = datetime.fromtimestamp(payload.get('exp'), timezone.utc)
    time_delta = expire_datetime - datetime.now(timezone.utc)
    time_delta = time_delta.total_seconds()/60
    if time_delta < expire_minutes:
        new_token = create_access_token(data={'sub': username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        app.storage.user.update({'token': new_token})


# =============================================================================
# AUTHENTICATION MIDDLEWARE
# =============================================================================

def require_auth(permission: Permission | None = Permission.read):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Auth prüfen nur auf Basis globalem State (nicht mit Request-Parametern!)
            missing_permission = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Missing permissions')
            unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
            
            token = app.storage.user.get('token')
            if token is None:
                raise unauthorized
            
            try:
                user = await get_current_user(token)
            except HTTPException:
                app.storage.user.clear()
                raise unauthorized
                        
            if permission == Permission.read:
                if user.permission not in [Permission.read, Permission.write, Permission.admin]:
                    raise missing_permission
            elif permission == Permission.write:
                if user.permission not in [Permission.write, Permission.admin]:
                    raise missing_permission
            elif permission == Permission.admin:
                if user.permission not in [Permission.admin]:
                    raise missing_permission
            
            refresh_token(token)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator