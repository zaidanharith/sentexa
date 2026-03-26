# 🧠 Struktur NLP (Natural Language Preprocessing) Module

Folder [backend/app/nlp](backend/app/nlp) dipakai untuk seluruh lifecycle model NLP dari training sampai inference.

## 🗂️ Struktur Folder

```text
nlp/
├─ data/
│  ├─ loaders.py
│  ├─ split.py
│  └─ labelling.py
├─ preprocessing/
│  ├─ cleaning.py
│  ├─ normalization.py
│  ├─ tokenization.py
│  ├─ stemming.py
│  └─ stopwords.py
├─ features/
│  ├─ bow.py
│  ├─ tfidf.py
│  └─ embeddings.py
├─ training/
│  ├─ train_baseline.py
│  ├─ train_classifier.py
│  └─ tune.py
├─ evaluation/
│  ├─ metrics.py
│  ├─ validate.py
│  └─ reports.py
├─ inference/
│  ├─ predictor.py
│  └─ postprocess.py
└─ registry/
     ├─ model_loader.py
     └─ versioning.py
```

## 🎯 Fungsi Tiap Folder

### 📦 `/data`

- Memuat utilitas untuk load dataset mentah.
- Berisi logic split train, validation, test.
- Opsional untuk balancing data (oversampling atau undersampling).

### 🧹 `/preprocessing`

- Berisi pipeline pembersihan teks bahasa Indonesia.
- Menyamakan alur preprocessing saat training dan inference agar konsisten.

### 🧩 `/features`

- Mengubah teks hasil preprocessing menjadi fitur model.
- Menyimpan implementasi extractor seperti Bag of Words atau TF-IDF.

### 🏋️ `/training`

- Menjalankan training model dari awal.
- Menyimpan script baseline dan tuning hyperparameter.

### 📊 `/evaluation`

- Menghitung metrik performa model.
- Menyusun report hasil evaluasi untuk pemilihan model terbaik.

### 🔮 `/inference`

- Menyediakan logic prediksi untuk runtime API.
- Tidak berisi proses fit training, hanya load artifact dan predict.

### 🗃️ `/registry`

- Mengelola versi model dan artifact.
- Menentukan model aktif yang dipakai endpoint API.

## 🔄 Alur Kerja

1. `data` -> load dan split dataset.
2. `preprocessing` -> bersihkan dan normalisasi teks.
3. `features` -> ubah teks menjadi representasi numerik.
4. `training` -> latih model.
5. `evaluation` -> hitung metrik dan pilih model terbaik.
6. `registry` -> simpan model dan metadata versi.
7. `inference` -> gunakan model terdaftar untuk prediksi di API.
