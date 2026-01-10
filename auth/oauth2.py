from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db.database import get_async_db
from jose import JWTError, jwt
import os

# 1. Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# 2. Define the scheme
# This tells Swagger UI where to find the token (the URL of your auth service)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8004/login")


# 3. The Dependency
async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> int:
    """
    Decodes the token, verifies validity, and returns the User id.
    """
    if not SECRET_KEY:
        raise ValueError("CRITICAL: SECRET_KEY environment variable is required.")
    if not ALGORITHM:
        raise ValueError("CRITICAL: ALGORITHM environment variable is required.")
    try:
        payload: dict[str, str] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Extract the user ID
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Did not find the user id in the payload",
        )
    try:
        return int(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User ID format is invalid: {e}",
        )
