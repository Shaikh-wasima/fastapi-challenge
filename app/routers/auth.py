from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from app.core.security import create_access_token, hash_password, verify_password
from app.db.mongo import get_db
from app.core.messages import Messages
from app.core.response import api_response
from app.schemas import Token, TokenResponse, UserCreate, UserCreatedResponse


router = APIRouter()
logger = logging.getLogger("api.auth")


@router.post("/register", response_model=UserCreatedResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate):
    db = get_db()
    user = {
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "created_at": datetime.utcnow(),
    }
    try:
        result = await db.users.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("User registered: %s", user["email"])
    return api_response(
        Messages.USER_REGISTERED,
        {
            "id": str(result.inserted_id),
            "email": user["email"],
            "created_at": user["created_at"],
        },
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token(subject=user["email"])
    logger.info("User login: %s", user["email"])
    return api_response(
        Messages.LOGIN_SUCCESS,
        {"access_token": token, "token_type": "bearer"},
    )


@router.post("/token", response_model=Token)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = get_db()
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    token_value = create_access_token(subject=user["email"])
    return {"access_token": token_value, "token_type": "bearer"}
