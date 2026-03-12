# 📋 Daftar API Endpoints

Akses Backend dapat melalui [**http://localhost:8000**](http://localhost:8000)

🌐 : **Public Endpoint** (Endpoint yang bisa diakses tanpa login)

🔒 : **Protected Endpoint** (Endpoint yang memerlukan autentikasi)

## 0. General

- 🌐 `GET /api` : Menampilkan informasi umum dan versi API

- 🌐 `GET /api/health` : Mengecek status kesehatan (_liveness_) aplikasi

- 🌐 `GET /api/ready` : Mengecek kesiapan (_readiness_) aplikasi untuk menerima trafik

- 🌐 `GET /api/metrics` : Menampilkan metrik performa dan penggunaan aplikasi

## 1. Auth

- 🌐 `POST /api/auth/login` : Login menggunakan email dan password

- 🌐 `POST /api/auth/register` : Mendaftarkan akun pengguna baru

- 🌐 `GET /api/auth/google` : Mengarahkan pengguna ke halaman login Google (OAuth 2.0 redirect)

- 🌐 `GET /api/auth/google/callback` : Menerima callback dari Google setelah autentikasi berhasil, lalu mengembalikan token akses

- 🔒 `POST /api/auth/logout` : Menghapus sesi dan token aktif pengguna

- 🔒 `GET /api/auth/me` : Mengambil data profil dan status langganan pengguna yang sedang login

## 2. Subscription & Billing

- 🔒 `GET /api/subscription` : Mengambil status langganan aktif, sisa kuota, dan tanggal kedaluwarsa

- 🌐 `GET /api/subscription/plans` : Menampilkan daftar paket langganan yang tersedia beserta detail fitur dan harga (Free, Weekly, Monthly, Annual)

- 🔒 `POST /api/subscription/subscribe` : Mengaktifkan atau memperbarui paket langganan pengguna

## 3. File Upload

- 🔒 `POST /api/uploads` : Mengunggah file ulasan berformat CSV atau Excel untuk diproses lebih lanjut

## 4. Analysis

- 🔒 `POST /api/text/clean` : Membersihkan dan menormalisasi teks (hapus noise, slang, dll.) sebagai preview sebelum analisis

- 🔒 `POST /api/sentiment/predict` : Menganalisis sentimen satu teks secara langsung dan mengembalikan label (Positif/Negatif/Netral) beserta skor kepercayaan

- 🔒 `POST /api/sentiment/predict/batch` : Menganalisis sentimen banyak teks atau file sekaligus secara asinkron, mengembalikan `job_id` untuk dipantau

- 🔒 `GET /api/sentiment/predict/jobs` : Mengambil daftar semua job analisis batch milik pengguna beserta statusnya

- 🔒 `GET /api/sentiment/predict/jobs/{job_id}` : Mengambil status terkini dan ringkasan hasil (jumlah per label, progres) dari job tertentu

- 🔒 `GET /api/sentiment/predict/jobs/{job_id}/results` : Mengambil hasil detail per ulasan dari suatu job analisis secara terpaginasi

- 🔒 `POST /api/sentiment/predict/jobs/{job_id}/reprocess` : Memproses ulang job analisis menggunakan versi model atau konfigurasi preprocessing yang berbeda

- 🔒 `POST /api/sentiment/postprocess` : Menerapkan aturan bisnis pada hasil prediksi, seperti penyesuaian threshold atau penggabungan label

## 5. Reports

- 🔒 `GET /api/reports` : Mengambil daftar laporan yang pernah dibuat oleh pengguna

- 🔒 `POST /api/reports/generate` : Membuat laporan baru berdasarkan hasil analisis job tertentu atau rentang waktu yang dipilih

- 🔒 `GET /api/reports/{report_id}` : Mengambil metadata dan ringkasan isi laporan tertentu

- 🔒 `GET /api/reports/{report_id}/download?format=csv|pdf` : Mengunduh laporan dalam format CSV atau PDF (fitur Premium)

## 6. Dashboard

- 🔒 `GET /api/dashboard/summary?start=&end=` : Mengambil ringkasan metrik sentimen dalam rentang waktu tertentu, mencakup total ulasan, persentase tiap label, dan skor kepuasan rata-rata

- 🔒 `GET /api/dashboard/trends?start=&end=&interval=daily|weekly` : Mengambil data tren sentimen dari waktu ke waktu berdasarkan interval harian atau mingguan untuk ditampilkan sebagai _line chart_

- 🔒 `GET /api/dashboard/keywords?job_id=&top=&sentiment=negative|neutral|positive` : Mengambil kata kunci yang paling sering muncul pada label sentimen tertentu untuk ditampilkan sebagai _word cloud_

## 7. History & Feedback

- 🔒 `GET /api/analyses` : Mengambil riwayat seluruh analisis yang pernah dilakukan pengguna beserta statistik ringkasnya

- 🔒 `POST /api/feedback` : Mengirimkan koreksi label sentimen pada hasil tertentu untuk keperluan peningkatan akurasi model

- 🔒 `POST /api/alerts` : Menandai ulasan negatif krusial sebagai peringatan (_urgent alert_) yang perlu ditindaklanjuti
