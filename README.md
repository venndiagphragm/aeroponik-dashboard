# 🌿 Aeroponik Dashboard (Buku Saku Digital)

Aeroponik Dashboard adalah aplikasi berbasis web yang dirancang khusus untuk mempermudah pemantauan harian pertumbuhan tanaman bayam dengan metode aeroponik. Aplikasi ini bertindak sebagai asisten pencatatan sekaligus memberikan umpan balik (feedback) secara instan mengenai kondisi tanaman berdasarkan usia, tinggi, dan jumlah daunnya.

Proyek ini awalnya bernama "Bayamin" dan telah disesuaikan menjadi dashboard "Aeroponik" dengan identitas visual khas Universitas Airlangga (UNAIR).

## 🚀 Fitur Utama

- **Manajemen Batch Tanam**: Buat dan kelola siklus tanam (batch) dengan parameter nozzle 0.1mm dan media rockwool. Setiap batch memiliki tanggal mulai dan `hari_ke` dihitung otomatis.
- **Pencatatan Harian Interaktif**: Form pencatatan untuk tinggi (cm) dan jumlah helai daun dengan tombol (+) dan (-) yang mudah digunakan, terkait langsung ke batch yang dipilih.
- **Integrasi Kamera Langsung**: Pengguna dapat langsung mengambil foto kondisi tanaman secara *real-time* menggunakan kamera belakang ponsel mereka.
- **Sistem Penilaian Otomatis (Skor Komposit 0-100)**: Aplikasi membandingkan data input dengan *baseline* ideal dari data riset (nozzle 0.1mm + rockwool). Threshold penilaian sesuai PRD:
  - 🟢 **Optimal (≥ 80)**: Tumbuh subur, sesuai atau melebihi target.
  - 🟡 **Perhatian (50 - 79)**: Pertumbuhan di bawah target, perlu perhatian.
  - 🔴 **Kritis (< 50)**: Kondisi darurat yang membutuhkan penanganan segera.
- **Riwayat Pencatatan (Logs)**: Halaman khusus untuk melihat seluruh data historis pencatatan, dengan filter per batch, skor numerik, status warna, dan dokumentasi foto.
- **Buku Saku Digital**: Halaman panduan singkat cara penggunaan aplikasi, sistem penilaian, standar lingkungan ideal untuk tanaman (suhu & kelembapan), spesifikasi sistem, serta kontak langsung ke Pendamping Desa via WhatsApp.
- **PWA (Progressive Web App)**: Dilengkapi dengan *manifest* dan *service-worker* sehingga aplikasi dapat diakses dengan mulus di perangkat *mobile*, di-*install* ke layar utama, dan memiliki dukungan *caching*.

## 🛠️ Tech Stack

- **Backend**: Python 3, **FastAPI**, Uvicorn (ASGI server)
- **Database**: SQLite + **SQLAlchemy 2.0** (ORM)
- **Frontend / Styling**: HTML5, Vanilla JavaScript, Tailwind CSS (via CDN), Jinja2 Templates
- **PWA**: Service Worker (`service-worker.js`), Web App Manifest (`manifest.json`)
- **Penyimpanan Berkas**: Penyimpanan lokal terstruktur untuk unggahan foto dokumentasi harian (`static/uploads`).

## 📊 Data Baseline

Data baseline ideal pertumbuhan bayam diambil dari hasil riset dengan spesifikasi:
- **Nozzle**: 0.1mm
- **Media Tanam**: Rockwool
- **Periode**: Hari ke-1 sampai 29

Data pada hari ganjil (1,3,5,...,29) berasal langsung dari pengukuran paper. Hari genap diinterpolasi linear antar titik data terdekat.

## 📁 Struktur Direktori

```text
📦 project desbin
 ┣ 📂 instance
 ┃ ┗ 📜 bayamin.db          # Database SQLite utama
 ┣ 📂 static
 ┃ ┣ 📂 uploads             # Folder tempat foto tanaman disimpan
 ┃ ┣ 📜 manifest.json       # Konfigurasi PWA
 ┃ ┣ 📜 service-worker.js   # Script Service Worker untuk PWA Cache
 ┃ ┗ 📜 unair_logo.png      # Logo Universitas Airlangga
 ┣ 📂 templates
 ┃ ┣ 📜 about.html          # Halaman Buku Saku / Panduan
 ┃ ┣ 📜 base.html           # Template dasar (Navbar, Tailwind config)
 ┃ ┣ 📜 batches.html        # Halaman Manajemen Batch Tanam
 ┃ ┣ 📜 index.html          # Halaman utama (Form Pencatatan)
 ┃ ┗ 📜 logs.html           # Halaman Riwayat Pencatatan
 ┣ 📜 app.py                # File utama (FastAPI Routes & Controllers)
 ┣ 📜 database.py           # Konfigurasi database (SQLAlchemy engine, session)
 ┣ 📜 models.py             # Definisi skema Database (BatchTanam, LogHarian, BaselineIdeal)
 ┣ 📜 requirements.txt      # Daftar dependensi Python
 ┗ 📜 seed.py               # Script untuk mengisi data baseline dari paper riset
```

## ⚙️ Cara Menjalankan Project Secara Lokal

1. **Pastikan Python 3.10+** sudah terinstall di komputer Anda.
2. **Buat & Aktifkan Virtual Environment** (direkomendasikan):
   ```bash
   python -m venv venv
   
   # Di Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   
   # Di macOS/Linux
   source venv/bin/activate
   ```
3. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Seed Data Baseline** (jalankan sekali saja):
   ```bash
   python seed.py
   ```
5. **Jalankan Aplikasi**:
   ```bash
   python app.py
   ```
   Atau langsung dengan Uvicorn:
   ```bash
   uvicorn app:app --host 127.0.0.1 --port 5000 --reload
   ```
6. **Akses Aplikasi**:
   Buka browser dan kunjungi `http://127.0.0.1:5000`

## 🗺️ Roadmap Migrasi Production

Untuk versi production yang diakses luas dari banyak perangkat, pertimbangkan migrasi berikut:

| Komponen | MVP (Saat ini) | Production |
|----------|---------------|------------|
| Database | SQLite | PostgreSQL (concurrent writes, production-ready) |
| Vector DB | - | pgvector extension (pondasi RAG/chatbot) |
| Deployment | `python app.py` | Docker + Uvicorn multi-worker |
| HTTPS | - | Nginx reverse proxy + Let's Encrypt |

> **Catatan**: SQLite memiliki keterbatasan *concurrent write* yang perlu diperhatikan jika banyak pengguna mengakses bersamaan. Untuk skala kecil/MVP, SQLite masih memadai.
