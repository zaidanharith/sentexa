"""
## BUNDLE PENGUJIAN 9 : RIWAYAT ANALISIS
Menguji operasi melihat dan menavigasi riwayat analisis pengguna:
  - List Riwayat Analisis  (GET /analyses)
  - Ringkasan Riwayat      (GET /analyses/summary)
  - Tren Riwayat           (GET /analyses/trend)
  - Detail Riwayat         (GET /analyses/{id})
"""

from httpx import AsyncClient


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 9 : ANALYSES HISTORY
# ════════════════════════════════════════════════════════════════════════════
class TestAnalysesHistory:
    """Pengujian operasi riwayat analisis sentimen pengguna."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_list_riwayat_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil daftar riwayat analisis (mungkin kosong)
        Expected : HTTP 200, respons memiliki struktur items, count, offset, limit
        """
        resp = await client.get("/api/analyses", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "count" in data
        assert "offset" in data
        assert "limit" in data

    async def test_list_riwayat_dengan_pagination(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil riwayat dengan parameter limit=5 dan offset=0
        Expected : HTTP 200, maksimal 5 item dikembalikan
        """
        resp = await client.get(
            "/api/analyses?limit=5&offset=0", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 5

    async def test_ringkasan_riwayat_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil ringkasan statistik riwayat analisis
        Expected : HTTP 200, memiliki total_analyses dan sentiment_counts
        """
        resp = await client.get("/api/analyses/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_analyses" in data
        assert "sentiment_counts" in data

    async def test_tren_riwayat_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil data tren riwayat 30 hari terakhir
        Expected : HTTP 200, respons memiliki list items tren
        """
        resp = await client.get(
            "/api/analyses/trend?days=30", headers=auth_headers
        )
        assert resp.status_code == 200
        assert "items" in resp.json()

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_list_riwayat_gagal_tanpa_token(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengakses riwayat analisis tanpa token autentikasi
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.get("/api/analyses")
        assert resp.status_code == 401

    async def test_detail_riwayat_tidak_ditemukan(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Negative
        Aksi     : Mengambil detail riwayat dengan ID yang tidak ada (888888)
        Expected : HTTP 404 Not Found
        """
        resp = await client.get("/api/analyses/888888", headers=auth_headers)
        assert resp.status_code == 404

    async def test_list_riwayat_filter_source_type(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Filter riwayat berdasarkan source_type='text'
        Expected : HTTP 200, hanya item dengan source_type='text'
        """
        resp = await client.get(
            "/api/analyses?source_type=text", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        for item in data["items"]:
            assert item.get("source_type") == "text"
