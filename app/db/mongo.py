from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import MONGODB_CREATE_INDEXES, MONGODB_DB_NAME, MONGODB_URL

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        # Singleton client to reuse connections across requests.
        _client = AsyncIOMotorClient(MONGODB_URL)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    return get_client()[MONGODB_DB_NAME]


async def init_db() -> None:
    if not MONGODB_CREATE_INDEXES:
        return
    db = get_db()
    # Unique email for accounts.
    await db.users.create_index("email", unique=True)
    # Prevent duplicate joins per user per challenge.
    await db.user_challenges.create_index(
        [("user_id", 1), ("challenge_id", 1)], unique=True
    )


def close_db() -> None:
    client = get_client()
    client.close()
