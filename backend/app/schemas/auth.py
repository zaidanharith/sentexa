from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class RegisterRequest(BaseModel):
	name: str
	email: EmailStr
	password: str


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class UpdateProfileRequest(BaseModel):
	firstName: str
	lastName: str
	email: EmailStr


class UserOut(BaseModel):
	id: int
	name: str
	email: EmailStr
	subscription: str
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class LogoutResponse(BaseModel):
	detail: str
