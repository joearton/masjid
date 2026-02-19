# Panduan Instalasi Sistem Informasi Masjid

Selamat datang di proyek Sistem Informasi Masjid. Berikut adalah panduan langkah demi langkah untuk menginstal dan menjalankan aplikasi ini di komputer lokal Anda.

## Prasyarat

Pastikan **Python 3.8+** dan **pip** sudah terinstal di komputer Anda sebelum memulai.

## 1. Persiapan Lingkungan (Virtual Environment)

Disarankan menggunakan *virtual environment* agar dependensi proyek tidak tercampur dengan sistem global.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Instalasi Dependensi

Instal paket-paket Python yang dibutuhkan oleh aplikasi ini.

```bash
pip install django django-crispy-forms crispy-bootstrap5 pillow adhanpy pytz currency-symbols
```

*> Jika tersedia file `requirements.txt`, Anda bisa menggunakan perintah: `pip install -r requirements.txt`*

## 3. Setup Database & Migrasi

Inisialisasi database SQLite (default) dan jalankan migrasi tabel.

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Import Dummy Data (Data Contoh)

Aplikasi ini menyediakan perintah khusus untuk mengisi database dengan data contoh, meliputi:
- Jadwal Sholat & Pengaturan Lokasi
- Berita & Pengumuman
- Kegiatan Masjid
- Laporan Keuangan (Pemasukan/Pengeluaran)
- Data Donatur
- Akun Admin & Staff

Jalankan perintah berikut:

```bash
python manage.py populate_dummy_data
```

### Akun Admin Default:
- **Superuser:** Username: `admin` / Password: `admin`
- **Staff:** Username: `staff` / Password: `staff`

## 5. Menjalankan Server

Jalankan server pengembangan lokal Django.

```bash
python manage.py runserver
```

## 6. Akses Aplikasi

Setelah server berjalan, Anda dapat mengakses aplikasi melalui browser:

- **Halaman Publik:** [http://localhost:8000](http://localhost:8000)
- **Panel Admin (Dashboard Pengurus):** [http://localhost:8000/panel/](http://localhost:8000/panel/)
- **Display Digital Signage (TV Masjid):** [http://localhost:8000/display/](http://localhost:8000/display/)
- **Django Admin (Superuser):** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## Lisensi & Penggunaan

Proyek ini bersifat **Open Source** dan bebas digunakan oleh siapa saja, baik untuk keperluan pribadi, komunitas, maupun institusi masjid. Anda diperbolehkan untuk memodifikasi, mendistribusikan ulang, dan menggunakan kode sumber ini tanpa biaya lisensi apa pun.

Semoga bermanfaat untuk kemakmuran masjid dan umat.

