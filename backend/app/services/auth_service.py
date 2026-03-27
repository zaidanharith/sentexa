import logging
from datetime import timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.security import TokenResponse
from app.models.user import User

logger = logging.getLogger(__name__)

async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
	result = await db.execute(select(User).where(User.id == user_id))
	return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
	result = await db.execute(select(User).where(User.email == email))
	return result.scalar_one_or_none()

async def create_user(
	db: AsyncSession,
	*,
	name: str,
	email: str,
	password: str,
) -> User:

	existing = await get_user_by_email(db, email)
	if existing:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
		)

	user = User(
		name=name,
		email=email,
		password=security.hash_password(password),
	)

	db.add(user)
	try:
		await db.flush()
	except IntegrityError as exc:
		logger.warning("Integrity error creating user: %s", exc)
		await db.rollback()
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
		) from exc

	await db.refresh(user)
	return user

async def authenticate_user(
	db: AsyncSession, *, email: str, password: str
) -> User:
	user = await get_user_by_email(db, email)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)

	if not security.verify_password(password, user.password):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid credentials",
			headers={"WWW-Authenticate": "Bearer"},
		)

	return user

def issue_tokens(user: User) -> TokenResponse:
	payload = {"sub": str(user.id), "email": user.email}

	access_token = security.create_access_token(
		payload,
		expires_delta=timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES),
	)
	refresh_token = security.create_refresh_token(
		payload,
		expires_delta=timedelta(days=security.REFRESH_TOKEN_EXPIRE_DAYS),
	)

	return TokenResponse(access_token=access_token, refresh_token=refresh_token)

async def update_user(
	db: AsyncSession,
	user_id: int,
	*,
	name: Optional[str] = None,
	email: Optional[str] = None,
) -> User:
	"""Update user profile (name and email)"""
	user = await get_user_by_id(db, user_id)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User not found"
		)

	if email and email != user.email:
		existing = await get_user_by_email(db, email)
		if existing:
			raise HTTPException(
				status_code=status.HTTP_409_CONFLICT,
				detail="Email already in use"
			)
		user.email = email

	if name:
		user.name = name

	db.add(user)
	try:
		await db.flush()
		await db.commit()
		await db.refresh(user)
	except IntegrityError as exc:
		logger.warning("Integrity error updating user: %s", exc)
		await db.rollback()
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="Failed to update user"
		) from exc

	return user

def verify_refresh_token(token: str) -> Optional[dict]:
	try:
		payload = security.verify_refresh_token(token)
		if not payload:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Invalid token",
				headers={"WWW-Authenticate": "Bearer"},
			)
		return payload
	except JWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token",
			headers={"WWW-Authenticate": "Bearer"},
		) from exc
