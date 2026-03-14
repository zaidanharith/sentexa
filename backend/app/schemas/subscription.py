from datetime import datetime
from typing import Literal
from pydantic import BaseModel

PlanCode = Literal["free", "premium"]
PremiumDurationCode = Literal["weekly", "monthly", "annual"]

class DurationOption(BaseModel):
	code: PremiumDurationCode
	name: str
	price: int
	currency: str
	duration_days: int

class SubscriptionPlan(BaseModel):
	code: PlanCode
	name: str
	quota: int
	features: list[str]
	duration_options: list[DurationOption] = []

class SubscriptionStatus(BaseModel):
	plan: PlanCode
	status: Literal["active", "expired"]
	remaining_quota: int
	expires_at: datetime | None

class SubscribeRequest(BaseModel):
	plan: PlanCode
	duration: PremiumDurationCode | None = None

class SubscribeResponse(BaseModel):
	detail: str
	subscription: SubscriptionStatus
