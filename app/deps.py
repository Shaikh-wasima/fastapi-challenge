from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.security import ALGORITHM, SECRET_KEY
from app.db.mongo import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = get_db()
    user = await db.users.find_one({"email": subject})
    if not user:
        raise credentials_exception
    return user
