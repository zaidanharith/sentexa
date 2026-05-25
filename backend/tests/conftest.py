"""
## PREREQUISITE
Konfigurasi dasar pengujian otomatis untuk Sentexa API.
Berisi fixtures (pengganti hook) yang digunakan di seluruh test bundle:
  - app            : instance FastAPI dengan DB SQLite in-memory
  - client         : AsyncClient httpx yang terhubung ke app
  - auth_headers   : header Authorization berisi Bearer token user uji
  - premium_headers: header Authorization untuk user premium

Jalankan dengan:
    cd backend
    pytest tests/ -v
"""

import os
import sys
from types import ModuleType
from unittest.mock import MagicMock

# ════════════════════════════════════════════════════════════════════════════
# MOCK MODUL ML SEBELUM IMPORT APP
# (torch, transformers, dan modul ML lain tidak tersedia di lingkungan uji)
# ════════════════════════════════════════════════════════════════════════════

# Stub modul pihak ketiga yang berat
for _stub in [
    "torch", "torch.nn", "torch.nn.functional",
    "transformers",
    "pandas",
    "sklearn", "sklearn.model_selection", "sklearn.metrics",
]:
    if _stub not in sys.modules:
        sys.modules[_stub] = MagicMock()

# Stub modul internal ML Sentexa
for _ml in [
    "ml", "ml.inference", "ml.inference.predict",
    "ml.model", "ml.model.config",
    "ml.preprocessing", "ml.preprocessing.cleaning",
    "ml.preprocessing.normalization", "ml.preprocessing.stopwords",
]:
    if _ml not in sys.modules:
        sys.modules[_ml] = MagicMock()

# Pastikan PredictionError dan fungsi predict tersedia sebagai atribut mock
import ml.inference.predict as _ml_predict  # type: ignore
_ml_predict.PredictionError = type("PredictionError", (ValueError,), {})
_ml_predict.predict_text = MagicMock()
_ml_predict.predict_texts = MagicMock()

# ── Konfigurasi environment ──────────────────────────────────────────────────
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-sentexa-testing-only")
os.environ.setdefault("ENVIRONMENT", "development")

# ── Import utama setelah stub terpasang ────────────────────────────────────
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.core.database import Base
from app.api import deps

# ════════════════════════════════════════════════════════════════════════════
# DATABASE PENGUJIAN — SQLite in-memory
# ════════════════════════════════════════════════════════════════════════════
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Nilai kembalian mock prediksi ML
MOCK_PREDICT_SINGLE = {
    "label": "positive",
    "label_id": 2,
    "score": 0.95,
    "scores": {"negative": 0.02, "neutral": 0.03, "positive": 0.95},
}
MOCK_PREDICT_BATCH = [
    {
        "label": "positive",
        "label_id": 2,
        "score": 0.91,
        "scores": {"negative": 0.03, "neutral": 0.06, "positive": 0.91},
    },
    {
        "label": "negative",
        "label_id": 0,
        "score": 0.87,
        "scores": {"negative": 0.87, "neutral": 0.09, "positive": 0.04},
    },
]


# ── Override dependency database ─────────────────────────────────────────────
async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


app.dependency_overrides[deps.get_db] = override_get_db


# ════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ════════════════════════════════════════════════════════════════════════════

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """Hook session: buat tabel sebelum pengujian, hapus setelah selesai."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
def mock_app_engine():
    """
    Override app's engine with test engine.
    Ensures health checks use in-memory SQLite instead of Supabase.
    """
    from unittest.mock import patch
    from app.core import database
    
    # Store original engines
    orig_db_engine = database.engine
    orig_async_session_local = database.AsyncSessionLocal
    
    # Replace with test engine
    database.engine = test_engine
    database.AsyncSessionLocal = TestSessionLocal
    
    yield
    
    # Restore (not strictly needed for tests but good practice)
    database.engine = orig_db_engine
    database.AsyncSessionLocal = orig_async_session_local


@pytest_asyncio.fixture
async def client():
    """AsyncClient terhubung ke FastAPI app via ASGI (tanpa server nyata)."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient):
    """
    Hook beforeEach: daftarkan & login user free.
    Kembalikan header Authorization berisi Bearer token user uji
    """
    import uuid
    email = f"testuser_{uuid.uuid4().hex}@example.com"
    password = "TestPass1"
    await client.post(
        "/api/auth/register",
        json={"name": "Test User Sentexa", "email": email, "password": password},
    )
    resp = await client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert resp.status_code == 200, f"Login gagal saat setup fixture: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def premium_headers(client: AsyncClient):
    """
    Hook beforeEach: daftarkan, login, dan upgrade langsung ke premium.
    Kembalikan header Authorization untuk user premium.
    """
    import uuid
    email = f"premium_{uuid.uuid4().hex}@example.com"
    password = "PremPass2"
    await client.post(
        "/api/auth/register",
        json={"name": "Premium User Sentexa", "email": email, "password": password},
    )
    resp = await client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    await client.post(
        "/api/subscription/subscribe",
        json={"plan": "premium"},
        headers=headers,
    )
    return headers
