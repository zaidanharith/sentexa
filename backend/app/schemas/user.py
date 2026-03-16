from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class User(BaseModel):
	id: int
	name: str
	email: EmailStr
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
