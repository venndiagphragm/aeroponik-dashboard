# 🌿 Aeroponik Dashboard (Buku Saku Digital)

Aeroponik Dashboard adalah aplikasi berbasis web yang dirancang khusus untuk mempermudah pemantauan harian pertumbuhan tanaman dengan metode aeroponik. Aplikasi ini bertindak sebagai asisten pencatatan sekaligus memberikan umpan balik (feedback) secara instan mengenai kondisi tanaman berdasarkan usia, tinggi, dan jumlah daunnya.

Proyek ini awalnya bernama "Bayamin" dan telah disesuaikan menjadi dashboard "Aeroponik" dengan identitas visual khas Universitas Airlangga (UNAIR).

## 🚀 Fitur Utama

- **Pencatatan Harian Interaktif**: Form pencatatan untuk umur tanaman, tinggi (cm), dan jumlah helai daun dengan tombol (+) dan (-) yang mudah digunakan.
- **Integrasi Kamera Langsung**: Pengguna dapat langsung mengambil foto kondisi tanaman secara *real-time* menggunakan kamera belakang ponsel mereka.
- **Sistem Penilaian Otomatis (Smart Feedback)**: Aplikasi akan membandingkan data yang diinput dengan *baseline* ideal tanaman pada hari tersebut. Pengguna akan mendapatkan status instan:
  - 🟢 **Optimal (Hijau)**: Tumbuh subur.
  - 🟡 **Perhatian (Kuning)**: Pertumbuhan agak lambat.
  - 🔴 **Kritis (Merah)**: Kondisi darurat yang membutuhkan penanganan segera.
- **Riwayat Pencatatan (Logs)**: Halaman khusus untuk melihat seluruh data historis pencatatan, lengkap dengan status skor, ukuran, dan dokumentasi foto.
- **Buku Saku Digital**: Halaman panduan singkat cara penggunaan aplikasi dan standar lingkungan ideal untuk tanaman (suhu & kelembapan) serta kontak langsung ke Pendamping Desa via WhatsApp.
- **PWA (Progressive Web App)**: Dilengkapi dengan *manifest* dan *service-worker* sehingga aplikasi dapat diakses dengan mulus di perangkat *mobile*, di-*install* ke layar utama (Home Screen) layaknya aplikasi *native*, dan memiliki dukungan *caching*.

## 🛠️ Tech Stack (Teknologi yang Digunakan)

- **Backend**: Python 3, Flask
- **Database**: SQLite, Flask-SQLAlchemy (ORM)
- **Frontend / Styling**: HTML5, Vanilla JavaScript, Tailwind CSS (via CDN)
- **PWA**: Service Worker (`service-worker.js`), Web App Manifest (`manifest.json`)
- **Penyimpanan Berkas**: Penyimpanan lokal terstruktur untuk unggahan foto dokumentasi harian (`static/uploads`).

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
 ┃ ┣ 📜 index.html          # Halaman utama (Form Pencatatan)
 ┃ ┗ 📜 logs.html           # Halaman Riwayat Pencatatan
 ┣ 📜 app.py                # File utama (Routing & Controller) Flask
 ┣ 📜 models.py             # Definisi skema Database (SQLAlchemy)
 ┣ 📜 requirements.txt      # Daftar dependensi Python
 ┗ 📜 seed.py               # Script untuk mengisi data baseline (opsional)
```

## ⚙️ Cara Menjalankan Project Secara Lokal

1. **Pastikan Python sudah terinstall** di komputer Anda.
2. **Aktifkan Virtual Environment** (direkomendasikan):
   ```bash
   # Di Windows (PowerShell)
   .\venv\Scripts\Activate.ps1
   ```
3. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Jalankan Aplikasi Flask**:
   ```bash
   python app.py
   ```
5. **Akses Aplikasi**:
   Buka browser dan kunjungi `http://127.0.0.1:5000`
