# 📋 Daftar API Endpoints

Akses Backend dapat melalui [**http://localhost:8000**](http://localhost:8000)

🌐 : **Public Endpoint** (Endpoint yang bisa diakses tanpa login)

🔒 : **Protected Endpoint** (Endpoint yang memerlukan autentikasi)

## 0. General

- 🌐 `GET /api` : Menampilkan informasi umum dan versi API

  Contoh _response_:

  ```text
     {
       "message": "Welcome to the Sentexa API"
     }
  ```

- 🌐 `GET /api/health` : Mengecek status kesehatan (_liveness_) aplikasi

  Contoh _response_:

  ```text
     {
       "status": "ok"
     }
  ```

- 🌐 `GET /api/ready` : Mengecek kesiapan (_readiness_) aplikasi untuk menerima trafik

  Contoh _response_:

  ```text
     {
       "status": "ready"
     }
  ```

- 🌐 `GET /api/metrics` : Menampilkan metrik performa dan penggunaan aplikasi

  Contoh _response_:

  ```text
     # HELP sentexa_http_requests_total Total HTTP requests
     # TYPE sentexa_http_requests_total counter
     sentexa_http_requests_total{method="GET",path="/api/health"} 42
  ```

## 1. Auth

- 🌐 `POST /api/auth/login` : Login menggunakan email dan password

  Contoh _request_:

  ```text
     {
       "email": "teddy@gmail.com",
       "password": "12345678"
     }
  ```

  Contoh _response_:

  ```text
     {
       "access_token": "abcdefghijklmnopqrstuvwxyz",
       "refresh_token": "tuvwxfghijklmnopqrsfghijkl",
       "token_type": "bearer"
     }
  ```

- 🌐 `POST /api/auth/register` : Mendaftarkan akun pengguna baru

  Contoh _request_:

  ```text
     {
       "name": "Teddy",
       "email": "teddy@gmail.com",
       "password": "12345678"
     }
  ```

  Contoh _response_:

  ```text
     {
       "id": 1,
       "name": "Teddy",
       "email": "teddy@gmail.com"
     }
  ```

- 🌐 `GET /api/auth/google` : Mengarahkan pengguna ke halaman login Google (OAuth 2.0 redirect)

  Contoh _response_:

  ```text
     Redirect ke https://accounts.google.com/o/oauth2/v2/auth?...
  ```

- 🌐 `GET /api/auth/google/callback` : Menerima callback dari Google setelah autentikasi berhasil, lalu mengembalikan token akses

  Contoh _response_:

  ```text
     {
       "access_token": "abcdefghijklmnopqrstuvwxyz",
       "refresh_token": "tuvwxfghijklmnopqrsfghijkl",
       "token_type": "bearer"
     }
  ```

- 🔒 `POST /api/auth/logout` : Menghapus sesi dan token aktif pengguna

  Contoh _response_:

  ```text
     {
       "message": "Logout berhasil"
     }
  ```

- 🔒 `GET /api/auth/me` : Mengambil data profil dan status langganan pengguna yang sedang login

  Contoh _response_:

  ```text
     {
       "id": 1,
       "name": "Teddy",
       "email": "teddy@gmail.com",
       "subscription": {
         "plan": "free",
         "quota_remaining": 100,
         "expires_at": null
       }
     }
  ```

## 2. Subscription & Billing

- 🔒 `GET /api/subscription` : Mengambil status langganan aktif, sisa kuota, dan tanggal kedaluwarsa

  Contoh _response_:

  ```text
     {
       "plan": "monthly",
       "quota_remaining": 1200,
       "expires_at": "2026-06-01T00:00:00Z"
     }
  ```

- 🌐 `GET /api/subscription/plans` : Menampilkan daftar paket langganan yang tersedia beserta detail fitur dan harga (Free, Weekly, Monthly, Annual)

  Contoh _response_:

  ```text
     [
       {
         "id": "free",
         "name": "Free",
         "price": 0,
         "quota": 100
       },
       {
         "id": "monthly",
         "name": "Monthly",
         "price": 99000,
         "quota": 2000
       }
     ]
  ```

- 🔒 `POST /api/subscription/subscribe` : Mengaktifkan atau memperbarui paket langganan pengguna

  Contoh _request_:

  ```text
     {
       "plan": "monthly",
       "payment_method": "bank_transfer"
     }
  ```

  Contoh _response_:

  ```text
     {
       "status": "active",
       "plan": "monthly",
       "expires_at": "2026-06-01T00:00:00Z"
     }
  ```

## 3. File Upload

- 🔒 `POST /api/uploads` : Mengunggah file ulasan berformat CSV atau Excel untuk diproses lebih lanjut

  Contoh _request_:

  ```text
     multipart/form-data
     file=@reviews.csv
  ```

  Contoh _response_:

  ```text
     {
       "upload_id": "upl_123",
       "filename": "reviews.csv",
       "rows": 250
     }
  ```

## 4. Analysis

- 🔒 `POST /api/text/clean` : Membersihkan dan menormalisasi teks (hapus noise, slang, dll.) sebagai preview sebelum analisis

  Contoh _request_:

  ```text
     {
       "text": "Produk bgt bagusss, pengiriman lma bgt"
     }
  ```

  Contoh _response_:

  ```text
     {
       "cleaned_text": "produk banget bagus, pengiriman lama banget"
     }
  ```

- 🔒 `POST /api/sentiment/predict` : Menganalisis sentimen satu teks secara langsung dan mengembalikan label (Positif/Negatif/Netral) beserta skor kepercayaan

  Contoh _request_:

  ```text
     {
       "text": "Pengirimannya cepat dan produknya sesuai"
     }
  ```

  Contoh _response_:

  ```text
     {
       "label": "positive",
       "label_id": 2,
       "score": 0.7061385004752568,
       "scores": {
         "negative": 0.25071774770516725,
         "neutral": 0.04314375181957588,
         "positive": 0.7061385004752568
       },
       "postprocess": null
     }
  ```

- 🔒 `POST /api/sentiment/predict/batch` : Menganalisis sentimen banyak teks atau file sekaligus secara asinkron, mengembalikan `job_id` untuk dipantau

  Contoh _request_:

  ```text
     {
       "texts": [
         "Produknya bagus",
         "Pengiriman lama"
       ]
     }
  ```

  Contoh _response_:

  ```text
     {
       "items": [
         {
           "label": "positive",
           "label_id": 2,
           "score": 0.92,
           "scores": {
             "negative": 0.04,
             "neutral": 0.04,
             "positive": 0.92
           },
           "postprocess": null
         },
         {
           "label": "negative",
           "label_id": 0,
           "score": 0.81,
           "scores": {
             "negative": 0.81,
             "neutral": 0.12,
             "positive": 0.07
           },
           "postprocess": null
         }
       ],
       "count": 2
     }
  ```

- 🔒 `GET /api/sentiment/predict/jobs` : Mengambil daftar semua job analisis batch milik pengguna beserta statusnya

  Contoh _response_:

  ```text
     {
       "items": [
         {
           "job_id": "123",
           "status": "processing",
           "total": 200,
           "completed": 120,
           "created_at": "2026-05-01T09:00:00Z",
           "updated_at": "2026-05-01T09:05:00Z",
           "label_counts": null,
           "error": null
         }
       ],
       "count": 1
     }
  ```

- 🔒 `POST /api/sentiment/predict/jobs` : Membuat job analisis sentimen batch baru dengan mengupload file atau memasukkan daftar teks untuk dianalisis secara asinkron

  Contoh _request_:

  ```text
     {
       "texts": [
         "Produknya bagus",
         "Pengiriman lama"
       ],
       "include_scores": true,
       "apply_postprocess": true,
       "include_meta": false
     }
  ```

  Contoh _response_:

  ```text
     {
       "job": {
         "job_id": "124",
         "status": "queued",
         "total": 2,
         "completed": 0,
         "created_at": "2026-05-01T09:10:00Z",
         "updated_at": "2026-05-01T09:10:00Z",
         "label_counts": null,
         "error": null
       }
     }
  ```

- 🔒 `GET /api/sentiment/predict/jobs/{job_id}` : Mengambil status terkini dan ringkasan hasil (jumlah per label, progres) dari job tertentu

  Contoh _response_:

  ```text
     {
       "job": {
         "job_id": "123",
         "status": "completed",
         "total": 200,
         "completed": 200,
         "created_at": "2026-05-01T09:00:00Z",
         "updated_at": "2026-05-01T09:15:00Z",
         "label_counts": {
           "positive": 120,
           "negative": 30,
           "neutral": 50
         },
         "error": null
       }
     }
  ```

- 🔒 `GET /api/sentiment/predict/jobs/{job_id}/results` : Mengambil hasil detail per ulasan dari suatu job analisis secara terpaginasi

  Contoh _response_:

  ```text
     {
       "items": [
         {
           "index": 0,
           "text": "Produknya bagus",
           "prediction": {
             "label": "positive",
             "label_id": 2,
             "score": 0.95,
             "scores": {
               "negative": 0.02,
               "neutral": 0.03,
               "positive": 0.95
             },
             "postprocess": null
           }
         }
       ],
       "count": 1,
       "total": 200,
       "offset": 0,
       "limit": 20
     }
  ```

- 🔒 `POST /api/sentiment/predict/jobs/{job_id}/reprocess` : Memproses ulang job analisis menggunakan versi model atau konfigurasi preprocessing yang berbeda

  Contoh _request_:

  ```text
     {
       "include_scores": true,
       "apply_postprocess": true,
       "include_meta": false
     }
  ```

  Contoh _response_:

  ```text
     {
       "job": {
         "job_id": "123",
         "status": "queued",
         "total": 200,
         "completed": 0,
         "created_at": "2026-05-01T09:20:00Z",
         "updated_at": "2026-05-01T09:20:00Z",
         "label_counts": null,
         "error": null
       }
     }
  ```

- 🔒 `POST /api/sentiment/postprocess` : Menerapkan aturan bisnis pada hasil prediksi, seperti penyesuaian threshold atau penggabungan label

  Contoh _request_:

  ```text
     {
       "predictions": [
         {
           "label": "positive",
           "label_id": 2,
           "score": 0.55,
           "scores": {
             "negative": 0.2,
             "neutral": 0.25,
             "positive": 0.55
           },
           "postprocess": null
         }
       ],
       "rules": {
         "min_confidence": 0.6,
         "fallback_label": "neutral"
       },
       "include_meta": true
     }
  ```

  Contoh _response_:

  ```text
     {
       "items": [
         {
           "label": "neutral",
           "label_id": 1,
           "score": 0.55,
           "scores": {
             "negative": 0.2,
             "neutral": 0.25,
             "positive": 0.55
           },
           "postprocess": {
             "label_before": "positive",
             "label_after": "neutral",
             "threshold": 0.6
           }
         }
       ],
       "count": 1
     }
  ```

## 5. Reports

- 🔒 `GET /api/reports` : Mengambil daftar laporan yang pernah dibuat oleh pengguna

  Contoh _response_:

  ```text
     [
       {
         "report_id": "rep_001",
         "title": "Laporan Mei",
         "created_at": "2026-05-01T10:00:00Z"
       }
     ]
  ```

- 🔒 `POST /api/reports/generate` : Membuat laporan baru berdasarkan hasil analisis job tertentu atau rentang waktu yang dipilih

  Contoh _request_:

  ```text
     {
       "job_id": "job_abc123",
       "title": "Laporan Mei"
     }
  ```

  Contoh _response_:

  ```text
     {
       "report_id": "rep_001",
       "status": "processing"
     }
  ```

- 🔒 `GET /api/reports/{report_id}` : Mengambil metadata dan ringkasan isi laporan tertentu

  Contoh _response_:

  ```text
     {
       "report_id": "rep_001",
       "title": "Laporan Mei",
       "summary": {
         "positive": 120,
         "negative": 30,
         "neutral": 50
       }
     }
  ```

- 🔒 `GET /api/reports/{report_id}/download?format=csv|pdf` : Mengunduh laporan dalam format CSV atau PDF (fitur Premium)

  Contoh _response_:

  ```text
     Binary file (CSV/PDF)
  ```

## 6. Dashboard

- 🔒 `GET /api/dashboard/summary?start=&end=` : Mengambil ringkasan metrik sentimen dalam rentang waktu tertentu, mencakup total ulasan, persentase tiap label, dan skor kepuasan rata-rata

  Contoh _request_:

  ```text
     GET /api/dashboard/summary?start=2026-05-01&end=2026-05-31
  ```

  Contoh _response_:

  ```text
     {
       "total_reviews": 200,
       "positive_pct": 60,
       "negative_pct": 15,
       "neutral_pct": 25,
       "avg_score": 4.2
     }
  ```

- 🔒 `GET /api/dashboard/trends?start=&end=&interval=daily|weekly` : Mengambil data tren sentimen dari waktu ke waktu berdasarkan interval harian atau mingguan untuk ditampilkan sebagai _line chart_

  Contoh _request_:

  ```text
     GET /api/dashboard/trends?start=2026-05-01&end=2026-05-07&interval=daily
  ```

  Contoh _response_:

  ```text
     [
       { "date": "2026-05-01", "positive": 20, "negative": 5, "neutral": 10 },
       { "date": "2026-05-02", "positive": 18, "negative": 3, "neutral": 9 }
     ]
  ```

- 🔒 `GET /api/dashboard/keywords?job_id=&top=&sentiment=negative|neutral|positive` : Mengambil kata kunci yang paling sering muncul pada label sentimen tertentu untuk ditampilkan sebagai _word cloud_

  Contoh _request_:

  ```text
     GET /api/dashboard/keywords?job_id=job_abc123&top=10&sentiment=negative
  ```

  Contoh _response_:

  ```text
     [
       { "keyword": "pengiriman", "count": 12 },
       { "keyword": "lama", "count": 9 }
     ]
  ```

## 7. History & Feedback

- 🔒 `GET /api/analyses` : Mengambil riwayat seluruh analisis yang pernah dilakukan pengguna beserta statistik ringkasnya

  Contoh _response_:

  ```text
     [
       {
         "analysis_id": "an_001",
         "job_id": "job_abc123",
         "created_at": "2026-05-01T10:00:00Z",
         "total": 200
       }
     ]
  ```

  - 🔒 `GET /api/analyses/summary` : Mengambil ringkasan metrik analisis milik pengguna (total analisis, perubahan dari kemarin, dan distribusi sentimen)

    Contoh _response_:

    ```text
       {
         "total_analyses": 120,
         "delta_from_yesterday": 5,
         "sentiment_counts": {
           "positive": 68,
           "negative": 32,
           "neutral": 20
         },
         "total_sentiments": 120
       }
    ```

- 🔒 `POST /api/feedback` : Mengirimkan koreksi label sentimen pada hasil tertentu untuk keperluan peningkatan akurasi model

  Contoh _request_:

  ```text
     {
       "review_id": 123,
       "correct_label": "negative"
     }
  ```

  Contoh _response_:

  ```text
     {
       "status": "received"
     }
  ```

- 🔒 `POST /api/alerts` : Menandai ulasan negatif krusial sebagai peringatan (_urgent alert_) yang perlu ditindaklanjuti

  Contoh _request_:

  ```text
     {
       "review_id": 123,
       "reason": "Komplain serius terkait keamanan produk"
     }
  ```

  Contoh _response_:

  ```text
     {
       "alert_id": "alert_001",
       "status": "created"
     }
  ```
