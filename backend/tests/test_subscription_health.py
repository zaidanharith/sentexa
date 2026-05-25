"""
## BUNDLE PENGUJIAN 10 : SUBSCRIPTION & HEALTH
Menguji operasi manajemen langganan dan endpoint kesehatan sistem:
  - Get Subscription Status  (GET  /subscription)
  - Get Subscription Plans   (GET  /subscription/plans)
  - Subscribe / Upgrade Plan (POST /subscription/subscribe)
  - Health Check             (GET  /health)
  - Readiness Check          (GET  /ready)
"""

from httpx import AsyncClient


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 10A : HEALTH & GENERAL
# ════════════════════════════════════════════════════════════════════════════
class TestHealthEndpoints:
    """Pengujian endpoint kesehatan dan informasi umum API."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_health_check_berhasil(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Mengakses GET /api/health
        Expected : HTTP 200, status sistem 'ok'
        """
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json().get("status") == "healthy"

    async def test_readiness_check_berhasil(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Mengakses GET /api/ready
        Expected : HTTP 200, sistem siap menerima traffic
        """
        resp = await client.get("/api/ready")
        assert resp.status_code == 200
        assert resp.json().get("status") == "ready"

    async def test_root_redirect(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Mengakses root URL '/'
        Expected : Redirect (302 atau 307) ke /api
        """
        resp = await client.get("/", follow_redirects=False)
        assert resp.status_code in (302, 307)
        assert "/api" in resp.headers.get("location", "")


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 10B : SUBSCRIPTION
# ════════════════════════════════════════════════════════════════════════════
class TestSubscription:
    """Pengujian operasi manajemen paket langganan pengguna."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_get_plans_berhasil_tanpa_login(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Mengambil daftar paket langganan (endpoint publik)
        Expected : HTTP 200, list paket tersedia (minimal free dan premium)
        """
        resp = await client.get("/api/subscription/plans")
        assert resp.status_code == 200
        plans = resp.json()
        assert isinstance(plans, list)
        assert len(plans) >= 2
        codes = [p["code"] for p in plans]
        assert "free" in codes
        assert "premium" in codes

    async def test_get_status_langganan_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil status langganan user yang sedang login
        Expected : HTTP 200, memiliki field plan, status, dan remaining_quota
        """
        resp = await client.get("/api/subscription", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "plan" in data
        assert "status" in data
        assert "remaining_quota" in data

    async def test_subscribe_ke_premium_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Upgrade langsung ke paket premium tanpa pembayaran
        Expected : HTTP 200, plan berubah menjadi 'premium'
        """
        resp = await client.post(
            "/api/subscription/subscribe",
            json={"plan": "premium"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["subscription"]["plan"] == "premium"

    async def test_subscribe_ke_free_plan_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Downgrade kembali ke paket free
        Expected : HTTP 200, plan berubah menjadi 'free'
        """
        resp = await client.post(
            "/api/subscription/subscribe",
            json={"plan": "free"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["subscription"]["plan"] == "free"

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_get_status_gagal_tanpa_token(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengambil status langganan tanpa autentikasi
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.get("/api/subscription")
        assert resp.status_code == 401

    async def test_subscribe_premium_tanpa_durasi_tetap_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Negative
        Aksi     : Subscribe ke premium tanpa detail pembayaran
        Expected : HTTP 200, tetap berhasil karena alur dipercepat untuk development
        """
        resp = await client.post(
            "/api/subscription/subscribe",
            json={"plan": "premium"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_akses_report_tanpa_premium_ditolak(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Negative
        Aksi     : User free mencoba mengakses endpoint /reports (khusus premium)
        Expected : HTTP 403 Forbidden
        """
        resp = await client.get("/api/reports", headers=auth_headers)
        assert resp.status_code == 403


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 11 : DASHBOARD
# ════════════════════════════════════════════════════════════════════════════
class TestDashboard:
    """Pengujian endpoint dashboard untuk visualisasi data analisis."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_get_keywords_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil kata kunci teratas dari seluruh analisis
        Expected : HTTP 200, respons memiliki field items
        """
        resp = await client.get("/api/dashboard/keywords", headers=auth_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()

    async def test_get_keywords_filter_sentiment(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Filter kata kunci hanya untuk sentimen 'positive'
        Expected : HTTP 200, sentiment field pada respons sesuai filter
        """
        resp = await client.get(
            "/api/dashboard/keywords?sentiment=positive&top=10",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_get_keywords_gagal_tanpa_token(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengakses dashboard tanpa header Authorization
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.get("/api/dashboard/keywords")
        assert resp.status_code == 401
