# 🎯 **Sentexa** by Senpruyyy

Sentexa adalah aplikasi berbasis web untuk melakukan analisis sentimen berbasis **Natural Language Processing (NLP)** yang dirancang untuk mengklasifikasikan teks ke dalam kategori **positif, negatif, atau netral**. Aplikasi ini dikembangkan sebagai bagian dari Senior Project dan menghadirkan proses preprocessing, pemodelan AI, serta visualisasi hasil analisis melalui antarmuka web yang interaktif dan mudah digunakan.

## ✨ Fitur Utama

- 🤖 Analisis sentimen real-time dengan AI
- 📊 Visualisasi data interaktif
- 🎨 UI/UX yang user-friendly
- ⚡ Performa optimal dengan teknologi cloud
- 🔄 Preprocessing teks otomatis

## ⚙️ Cara Menjalankan Program

1. Pastikan file `.env` sudah ada di folder `/backend` dan file `.env.local` sudah ada di folder `/frontend`. Jika belum, silakan buat dengan _template_ di `.env.example` di setiap foldernya.

2. _Clone_ Repository GitHub ini.

   ```bash
   git clone https://github.com/zaidanharith/sentexa.git
   cd sentexa
   ```

3. Jalankan _command prompt_ berikut di folder root (`/sentexa`).

   ```bash
   docker compose -f backend/deployments/docker/docker-compose.yml up -d --build
   cd frontend
   npm install
   npm run dev
   ```

4. Akses aplikasi:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

## 📋 Daftar API Endpoints

Untuk melihat dokumentasi lengkap API endpoints, silakan akses [di sini](./backend/README.md).

## 👨‍💻 Developer Tergacor Sedunia

Tak kenal maka tak kenalin. Yuk kenalan sama yang buat program gacor ini dulu ga sih🤗

| Nama                      | NIM                | Peran                             |
| ------------------------- | ------------------ | --------------------------------- |
| Zaidan Harith             | 23/512629/TK/56334 | Project Manager, AI Engineer      |
| Anggita Salsabilla        | 23/516001/TK/56775 | UI/UX Designer                    |
| Dzulfikar Rizqi Ramadhani | 23/522193/TK/57616 | Software Engineer, Cloud Engineer |
