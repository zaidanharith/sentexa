import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User
from app.core.security import create_access_token
from tests.conftest import TestSessionLocal

MOCK_SINGLE = {
    "label": "positive",
    "label_id": 2,
    "score": 0.95,
    "scores": {"negative": 0.02, "neutral": 0.03, "positive": 0.95},
}

class TestQuotaSystem:
    async def create_test_user(self, email: str, plan: str = "free", quota: int = 5, last_reset: datetime = None) -> User:
        async with TestSessionLocal() as session:
            user = User(
                name="Quota Test User",
                email=email,
                password="TestPassword123",
                subscription_plan=plan,
                subscription_status="active",
                analysis_quota=quota,
                last_quota_reset=last_reset,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    def get_auth_headers(self, user: User) -> dict:
        token = create_access_token(data={"sub": str(user.id)})
        return {"Authorization": f"Bearer {token}"}

    async def test_free_user_quota_deduction(self, client: AsyncClient):
        # 1. Create a free user with quota = 5, reset today
        email = f"quota_free_{uuid.uuid4().hex}@example.com"
        user = await self.create_test_user(email, plan="free", quota=5, last_reset=datetime.now(timezone.utc))
        headers = self.get_auth_headers(user)

        # 2. Perform 1 analysis
        with patch("app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "Ini tes analisis sentimen.", "include_scores": True},
                headers=headers,
            )
        assert resp.status_code == 200

        # 3. Check that the quota in the DB is reduced to 4
        async with TestSessionLocal() as session:
            stmt = select(User).where(User.id == user.id)
            res = await session.execute(stmt)
            updated_user = res.scalar_one()
            assert updated_user.analysis_quota == 4

    async def test_free_user_quota_exhaustion(self, client: AsyncClient):
        # 1. Create a free user with quota = 0, reset today
        email = f"quota_exhausted_{uuid.uuid4().hex}@example.com"
        user = await self.create_test_user(email, plan="free", quota=0, last_reset=datetime.now(timezone.utc))
        headers = self.get_auth_headers(user)

        # 2. Perform analysis - should fail with HTTP 429
        with patch("app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "Mestinya ini ditolak karena kuota habis.", "include_scores": True},
                headers=headers,
            )
        assert resp.status_code == 429
        assert "Insufficient quota" in resp.json()["detail"]

    async def test_premium_user_unlimited_quota(self, client: AsyncClient):
        # 1. Create a premium user with quota = 0, reset today
        email = f"quota_premium_{uuid.uuid4().hex}@example.com"
        user = await self.create_test_user(email, plan="premium", quota=0, last_reset=datetime.now(timezone.utc))
        headers = self.get_auth_headers(user)

        # 2. Perform analysis - should succeed (bypass quota check)
        with patch("app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "Premium bebas melakukan analisis.", "include_scores": True},
                headers=headers,
            )
        assert resp.status_code == 200

        # 3. Quota in the DB should remain 0 (not reduced)
        async with TestSessionLocal() as session:
            stmt = select(User).where(User.id == user.id)
            res = await session.execute(stmt)
            updated_user = res.scalar_one()
            assert updated_user.analysis_quota == 0

    async def test_daily_quota_reset_wib(self, client: AsyncClient):
        # WIB timezone is UTC+7
        WIB = timezone(timedelta(hours=7))
        now_wib = datetime.now(timezone.utc).astimezone(WIB)
        
        # Set last_quota_reset to yesterday in WIB
        yesterday_wib = now_wib - timedelta(days=1)
        # Convert back to UTC representation for database
        yesterday_utc = yesterday_wib.astimezone(timezone.utc).replace(tzinfo=None)

        email = f"quota_reset_{uuid.uuid4().hex}@example.com"
        # User has quota = 1, but last reset was yesterday
        user = await self.create_test_user(email, plan="free", quota=1, last_reset=yesterday_utc)
        headers = self.get_auth_headers(user)

        # Accessing any authenticated endpoint (e.g. GET /api/users/me or POST /api/sentiment/predict) should trigger reset.
        # Let's perform a prediction
        with patch("app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "Harus mereset kuota ke 5 lalu berkurang jadi 4.", "include_scores": True},
                headers=headers,
            )
        assert resp.status_code == 200

        # Quota should have been reset to 5, and then reduced by 1 for the prediction, so it's 4.
        async with TestSessionLocal() as session:
            stmt = select(User).where(User.id == user.id)
            res = await session.execute(stmt)
            updated_user = res.scalar_one()
            assert updated_user.analysis_quota == 4
            assert updated_user.last_quota_reset is not None
            
            # verify that the updated last_quota_reset date is today in WIB
            last_reset_wib = updated_user.last_quota_reset.replace(tzinfo=timezone.utc).astimezone(WIB)
            assert last_reset_wib.date() == now_wib.date()
