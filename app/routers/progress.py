import logging

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.messages import Messages
from app.core.response import api_response
from app.db.mongo import get_db
from app.deps import get_current_user
from app.schemas import ProgressResponse, ProgressUpdate


router = APIRouter()
logger = logging.getLogger("api.progress")


@router.post("", response_model=ProgressResponse)
async def update_progress(
    payload: ProgressUpdate,
    user=Depends(get_current_user),
):
    db = get_db()
    if not ObjectId.is_valid(payload.challenge_id):
        raise HTTPException(status_code=400, detail="Invalid challenge id")
    record = await db.user_challenges.find_one(
        {"user_id": str(user["_id"]), "challenge_id": payload.challenge_id}
    )
    if not record:
        raise HTTPException(status_code=404, detail="Challenge not joined")

    await db.user_challenges.update_one(
        {"_id": record["_id"]}, {"$set": {"progress": payload.progress_value}}
    )
    record["progress"] = payload.progress_value
    logger.info(
        "Progress updated: user=%s challenge=%s progress=%s",
        record["user_id"],
        record["challenge_id"],
        record["progress"],
    )
    return api_response(
        Messages.PROGRESS_UPDATED,
        {
            "id": str(record["_id"]),
            "user_id": record["user_id"],
            "challenge_id": record["challenge_id"],
            "joined_at": record["joined_at"],
            "progress": record["progress"],
        },
    )


@router.get("", response_model=ProgressResponse)
async def get_progress(
    challenge_id: str,
    user=Depends(get_current_user),
):
    db = get_db()
    if not ObjectId.is_valid(challenge_id):
        raise HTTPException(status_code=400, detail="Invalid challenge id")
    record = await db.user_challenges.find_one(
        {"user_id": str(user["_id"]), "challenge_id": challenge_id}
    )
    if not record:
        raise HTTPException(status_code=404, detail="Challenge not joined")
    return api_response(
        Messages.PROGRESS_FETCHED,
        {
            "id": str(record["_id"]),
            "user_id": record["user_id"],
            "challenge_id": record["challenge_id"],
            "joined_at": record["joined_at"],
            "progress": record["progress"],
        },
    )
