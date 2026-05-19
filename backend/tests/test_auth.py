"""
## BUNDLE PENGUJIAN 1 & 2 : AUTENTIKASI
Menguji seluruh siklus bisnis autentikasi pengguna:
  - Register (positive & negative)
  - Login (positive & negative)
  - Refresh Token
  - Get Profile (GET /me)
  - Update Profile (PUT /me)
  - Logout
"""

import pytest
from httpx import AsyncClient


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 1 : REGISTER
# ════════════════════════════════════════════════════════════════════════════
class TestRegister:
    """Pengujian operasi pendaftaran akun pengguna baru."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_register_berhasil_dengan_data_valid(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Mendaftar dengan nama, email, dan password yang valid
        Expected : HTTP 201, response memiliki access_token
        """
        resp = await client.post(
            "/api/auth/register",
            json={
                "name": "Budi Santoso",
                "email": "budi.santoso@test.com",
                "password": "SecureP1",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_register_gagal_email_duplikat(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mendaftar dengan email yang sudah terdaftar
        Expected : HTTP 409 Conflict
        """
        payload = {
            "name": "Siti Rahayu",
            "email": "duplikat@test.com",
            "password": "Pass1",
        }
        # Daftar pertama kali
        await client.post("/api/auth/register", json=payload)
        # Daftar ulang dengan email sama
        resp = await client.post("/api/auth/register", json=payload)
        assert resp.status_code == 409

    async def test_register_gagal_email_tidak_valid(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mendaftar dengan format email yang salah
        Expected : HTTP 422 Unprocessable Entity
        """
        resp = await client.post(
            "/api/auth/register",
            json={
                "name": "Andi",
                "email": "bukan-email-valid",
                "password": "Pass1",
            },
        )
        assert resp.status_code == 422

    async def test_register_gagal_tanpa_password(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mendaftar tanpa mengisi field password
        Expected : HTTP 422 Unprocessable Entity
        """
        resp = await client.post(
            "/api/auth/register",
            json={"name": "Dewi", "email": "dewi@test.com"},
        )
        assert resp.status_code == 422


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 2 : LOGIN
# ════════════════════════════════════════════════════════════════════════════
class TestLogin:
    """Pengujian operasi login pengguna terdaftar."""

    @pytest.fixture(autouse=True)
    async def _setup_user(self, client: AsyncClient):
        """Hook beforeEach: pastikan user uji sudah terdaftar."""
        await client.post(
            "/api/auth/register",
            json={
                "name": "Login Tester",
                "email": "login.tester@test.com",
                "password": "LoginP1",
            },
        )

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_login_berhasil_dengan_kredensial_benar(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Login dengan email dan password yang benar
        Expected : HTTP 200, response memiliki access_token dan refresh_token
        """
        resp = await client.post(
            "/api/auth/login",
            json={"email": "login.tester@test.com", "password": "LoginP1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_login_gagal_password_salah(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Login dengan password yang salah
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.post(
            "/api/auth/login",
            json={"email": "login.tester@test.com", "password": "WrongPass"},
        )
        assert resp.status_code == 401

    async def test_login_gagal_email_tidak_terdaftar(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Login dengan email yang belum pernah didaftarkan
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.post(
            "/api/auth/login",
            json={"email": "tidakada@test.com", "password": "Anything1"},
        )
        assert resp.status_code == 401

    async def test_login_gagal_tanpa_email(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Login tanpa menyertakan field email
        Expected : HTTP 422 Unprocessable Entity
        """
        resp = await client.post(
            "/api/auth/login", json={"password": "LoginP1"}
        )
        assert resp.status_code == 422


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 3 : REFRESH TOKEN
# ════════════════════════════════════════════════════════════════════════════
class TestRefreshToken:
    """Pengujian pembaruan access token menggunakan refresh token."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_refresh_berhasil_dengan_token_valid(self, client: AsyncClient):
        """
        Kondisi  : Positive
        Aksi     : Mengirim refresh_token yang valid
        Expected : HTTP 200, mendapatkan access_token baru
        """
        # Daftar dan login untuk mendapatkan refresh token
        await client.post(
            "/api/auth/register",
            json={
                "name": "Refresh Tester",
                "email": "refresh.tester@test.com",
                "password": "RefreshP1",
            },
        )
        login_resp = await client.post(
            "/api/auth/login",
            json={"email": "refresh.tester@test.com", "password": "RefreshP1"},
        )
        refresh_token = login_resp.json()["refresh_token"]

        resp = await client.post(
            "/api/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_refresh_gagal_token_palsu(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengirim refresh_token yang tidak valid / dipalsukan
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.post(
            "/api/auth/refresh",
            json={"refresh_token": "token.palsu.tidak.valid.sama.sekali"},
        )
        assert resp.status_code == 401


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 4 : PROFILE (GET & UPDATE ME)
# ════════════════════════════════════════════════════════════════════════════
class TestProfile:
    """Pengujian operasi melihat dan memperbarui profil pengguna."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_get_profile_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengakses GET /api/auth/me dengan token valid
        Expected : HTTP 200, data profil pengguna (id, name, email, dll.)
        """
        resp = await client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert "name" in data
        assert "email" in data
        assert "subscription_plan" in data

    async def test_update_profile_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Memperbarui nama depan dan belakang via PUT /api/auth/me
        Expected : HTTP 200, nama pada respons sudah diperbarui
        """
        resp = await client.put(
            "/api/auth/me",
            json={
                "firstName": "Nama",
                "lastName": "Diperbarui",
                "email": "testuser_sentexa@example.com",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert "Nama" in resp.json()["name"]

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_get_profile_gagal_tanpa_token(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengakses GET /api/auth/me tanpa header Authorization
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.get("/api/auth/me")
        assert resp.status_code == 401

    async def test_get_profile_gagal_token_tidak_valid(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengakses GET /api/auth/me dengan token acak yang tidak valid
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer token.tidak.valid.xyz"},
        )
        assert resp.status_code == 401


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 5 : LOGOUT
# ════════════════════════════════════════════════════════════════════════════
class TestLogout:
    """Pengujian operasi logout pengguna."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_logout_berhasil_dengan_token_valid(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Logout dengan token yang valid
        Expected : HTTP 200, pesan konfirmasi logout berhasil
        """
        resp = await client.post("/api/auth/logout", headers=auth_headers)
        assert resp.status_code == 200
        assert "detail" in resp.json()

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_logout_gagal_tanpa_token(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Logout tanpa menyertakan token Authorization
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.post("/api/auth/logout")
        assert resp.status_code == 401
