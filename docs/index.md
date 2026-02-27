# **Sentexa** by Senpruyyy

## Informasi Kelompok

- **Nama Kelompok:** Senpruyyy
- **Anggota dan NIM:**
  1. Zaidan Harith - 23/512629/TK/56334 (Project Manager, AI Engineer)
  2. Anggita Salsabilla - 23/516001/TK/56775 (UI/UX Designer)
  3. Dzulfikar Rizqi Ramadhani - 23/522193/TK/57616 (Software Engineer, Cloud Engineer)

- **Project:** Project Senior Project TI
- **Instansi:** Departemen Teknologi Elektro dan Teknologi Informasi, Fakultas Teknik, Universitas Gadjah Mada

## Jawaban Modul 1

- **Nama Produk:** Sentexa
- **Jenis Produk:** Platform analisis sentimen berbasis web menggunakan Natural Language Processing (NLP).

### Latar Belakang & Permasalahan

**Latar Belakang:**

Pelaku UMKM di marketplace sering kali kewalahan menghadapi volume ulasan pelanggan yang sangat besar. Hal ini menyebabkan:

- **Keluhan krusial terabaikan:** Komplain penting sering tertumpuk oleh ulasan singkat lainnya.
- **Analisis manual yang lambat:** Membutuhkan waktu berjam-jam untuk memetakan kepuasan pelanggan secara manual.
- **Kegagalan bisnis:** Kurangnya respon cepat terhadap layanan yang buruk berisiko membuat UMKM kehilangan pelanggan secara permanen.

**Rumusan Permasalahan:**

- Bagaimana cara mengklasifikasikan ribuan ulasan pelanggan ke dalam kategori sentimen (Positif, Negatif, Netral) secara otomatis?
- Bagaimana membangun integrasi yang aman antara sistem backend berbasis Python dengan dashboard berbasis web?
- Bagaimana memastikan sistem dapat diakses secara stabil oleh pelaku UMKM melalui infrastruktur cloud?

---

### Ide Solusi & Rancangan Fitur

Ide solusi yang diusulkan adalah membangun **Sentexa**, sebuah platform analisis sentimen berbasis web yang dirancang khusus untuk membantu pelaku UMKM mengelola volume ulasan pelanggan yang besar di marketplace secara otomatis. Sistem ini menggunakan teknologi NLP berbasis Python untuk mengklasifikasikan ulasan ke dalam kategori positif, negatif, atau netral, yang kemudian divisualisasikan melalui dashboard interaktif Next.js guna memetakan tren kepuasan pelanggan secara real-time. Seluruh infrastruktur backend dan API di-deploy menggunakan layanan cloud Azure dengan protokol HTTPS/SSL.

---

**Rancangan Fitur:**

1. **User Authentication & Profile:**
   - Secure User Login: Memberikan akses pribadi bagi pemilik UMKM untuk mengamankan data ulasan mereka menggunakan database Azure.
   - Account Management: Memungkinkan pengguna untuk mengelola profil dan melihat status langganan aktif mereka (Free/Premium).

2. **Subscription Tier (Weekly/Monthly/Annual Plan):**
   - Free Plan: Pengguna Free hanya dapat memasukkan teks secara manual (tanpa unggah CSV/Excel), dibatasi 5 pengiriman teks per hari, tidak memiliki akses ke exportable reports.
   - Premium Plan (Weekly, Monthly & Annual): Pengguna Premium dapat membuka unggahan berkas multi-format (CSV/Excel), melakukan pengiriman teks tanpa batas, dan mengakses fitur exportable reports.

3. **Instant Data Ingestion:**
   - Multi-Format Upload: Menyediakan form sederhana untuk mengunggah file ulasan berformat CSV atau Excel hasil unduhan dari seller center marketplace.
   - Manual Text Area: Kolom teks untuk copy-paste ulasan secara langsung guna analisis instan tanpa perlu mengunggah file.

4. **AI Sentiment Processor:**
   - Automated NLP Classification: Menggunakan model Natural Language Processing berbasis Python untuk mengklasifikasikan ulasan ke dalam kategori Positif, Negatif, atau Netral.
   - Local Language Optimization: Model dirancang khusus untuk memahami bahasa ulasan pembeli di Indonesia (termasuk bahasa slang atau tidak baku) agar hasil akurat.

5. **Sentiment Visualization Dashboard:**
   - Visual Distribution: Menampilkan Pie Chart atau Donut Chart untuk gambaran persentase sentimen pelanggan.
   - Time-Series Trend: Menampilkan Line Chart guna memantau apakah kualitas layanan toko membaik atau menurun dari waktu ke waktu.
   - Key Metrics: Menyediakan ringkasan statistik seperti "Total Ulasan" dan "Skor Kepuasan Rata-rata" dalam satu tampilan layar.

6. **Keyword Word Cloud:**
   - Negative Highlight: Mengekstraksi kata kunci yang paling sering muncul dalam ulasan negatif menggunakan AI.
   - Pain Point Detection: Membantu UMKM mengetahui penyebab utama komplain secara cepat, seperti kata "lambat", "sobek", atau "palsu".

7. **Smart Filter Table:**
   - Interactive Analysis: Tabel yang berisi teks asli, label sentimen, dan confidence score model AI.
   - Instant Toggle Filter: Tombol filter cepat untuk menampilkan ulasan "Negatif" saja agar bisa segera ditindaklanjuti.
   - Analysis History: Menyimpan riwayat analisis sebelumnya sehingga data tidak hilang saat browser ditutup.

8. **Exportable Report:**
   - Premium Reporting: Fitur untuk mengunduh seluruh hasil analisis dan visualisasi ke dalam format dokumen (PDF/CSV).

### Analisis Kompetitor

#### Kompetitor 1: **MonkeyLearn**

- **Jenis Kompetitor:** Direct
- **Jenis Produk:** Aplikasi web & extension
- **Target Customer:** Pengguna social media, penjual e-commerce, dll.

- **Kelebihan:**
  1. Antarmuka (UI) yang sangat intuitif dan ramah pengguna.
  2. Memungkinkan pengguna melatih model NLP sendiri melalui platform web.

- **Kekurangan:**
  1. Fitur pelatihan model via web berpotensi menjadi celah keamanan.
  2. Versi web app (app.monkeylearn.com) sering mengalami masalah akses atau sudah tidak aktif.

- **Key Competitive Advantage & Unique Value:** Sentexa unggul dalam akurasi klasifikasi ulasan karena dioptimalkan khusus untuk mendeteksi bahasa tidak baku (slang), singkatan, dan sarkasme khas pembeli marketplace Indonesia (seperti _'gercep'_, _'recom'_, _'sdh'_) yang sering kali gagal diidentifikasi secara tepat oleh model umum milik MonkeyLearn.

---

#### Kompetitor 2: **Brand24**

- **Jenis Kompetitor:** Direct
- **Jenis Produk:** Aplikasi Web
- **Target Customer:** Pengguna social media, stockholder, dll.

- **Kelebihan:**
  1. Fetch data dari seluruh caption di berbagai social media.
  2. Memiliki fitur pelacakan sebutan (mention) merek secara real-time.

- **Kekurangan:**
  1. Harga langganan mahal (berbasis dolar), kurang ramah untuk kantong UMKM.
  2. Tidak fokus pada ulasan transaksi di halaman produk marketplace lokal (Shopee/Tokopedia).

- **Key Competitive Advantage & Unique Value:** Sentexa lebih spesifik dalam menganalisis ulasan transaksi e-commerce, sedangkan Brand24 hanya memantau media sosial secara umum.

---

#### Kompetitor 3: **Sentix**

- **Jenis Kompetitor:** Direct
- **Jenis Produk:** Platform Analisis Sentimen (Web/API)
- **Target Customer:** Korporasi, analis pasar, dan institusi finansial

- **Kelebihan:**
  1. Proses klasifikasi data teks dalam volume besar sangat cepat.
  2. Memiliki fitur kustomisasi kategori sentimen untuk pengguna mahir.

- **Kekurangan:**
  1. Kurang akurat dalam mendeteksi dialek dan bahasa slang lokal Indonesia.
  2. Biaya langganan tinggi, tidak cocok untuk skala UMKM.

- **Key Competitive Advantage & Unique Value:** Sentexa unggul melalui fitur _Urgent Alert_ yang secara otomatis memprioritaskan keluhan krusial UMKM, sementara Sentix lebih bersifat umum dan tidak memiliki sistem peringatan dini untuk ulasan negatif di marketplace.
