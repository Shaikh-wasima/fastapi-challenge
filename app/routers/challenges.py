from datetime import datetime
import logging

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.messages import Messages
from app.core.response import api_response
from app.db.mongo import get_db
from app.deps import get_current_user
from app.schemas import (
    ChallengeCreate,
    ChallengeCreatedResponse,
    ChallengeListResponse,
    ChallengeOut,
    JoinResponse,
    UserChallengesResponse,
)


router = APIRouter()
logger = logging.getLogger("api.challenges")


@router.post("", response_model=ChallengeCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    payload: ChallengeCreate,
    _user=Depends(get_current_user),
):
    db = get_db()
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()
    result = await db.challenges.insert_one(data)
    logger.info("Challenge created: %s", data["title"])
    return api_response(Messages.CHALLENGE_CREATED, {"id": str(result.inserted_id), **data})


@router.get("", response_model=ChallengeListResponse)
async def list_active_challenges(_user=Depends(get_current_user)):
    db = get_db()
    cursor = db.challenges.find({"is_active": True})
    items = []
    async for doc in cursor:
        items.append(
            {
                "id": str(doc["_id"]),
                "title": doc["title"],
                "description": doc["description"],
                "target_value": doc["target_value"],
                "duration_days": doc["duration_days"],
                "is_active": doc["is_active"],
                "created_at": doc["created_at"],
            }
        )
    return api_response(Messages.CHALLENGES_FETCHED, items)


@router.post("/{challenge_id}/join", response_model=JoinResponse, status_code=status.HTTP_201_CREATED)
async def join_challenge(
    challenge_id: str,
    user=Depends(get_current_user),
):
    db = get_db()
    if not ObjectId.is_valid(challenge_id):
        raise HTTPException(status_code=400, detail="Invalid challenge id")
    challenge = await db.challenges.find_one({"_id": ObjectId(challenge_id)})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if not challenge.get("is_active", True):
        raise HTTPException(status_code=400, detail="Challenge is not active")

    existing = await db.user_challenges.find_one(
        {"user_id": str(user["_id"]), "challenge_id": challenge_id}
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already joined")

    join = {
        "user_id": str(user["_id"]),
        "challenge_id": challenge_id,
        "joined_at": datetime.utcnow(),
        "progress": 0,
    }
    result = await db.user_challenges.insert_one(join)
    logger.info("User joined challenge: user=%s challenge=%s", join["user_id"], join["challenge_id"])
    return api_response(Messages.CHALLENGE_JOINED, {"id": str(result.inserted_id), **join})


@router.get("/my", response_model=UserChallengesResponse)
async def list_my_challenges(user=Depends(get_current_user)):
    db = get_db()
    cursor = db.user_challenges.find({"user_id": str(user["_id"])})
    items = []
    async for doc in cursor:
        challenge = await db.challenges.find_one({"_id": ObjectId(doc["challenge_id"])})
        if not challenge:
            continue
        items.append(
            {
                "id": str(doc["_id"]),
                "challenge_id": doc["challenge_id"],
                "joined_at": doc["joined_at"],
                "progress": doc["progress"],
                "challenge": {
                    "id": str(challenge["_id"]),
                    "title": challenge["title"],
                    "description": challenge["description"],
                    "target_value": challenge["target_value"],
                    "duration_days": challenge["duration_days"],
                    "is_active": challenge["is_active"],
                    "created_at": challenge["created_at"],
                },
            }
        )
    return api_response(Messages.MY_CHALLENGES_FETCHED, items)
