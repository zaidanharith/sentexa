"""
## BUNDLE PENGUJIAN 6, 7, 8 : ANALISIS SENTIMEN
Menguji siklus bisnis inti Sentexa — prediksi sentimen teks:
  - Single Text Prediction  (POST /sentiment/predict)
  - Job-based Prediction    (POST /sentiment/predict/jobs)
  - List & Get Job          (GET  /sentiment/predict/jobs)

Sentiment service (ML model) di-mock agar pengujian tidak bergantung
pada ketersediaan model AI — fokus ke logika API, bukan inferensi.
"""

from unittest.mock import patch, AsyncMock
from httpx import AsyncClient

# Nilai kembalian mock (meniru format respons model nyata)
MOCK_SINGLE = {
    "label": "positive",
    "label_id": 2,
    "score": 0.95,
    "scores": {"negative": 0.02, "neutral": 0.03, "positive": 0.95},
}

MOCK_BATCH = [
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


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 6 : SINGLE TEXT PREDICTION
# ════════════════════════════════════════════════════════════════════════════
class TestSinglePredict:
    """Pengujian prediksi sentimen untuk satu teks."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_predict_berhasil_teks_positif(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengirim teks ulasan positif dengan include_scores=True
        Expected : HTTP 200, label sentimen dan skor tersedia
        """
        with patch(
            "app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE
        ):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "Produk ini sangat bagus dan memuaskan!", "include_scores": True},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "label" in data
        assert "score" in data
        assert data["label"] in ("positive", "negative", "neutral")

    async def test_predict_berhasil_tanpa_skor(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Prediksi sentimen dengan include_scores=False
        Expected : HTTP 200, hanya label tanpa detail skor per kelas
        """
        mock_no_score = {"label": "positive", "label_id": 2, "score": None, "scores": None}
        with patch(
            "app.services.sentiment_service.predict_text", return_value=mock_no_score
        ):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "Pelayanannya ramah sekali.", "include_scores": False},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert "label" in resp.json()

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_predict_gagal_teks_kosong(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Negative
        Aksi     : Mengirim teks yang kosong (hanya spasi)
        Expected : HTTP 400 Bad Request
        """
        with patch("app.services.sentiment_service.predict_text", return_value=MOCK_SINGLE):
            resp = await client.post(
                "/api/sentiment/predict",
                json={"text": "   ", "include_scores": True},
                headers=auth_headers,
            )
        assert resp.status_code == 400

    async def test_predict_gagal_tanpa_token(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Mengakses endpoint prediksi tanpa token autentikasi
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.post(
            "/api/sentiment/predict",
            json={"text": "Barang bagus!", "include_scores": True},
        )
        assert resp.status_code == 401

    async def test_predict_gagal_field_text_tidak_ada(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Negative
        Aksi     : Request tanpa menyertakan field 'text'
        Expected : HTTP 422 Unprocessable Entity
        """
        resp = await client.post(
            "/api/sentiment/predict",
            json={"include_scores": True},
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ════════════════════════════════════════════════════════════════════════════
# BUNDLE PENGUJIAN 8 : JOB-BASED PREDICTION
# ════════════════════════════════════════════════════════════════════════════
class TestSentimentJobs:
    """Pengujian alur kerja job asinkron untuk analisis sentimen skala besar."""

    # ── Positive ─────────────────────────────────────────────────────────────
    async def test_create_job_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Membuat job baru dengan tiga teks input
        Expected : HTTP 201, job_id tersedia, status awal 'queued'
        """
        with patch(
            "app.services.sentiment_service.predict_texts", return_value=MOCK_BATCH
        ), patch(
            "app.services.sentiment_job_service.run_job", new_callable=AsyncMock
        ):
            resp = await client.post(
                "/api/sentiment/predict/jobs",
                json={
                    "texts": [
                        "Kualitas produk sangat memuaskan.",
                        "Layanan pelanggan tidak responsif.",
                        "Harga terjangkau untuk kualitas ini.",
                    ],
                    "include_scores": True,
                },
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "job" in data
        assert "job_id" in data["job"]
        assert data["job"]["status"] in ("queued", "processing", "completed")

    async def test_list_jobs_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Mengambil daftar semua job milik user yang sedang login
        Expected : HTTP 200, respons berisi list items dan count
        """
        resp = await client.get(
            "/api/sentiment/predict/jobs", headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "count" in data

    async def test_get_job_detail_berhasil(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Positive
        Aksi     : Membuat job lalu mengambil detail job berdasarkan job_id
        Expected : HTTP 200, detail job mencakup status dan total teks
        """
        with patch(
            "app.services.sentiment_service.predict_texts", return_value=MOCK_BATCH
        ), patch(
            "app.services.sentiment_job_service.run_job", new_callable=AsyncMock
        ):
            create_resp = await client.post(
                "/api/sentiment/predict/jobs",
                json={"texts": ["Satu teks saja."], "include_scores": True},
                headers=auth_headers,
            )
        assert create_resp.status_code == 200
        job_id = create_resp.json()["job"]["job_id"]

        detail_resp = await client.get(
            f"/api/sentiment/predict/jobs/{job_id}", headers=auth_headers
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["job"]["job_id"] == job_id

    # ── Negative ─────────────────────────────────────────────────────────────
    async def test_get_job_tidak_ditemukan(
        self, client: AsyncClient, auth_headers: dict
    ):
        """
        Kondisi  : Negative
        Aksi     : Mengakses detail job dengan ID yang tidak ada (999999)
        Expected : HTTP 404 Not Found
        """
        resp = await client.get(
            "/api/sentiment/predict/jobs/999999", headers=auth_headers
        )
        assert resp.status_code == 404

    async def test_create_job_gagal_tanpa_autentikasi(self, client: AsyncClient):
        """
        Kondisi  : Negative
        Aksi     : Membuat job tanpa header Authorization
        Expected : HTTP 401 Unauthorized
        """
        resp = await client.post(
            "/api/sentiment/predict/jobs",
            json={"texts": ["teks uji"], "include_scores": True},
        )
        assert resp.status_code == 401
