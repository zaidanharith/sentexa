import pytest
from unittest.mock import patch
from httpx import AsyncClient
from app.models.report_feedback_alert import Report  # Mendaftarkan tabel reports ke Base.metadata

MOCK_SINGLE = {
    "label": "positive",
    "label_id": 2,
    "score": 0.95,
    "scores": {"negative": 0.02, "neutral": 0.03, "positive": 0.95},
}


class TestReports:
    """Pengujian operasi CRUD Laporan (Reports)"""

    async def test_generate_report_tanpa_analisis_gagal(
        self, client: AsyncClient, premium_headers: dict
    ):
        """
        Kondisi  : Premium user, tidak ada data analisis
        Aksi     : Mencoba generate laporan dengan date range
        Expected : HTTP 201 (draft berhasil dibuat), tetapi status background akan menjadi failed karena tidak ada data analisis
        """
        resp = await client.post(
            "/api/reports/generate",
            json={
                "title": "Laporan Test 1",
                "description": "Deskripsi Test",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
                "format": "pdf",
            },
            headers=premium_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["report"]["title"] == "Laporan Test 1"
        assert data["report"]["status"] == "draft"

    async def test_crud_laporan_lengkap(
        self, client: AsyncClient, premium_headers: dict
    ):
        """
        Kondisi  : User premium, memiliki setidaknya satu analisis history
        Aksi     : 1. Buat analisis baru (untuk mengisi history)
                   2. Buat laporan baru (generate)
                   3. Ambil daftar laporan (list)
                   4. Edit laporan (PATCH)
                   5. Hapus laporan (DELETE)
        Expected : Seluruh alur CRUD berhasil dengan status code yang sesuai
        """
        # 1. Buat analisis baru agar history tidak kosong dengan memotong pemanggilan ML (mock)
        with patch("app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE):
            analisis_resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "sangat bagus sekali", "include_scores": True},
                headers=premium_headers,
            )
        assert analisis_resp.status_code == 200

        # 2. Buat Laporan Baru
        create_resp = await client.post(
            "/api/reports/generate",
            json={
                "title": "Laporan Kinerja Bulanan",
                "description": "Laporan analisis sentimen",
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-12-31T23:59:59Z",
                "format": "pdf",
            },
            headers=premium_headers,
        )
        assert create_resp.status_code == 201
        report = create_resp.json()["report"]
        report_id = report["id"]
        assert report["title"] == "Laporan Kinerja Bulanan"

        # 3. Get list reports
        list_resp = await client.get("/api/reports", headers=premium_headers)
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["count"] >= 1
        assert any(item["id"] == report_id for item in list_data["items"])

        # 4. Get detail report
        detail_resp = await client.get(
            f"/api/reports/{report_id}", headers=premium_headers
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["report"]["title"] == "Laporan Kinerja Bulanan"

        # 5. Patch/Update Laporan
        patch_resp = await client.patch(
            f"/api/reports/{report_id}",
            json={
                "title": "Laporan Kinerja Diperbarui",
                "description": "Deskripsi Baru",
            },
            headers=premium_headers,
        )
        assert patch_resp.status_code == 200
        updated_report = patch_resp.json()["report"]
        assert updated_report["title"] == "Laporan Kinerja Diperbarui"
        assert updated_report["description"] == "Deskripsi Baru"

        # 6. Delete Laporan
        delete_resp = await client.delete(
            f"/api/reports/{report_id}", headers=premium_headers
        )
        assert delete_resp.status_code == 204

        # 7. Get detail report lagi (harusnya 404)
        get_again_resp = await client.get(
            f"/api/reports/{report_id}", headers=premium_headers
        )
        assert get_again_resp.status_code == 404

    async def test_non_premium_user_akses_laporan_gagal(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : User non-premium (free plan)
        Aksi     : Mencoba mengakses list laporan
        Expected : HTTP 403 Forbidden
        """
        resp = await client.get("/api/reports", headers=auth_headers)
        assert resp.status_code in (403, 400)
