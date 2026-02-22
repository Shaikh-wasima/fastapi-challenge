from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, EmailStr, conint


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    message: str
    data: T


class ChallengeCreate(BaseModel):
    title: str
    description: str
    target_value: conint(gt=0)  # type: ignore[valid-type]
    duration_days: conint(gt=0)  # type: ignore[valid-type]
    is_active: bool = True


class ChallengeOut(BaseModel):
    id: str
    title: str
    description: str
    target_value: int
    duration_days: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class JoinOut(BaseModel):
    id: str
    user_id: str
    challenge_id: str
    joined_at: datetime
    progress: int

    class Config:
        from_attributes = True


class ProgressUpdate(BaseModel):
    challenge_id: str
    progress_value: conint(ge=0)  # type: ignore[valid-type]


class UserCreatedResponse(ApiResponse[UserPublic]):
    pass


class TokenResponse(ApiResponse[Token]):
    pass


class ChallengeCreatedResponse(ApiResponse[ChallengeOut]):
    pass


class ChallengeListResponse(ApiResponse[list[ChallengeOut]]):
    pass


class JoinResponse(ApiResponse[JoinOut]):
    pass


class ProgressResponse(ApiResponse[JoinOut]):
    pass


class UserChallengeOut(BaseModel):
    id: str
    challenge_id: str
    joined_at: datetime
    progress: int
    challenge: ChallengeOut


class UserChallengesResponse(ApiResponse[list[UserChallengeOut]]):
    pass
