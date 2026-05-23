from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.subscription import (
	DurationOption,
	PlanCode,
	PremiumDurationCode,
	SubscriptionPlan,
	SubscriptionStatus,
)

_PLANS: dict[PlanCode, dict] = {
	"free": {
		"name": "Free",
		"quota": 5,
		"features": [
			"Manual text analysis only (tanpa upload CSV/Excel)",
			"Maksimal 5 pengiriman teks per hari",
			"Tidak ada akses export report",
		],
		"duration_options": [],
	},
	"premium": {
		"name": "Premium",
		"quota": 999999,
		"features": [
			"Upload file ulasan multi-format (CSV/Excel)",
			"Pengiriman teks tanpa batas",
			"Akses exportable reports",
		],
		"duration_options": [],
	},
}

_LEGACY_PREMIUM_CODES: set[str] = {"weekly", "monthly", "annual"}

def _normalized_plan(plan_value: str) -> PlanCode:
	if plan_value in _PLANS:
		return plan_value
	if plan_value in _LEGACY_PREMIUM_CODES:
		return "premium"
	return "free"

def get_subscription_plans() -> list[SubscriptionPlan]:
	return [
		SubscriptionPlan(
			code=code,
			name=plan["name"],
			quota=plan["quota"],
			features=plan["features"],
			duration_options=[DurationOption(**opt) for opt in plan["duration_options"]],
		)
		for code, plan in _PLANS.items()
	]

def get_user_subscription_status(user: User) -> SubscriptionStatus:
	now = datetime.now(timezone.utc)
	expires_at = user.subscription_end

	if expires_at is not None and expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)

	status = "active"
	if expires_at is not None and expires_at < now:
		status = "expired"

	return SubscriptionStatus(
		plan=_normalized_plan(user.subscription_plan),
		status=status,
		remaining_quota=user.analysis_quota,
		expires_at=user.subscription_end,
	)

async def subscribe_user(
	db: AsyncSession,
	user: User,
	plan_code: PlanCode,
	duration_code: PremiumDurationCode | None,
) -> SubscriptionStatus:
	plan = _PLANS[plan_code]
	user.subscription_plan = plan_code
	user.analysis_quota = plan["quota"]

	if plan_code == "free":
		user.subscription_end = None
		user.subscription_start = None
		user.subscription_status = "active"
	else:
		now = datetime.now(timezone.utc)
		user.subscription_start = now
		user.subscription_end = None
		user.subscription_status = "active"

	await db.flush()
	await db.refresh(user)
	return get_user_subscription_status(user)


async def validate_and_reduce_quota(
	db: AsyncSession,
	user: User,
	amount_needed: int,
) -> None:
	if user.analysis_quota < amount_needed:
		raise HTTPException(
			status_code=status.HTTP_429_TOO_MANY_REQUESTS,
			detail=f"Insufficient quota. Required: {amount_needed}, Available: {user.analysis_quota}",
		)
	
	user.analysis_quota -= amount_needed
	await db.flush()
	await db.refresh(user)
