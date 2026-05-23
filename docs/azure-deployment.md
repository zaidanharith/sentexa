# 🚀 Panduan Deploy Sentexa Backend ke Azure

Dokumen ini berisi panduan lengkap untuk melakukan deploy FastAPI backend (termasuk komponen machine learning IndoBERT) ke **Azure Container Apps (ACA)** secara aman dan dioptimalkan untuk produksi.

Terdapat **2 metode** deployment yang didukung:
1. **Local Deployment**: Menggunakan PowerShell Script langsung dari komputer lokal Anda.
2. **CI/CD Pipeline (GitHub Actions)**: Otomatis melakukan deployment setiap kali Anda melakukan push ke branch `master`.

---

## 🛠️ Persiapan Sebelum Deploy

Sebelum memulai, pastikan tools berikut sudah terinstal di komputer Anda:
- **Azure CLI**: [Unduh dan Instal](https://aka.ms/installazurecliwindows)
- **Docker Desktop**: [Unduh dan Instal](https://www.docker.com/products/docker-desktop/) (pastikan engine Docker sudah berjalan)
- **Python 3.11** (untuk mendownload model jika menggunakan local baking)

---

## 🔒 Keamanan File & Rahasia (.env)

> [!WARNING]
> Jangan pernah memasukkan file `.env` ke Git! File ini sudah otomatis dimasukkan ke `.gitignore`. 
> Rahasia/secrets akan disuntikkan secara aman langsung ke **Azure Container Apps Secrets** pada saat proses deployment berlangsung.

Pastikan file `backend/.env` Anda berisi rahasia produksi yang valid sebelum melanjutkan:
```env
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://... (URL Database Anda)
SECRET_KEY=1fb96ce1411c525e71e000631442c92947d2f65cf91b9062ce149094184a6082
KAGGLE_USERNAME=zaidanharith
KAGGLE_KEY=...
HF_TOKEN=...
HF_MODEL=zaidanharith/sentexa-indobert
```

---

## 🏎️ Optimasi Machine Learning (Baking Model)

Model IndoBERT memiliki ukuran sekitar **450MB**. Di lingkungan serverless seperti Azure Container Apps, mendownload model pada setiap startup dapat menyebabkan keterlambatan respon pertama (cold start) dan bahkan memicu kegagalan startup probe dari Azure.

Kami menyediakan **fitur Model Baking**:
- Proses ini mendownload model pada saat image Docker di-build.
- Image Docker akan sedikit lebih besar, tetapi kontainer akan **langsung aktif seketika** (0 cold start delay) dan bebas dari ketergantungan API Hugging Face di runtime.
- **Sangat Direkomendasikan untuk Produksi!**

---

## 🖥️ Metode 1: Local Deployment via PowerShell (Windows)

Metode ini sangat cocok untuk melakukan setup awal infrastruktur Azure secara otomatis serta melakukan deploy dari komputer Anda.

1. Buka PowerShell dan arahkan ke direktori backend:
   ```powershell
   cd d:\CODING\JS\sentexa\backend
   ```
2. Jalankan skrip deployment:
   ```powershell
   .\deploy-azure.ps1
   ```
3. Skrip akan otomatis melakukan:
   - Cek instalasi Azure CLI dan status login Anda.
   - Membaca rahasia dari `.env` lokal secara aman.
   - Menanyakan apakah Anda ingin mengaktifkan **ML Model Baking**.
   - Membuat Resource Group di Azure (`rg-sentexa-prod`).
   - Menerapkan infrastruktur otomatis menggunakan template Bicep (`deploy.bicep`).
   - Membangun image Docker (dengan optimasi ML jika dipilih).
   - Melakukan login dan push image ke **Azure Container Registry (ACR)**.
   - Menyuntikkan rahasia ke **Azure Container Apps** dan mengaktifkan revisi terbaru.
   - Menampilkan URL API Backend yang aktif!

---

## 🔄 Metode 2: CI/CD Automatis via GitHub Actions

Untuk mengaktifkan deployment otomatis pada setiap push ke branch `master`, ikuti langkah berikut:

### 1. Buat Service Principal di Azure
Jalankan perintah ini di terminal Anda untuk membuat kredensial akses untuk GitHub Actions:
```bash
az ad sp create-for-rbac --name "github-sentexa-deployer" --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-sentexa-prod \
  --sdk-auth
```
*(Ganti `<SUBSCRIPTION_ID>` dengan ID Subscription Azure Anda).*

Salin seluruh output JSON yang dihasilkan.

### 2. Konfigurasi GitHub Repository Secrets
Buka halaman repository GitHub Anda, masuk ke **Settings > Secrets and variables > Actions**, lalu tambahkan rahasia berikut:

| Nama Secret | Deskripsi / Nilai |
| :--- | :--- |
| `AZURE_CREDENTIALS` | Tempelkan seluruh output JSON Service Principal dari langkah 1 |
| `DATABASE_URL` | URL Database PostgreSQL produksi (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | JWT Secret Key yang aman untuk autentikasi |
| `KAGGLE_USERNAME` | Username Kaggle Anda |
| `KAGGLE_KEY` | API Key Kaggle Anda |
| `HF_TOKEN` | Token Hugging Face Anda (diperlukan untuk download model private) |
| `HF_MODEL` | `zaidanharith/sentexa-indobert` |

### 3. Jalankan Workflow
Setiap push ke branch `master` yang menyentuh direktori `backend/` akan otomatis memicu workflow `.github/workflows/deploy-azure.yml`. Workflow ini akan:
- Melakukan verifikasi sintaks Python dan kelengkapan dependensi.
- Membuat infrastruktur Azure yang dideklarasikan di `deploy.bicep`.
- Melakukan build Docker dengan ML Model Baking secara otomatis.
- Melakukan push ke ACR dan update revisi Azure Container App.

---

## 📊 Detail Infrastruktur yang Dibuat (Bicep)

Template `deploy.bicep` akan membuat sumber daya Azure dengan spesifikasi berikut:
- **Azure Container Registry (ACR)**: Menyimpan Image Docker dengan aman secara privat.
- **Log Analytics Workspace**: Mengumpulkan log kontainer FastAPI untuk monitoring performa.
- **Azure Container Apps Environment**: Menyediakan kluster serverless hosting terisolasi.
- **Azure Container App (FastAPI Backend)**:
  - **Spesifikasi CPU**: 1.0 Core & **Memory**: 2.0Gi (Dioptimalkan untuk inferensi model AI/ML ringan).
  - **Auto Scaling**: Skala dari 0 hingga 5 replika berdasarkan trafik HTTP (menghemat biaya saat tidak ada aktivitas).
  - **Secure Ingress**: Terbuka ke publik melalui HTTPS (port 443) yang otomatis diarahkan ke port kontainer `8000`.
  - **Health Probes**: Liveness probe (`/api/health`) dan Readiness probe (`/api/ready`) terintegrasi untuk menjamin zero downtime.

---

## 🧪 Verifikasi Deployment & Kesehatan Aplikasi

Setelah proses deployment berhasil, Anda dapat menguji kesehatan API backend menggunakan endpoint publik:

1. **Liveness Check**:
   ```bash
   curl https://<your-app-domain>.azurecontainerapps.io/api/health
   # Diharapkan mengembalikan: {"status": "ok"}
   ```
2. **Readiness Check**:
   ```bash
   curl https://<your-app-domain>.azurecontainerapps.io/api/ready
   # Diharapkan mengembalikan: {"status": "ready"}
   ```
3. **Database Migration Status**:
   Saat startup, kontainer akan otomatis menjalankan perintah `alembic upgrade head` untuk menerapkan migrasi skema database terbaru secara otomatis.
