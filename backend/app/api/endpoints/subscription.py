from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.subscription import (
	SubscribeRequest,
	SubscribeResponse,
	SubscriptionPlan,
	SubscriptionStatus,
)
from app.services import subscription_service

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("", response_model=SubscriptionStatus)
async def get_subscription(current_user: User = Depends(deps.get_current_user)):
	return subscription_service.get_user_subscription_status(current_user)

@router.get("/plans", response_model=list[SubscriptionPlan])
async def get_subscription_plans():
	return subscription_service.get_subscription_plans()

@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(
	payload: SubscribeRequest,
	db: AsyncSession = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	subscription = await subscription_service.subscribe_user(
		db=db,
		user=current_user,
		plan_code=payload.plan,
		duration_code=payload.duration,
	)
	return SubscribeResponse(
		detail="Subscription updated successfully",
		subscription=subscription,
	)
