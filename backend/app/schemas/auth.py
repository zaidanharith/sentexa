from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class RegisterRequest(BaseModel):
	name: str
	email: EmailStr
	password: str


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class RefreshTokenRequest(BaseModel):
	refresh_token: str


class UpdateProfileRequest(BaseModel):
	firstName: str
	lastName: str
	email: EmailStr


class UserOut(BaseModel):
	id: int
	name: str
	email: EmailStr
	created_at: datetime
	analysis_quota: int
	subscription_plan: str
	subscription_status: str
	subscription_start: datetime | None = None
	subscription_end: datetime | None = None
 
	model_config = ConfigDict(from_attributes=True)


class LogoutResponse(BaseModel):
	detail: str
