from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db as _get_db
from app.core.security import verify_access_token
from app.models.user import User
from app.services import auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
	async for session in _get_db():
		yield session

async def get_current_user(
	db: AsyncSession = Depends(get_db),
	token: str = Depends(oauth2_scheme),
) -> User:
	payload = verify_access_token(token)
	if not payload:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid or expired token",
			headers={"WWW-Authenticate": "Bearer"},
		)

	sub = payload.get("sub")
	if not isinstance(sub, (str, int)):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token payload",
			headers={"WWW-Authenticate": "Bearer"},
		)

	try:
		user_id = int(sub)
	except ValueError:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token payload",
			headers={"WWW-Authenticate": "Bearer"},
		)

	user = await auth_service.get_user_by_id(db, user_id)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="User not found",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return user
