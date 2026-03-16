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
		"duration_options": [
			{
				"code": "weekly",
				"name": "Weekly",
				"price": 29000,
				"currency": "IDR",
				"duration_days": 7,
			},
			{
				"code": "monthly",
				"name": "Monthly",
				"price": 99000,
				"currency": "IDR",
				"duration_days": 30,
			},
			{
				"code": "annual",
				"name": "Annual",
				"price": 899000,
				"currency": "IDR",
				"duration_days": 365,
			},
		],
	},
}

_LEGACY_PREMIUM_CODES: set[str] = {"weekly", "monthly", "annual"}

def _normalized_plan(plan_value: str) -> PlanCode:
	if plan_value in _PLANS:
		return plan_value
	if plan_value in _LEGACY_PREMIUM_CODES:
		return "premium"
	return "free"

def _get_duration_option(duration_code: PremiumDurationCode) -> DurationOption:
	premium_options = _PLANS["premium"]["duration_options"]
	for option in premium_options:
		if option["code"] == duration_code:
			return DurationOption(**option)

	raise HTTPException(
		status_code=status.HTTP_400_BAD_REQUEST,
		detail="Invalid premium duration",
	)

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
	expires_at = user.subscription_expires_at

	if expires_at is not None and expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)

	status = "active"
	if expires_at is not None and expires_at < now:
		status = "expired"

	return SubscriptionStatus(
		plan=_normalized_plan(user.subscription),
		status=status,
		remaining_quota=user.subscription_quota_remaining,
		expires_at=user.subscription_expires_at,
	)

async def subscribe_user(
	db: AsyncSession,
	user: User,
	plan_code: PlanCode,
	duration_code: PremiumDurationCode | None,
) -> SubscriptionStatus:
	plan = _PLANS[plan_code]
	user.subscription = plan_code
	user.subscription_quota_remaining = plan["quota"]

	if plan_code == "free":
		user.subscription_expires_at = None
	elif duration_code is None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Duration is required for premium plan",
		)
	else:
		duration = _get_duration_option(duration_code)
		user.subscription_expires_at = datetime.now(timezone.utc) + timedelta(
			days=duration.duration_days
		)

	await db.flush()
	await db.refresh(user)
	return get_user_subscription_status(user)
