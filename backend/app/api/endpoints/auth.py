from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.schemas.auth import LoginRequest, LogoutResponse, RegisterRequest, UserOut, UpdateProfileRequest
from app.core.security import TokenResponse
from app.models.user import User
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(deps.get_db)):
	user = await auth_service.create_user(
		db,
		name=payload.name,
		email=payload.email,
		password=payload.password,
	)
	return auth_service.issue_tokens(user)

@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(deps.get_db)):
	user = await auth_service.authenticate_user(
		db, email=payload.email, password=payload.password
	)
	return auth_service.issue_tokens(user)

@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(deps.get_current_user)):
	return current_user

@router.put("/me", response_model=UserOut)
async def update_profile(
	payload: UpdateProfileRequest,
	current_user: User = Depends(deps.get_current_user),
	db: AsyncSession = Depends(deps.get_db)
):
	"""Update user profile (name and email)"""
	user = await auth_service.update_user(
		db,
		user_id=current_user.id,
		name=f"{payload.firstName} {payload.lastName}".strip(),
		email=payload.email
	)
	return user

@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: User = Depends(deps.get_current_user)):
	_ = current_user
	return LogoutResponse(detail="Logout successful")


