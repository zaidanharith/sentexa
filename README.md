# Sentexa

Sentexa adalah platform analisis sentimen ulasan pelanggan berbasis NLP (Natural Language Processing) yang membantu mengklasifikasikan teks ulasan produk ke dalam kategori positif, negatif, atau netral secara otomatis.

---

## About Project

Sentexa adalah platform analisis sentimen modern yang dirancang untuk membantu pelaku usaha dan UMKM mengelola serta memahami feedback pelanggan secara lebih cepat, terstruktur, dan objektif. Sistem ini memadukan pengolahan data berkas ulasan massal, analisis bahasa berbasis model AI, visualisasi statistik kepuasan, serta ekspor laporan analisis dalam satu ekosistem yang terpusat.

Masalah utama yang ingin diselesaikan adalah proses evaluasi ulasan konsumen yang masih manual, memakan banyak waktu, dan sulit diskalakan ketika volume transaksi meningkat. Sentexa dibuat untuk mengurangi beban operasional pemilik toko, meningkatkan kecepatan identifikasi keluhan pembeli, serta mendukung pengambilan keputusan bisnis yang tepat sasaran melalui otomatisasi pemrosesan ulasan.

Fokus utama sistem ini adalah membangun dashboard analitis yang mampu memproses ulasan (baik input teks manual maupun berkas CSV/Excel dari seller center e-commerce), membersihkan data teks tidak baku khas Indonesia, memprediksi label sentimen menggunakan model NLP, dan menyajikan visualisasi data yang mudah dipahami. Dengan pendekatan ini, pemilik usaha dapat langsung mengetahui aspek layanan yang perlu dievaluasi tanpa harus membaca ribuan ulasan satu per satu.

---

## Background

Di era digital saat ini, ulasan konsumen online telah menjadi salah satu faktor penentu utama dalam transaksi bisnis. Pengembangan Sentexa didasarkan pada temuan empiris berikut:

- Penelitian dari IJCSRR (2025) menunjukkan bahwa 93% konsumen membaca dan mempertimbangkan ulasan online sebelum membuat keputusan pembelian.
- Sebanyak 80% hingga 85% konsumen menyatakan pernah membatalkan atau mengubah keputusan pembelian mereka akibat adanya ulasan negatif.
- Volume ulasan yang masuk di platform e-commerce sangat besar, membuat pemantauan ulasan secara manual menjadi tidak efisien secara waktu dan tenaga.
- Ulasan pelanggan di Indonesia sering kali menggunakan bahasa tidak baku, singkatan, dan slang lokal yang menyulitkan proses identifikasi keluhan secara otomatis oleh model bahasa umum.

---

## Project Goals

Tujuan utama Sentexa adalah membangun sistem analisis sentimen ulasan pelanggan yang akurat, cepat, dan mudah digunakan. Sasaran utamanya meliputi:

- Klasifikasi sentimen ulasan pelanggan (positif, netral, negatif) secara otomatis menggunakan model NLP.
- Penyajian visualisasi data statistik berupa grafik tren dan awan kata (word cloud) untuk mempermudah evaluasi performa toko.
- Peningkatan efisiensi waktu operasional bagi pemilik usaha dalam mendeteksi dan mengelompokkan feedback keluhan konsumen.
- Penyediaan fitur pembuatan laporan analisis ulasan yang terstruktur dalam format dokumen CSV dan PDF untuk mendukung pengambilan keputusan bisnis.

---

## Main Features

### User Features

- Sentiment Dashboard: menampilkan statistik ringkasan sentimen, total ulasan, dan rata-rata skor kepuasan pelanggan dalam satu tampilan.
- Time-Series Trend Chart: menyajikan visualisasi grafik garis untuk memantau perkembangan tren sentimen ulasan dari waktu ke waktu.
- Keyword Word Cloud: mengekstrak dan menampilkan kata kunci yang paling sering muncul dalam ulasan negatif maupun positif untuk mendeteksi poin keluhan utama pelanggan.
- Manual Data Ingestion: menyediakan kolom input teks langsung untuk analisis sentimen instan.
- Multi-Format File Ingestion: mendukung pengunggahan berkas ulasan massal berformat CSV atau Excel hasil unduhan dari seller center e-commerce.
- Interactive Filter Table: menampilkan tabel daftar ulasan yang dilengkapi dengan label prediksi, skor kepercayaan model AI, serta filter cepat ulasan negatif.
- Exportable Report: memungkinkan pengguna mengunduh hasil analisis ulasan ke dalam dokumen CSV dan PDF (Premium).
- Subscription Plan: mengelola status akun dan kuota analisis harian pengguna (Free vs Premium).
- Authentication & Profile: mengamankan akses data ulasan pengguna menggunakan login akun reguler serta Google OAuth 2.0.

---

## AI Implementation

Sentexa menggunakan model bahasa IndoBERT sebagai inti pemrosesan cerdas untuk melakukan klasifikasi sentimen ulasan dalam Bahasa Indonesia. Sistem ini mengintegrasikan pipeline preprocessing teks untuk memastikan akurasi prediksi yang tinggi terhadap teks tidak baku.

- Model IndoBERT: menggunakan model fine-tuned IndoBERT (zaidanharith/sentexa-indobert) yang dilatih khusus untuk klasifikasi sentimen 3 kelas (positif, netral, negatif).
- Text Preprocessing: melakukan pembersihan teks dari tautan, angka, karakter khusus, dan emoji.
- Slang Normalization: mengubah bahasa tidak baku, singkatan, dan kata gaul khas Indonesia menjadi kata baku (misalnya "bgt" menjadi "banget").
- Stopwords Removal: membuang kata-kata umum yang tidak membawa makna sentimen berarti.
- Tokenization: memproses teks hasil pembersihan menjadi token representasi data menggunakan AutoTokenizer.
- Model Inference: menjalankan komputasi model sequence classification di sisi server backend secara asinkron untuk menghasilkan skor logits dan probabilitas sentimen menggunakan fungsi Softmax.

---

## Software Architecture

Arsitektur Sentexa dibangun dengan memisahkan tanggung jawab secara jelas antara frontend, backend, database, dan model hosting.

### Frontend

- Next.js: framework utama untuk aplikasi web berbasis React.
- React: membangun antarmuka pengguna yang interaktif dan modular.
- TypeScript: menjaga konsistensi tipe data dan mencegah bug runtime di frontend.
- Tailwind CSS: mendesain tata letak antarmuka yang modern, bersih, dan responsif.
- xlsx: melakukan pemrosesan dan validasi file ulasan CSV/Excel langsung di sisi klien.

### Backend

- FastAPI: menyediakan REST API asinkron berkinerja tinggi berbasis Python.
- SQLAlchemy: mengelola transaksi database PostgreSQL secara asinkron (AsyncSession).
- Lifespan Startup Event: memuat model AI IndoBERT sekali ke memori saat server backend dijalankan untuk mempercepat inferensi.
- CORS Middleware: mengamankan endpoint API dengan membatasi request hanya dari origin tepercaya (Vercel dan Localhost).

### Database

- Supabase PostgreSQL: menyimpan data akun pengguna, profil langganan, riwayat ulasan, dan data job analisis batch.

---

## Cloud Infrastructure

| Service | Function |
| --- | --- |
| Azure Container Apps | Meng-host kontainer Docker API backend FastAPI secara serverless dengan skala otomatis (1-3 replika). |
| Vercel | Menyebarkan dan meng-host frontend web Next.js secara global menggunakan Edge Network. |
| Supabase Cloud | Menyediakan database PostgreSQL terkelola yang dihubungkan menggunakan PgBouncer (Port 6543) untuk pooling koneksi. |
| Hugging Face Hub | Repositori cloud untuk menyimpan checkpoint model AI IndoBERT yang diunduh secara dinamis saat startup backend. |
| Azure Log Analytics | Mengumpulkan log kontainer backend untuk monitoring performa sistem secara terpadu. |

---

## End-to-End Workflow

1. Pengguna masuk ke aplikasi menggunakan Google OAuth 2.0.
2. Pengguna mengunggah berkas CSV/Excel ulasan atau mengetik teks ulasan secara manual.
3. Frontend Next.js memvalidasi kolom berkas (ID, Ulasan, Rating).
4. Data dikirim ke API backend FastAPI dalam payload JSON.
5. Backend membersihkan teks ulasan (cleaning, normalisasi slang, stopword).
6. Model IndoBERT menganalisis sentimen teks (positif, netral, negatif).
7. Data ulasan beserta hasil analisis disimpan ke database Supabase PostgreSQL.
8. Dashboard memperbarui visualisasi grafik tren, statistik, dan kata kunci terpopuler.
9. Pengguna mengunduh laporan analisis (CSV/PDF).

---

## Tech Stack

### Frontend

- Next.js (App Router)
- React
- TypeScript
- Tailwind CSS
- xlsx (Excel/CSV Parser)

### Backend

- FastAPI
- Python
- SQLAlchemy (Async ORM)
- Uvicorn (ASGI Server)

### AI

- IndoBERT (zaidanharith/sentexa-indobert)
- PyTorch
- Hugging Face Transformers
- Regex & Preprocessing Pipeline

### Database

- Supabase PostgreSQL
- PgBouncer Connection Pooler

### Cloud & DevOps

- Azure Container Apps
- Vercel
- Hugging Face Hub
- Azure Container Registry (ACR)
- GitHub (Version Control)

---

## Deployment

- Production URL: https://sentexa.vercel.app
- GitHub Repository: https://github.com/zaidanharith/sentexa

---

## Team Members

| Name | NIM | Role |
| --- | --- | --- |
| Zaidan Harith | 23/512629/TK/56334 | Project Manager, AI Engineer |
| Anggita Salsabilla | 23/516001/TK/56775 | UI/UX Designer, Frontend Developer |
| Dzulfikar Rizqi Ramadhani | 23/522193/TK/57616 | Software Engineer, Cloud Engineer |

---

## Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/zaidanharith/sentexa.git
cd sentexa
```

### 2. Setup Environment Variables

Buat berkas `.env` di folder `/backend` dan `.env.local` di folder `/frontend` dengan menyesuaikan konfigurasi variabel dari berkas template `.env.example` yang tersedia di masing-masing folder.

### 3. Run Backend (Docker Compose)

Pastikan Docker telah berjalan di laptop Anda, kemudian jalankan perintah berikut dari root project:

```bash
docker compose up --build
```

API Backend akan berjalan di alamat `http://localhost:8000`.

### 4. Run Frontend

Buka terminal baru, masuk ke folder frontend, lakukan instalasi dependencies, dan jalankan server pengembangan Next.js:

```bash
cd frontend
npm install
npm run dev
```

Aplikasi Frontend dapat diakses di alamat `http://localhost:3000`.

---

## Project Structure

```text
sentexa/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── types/
│   │   └── hooks/
│   ├── package.json
│   └── tsconfig.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── ml/
│   │   ├── model/
│   │   ├── inference/
│   │   └── preprocessing/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements/
├── docker-compose.yml
└── README.md
```

---

## Authentication & Security

Sentexa menerapkan beberapa lapisan keamanan untuk melindungi akses data ulasan pengguna:

- Supabase Auth & Google OAuth 2.0: menyediakan akses login terproteksi yang aman.
- Stateless JWT Authorization: memvalidasi request API backend menggunakan token JWT yang dikirim lewat HTTP Authorization Header (`Bearer Token`).
- CORS Configuration: membatasi asal request API backend agar hanya menerima request dari asal domain yang sah (Vercel dan Localhost).
- Database Connection Security: menghubungkan backend ke Supabase secara aman melalui PgBouncer untuk mencegah kelebihan beban koneksi database.
- Input File Validation: melakukan validasi ketat terhadap ukuran file, tipe ekstensi file (hanya CSV, XLS, XLSX), dan validitas struktur header kolom di sisi frontend sebelum dikirim ke server.
