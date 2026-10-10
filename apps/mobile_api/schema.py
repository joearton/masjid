"""Skema OpenAPI API MyUMKO Masjid: panduan, tag, dan galat seragam."""

PREFIX = '/api/mobile/v1/'


def only_mobile(endpoints, **kwargs):
    """Hanya endpoint seluler, tanpa endpoint skema/dokumentasi dan penampung 404."""
    return [e for e in endpoints if e[0].startswith(PREFIX)
            and not e[0].endswith(('/schema/', '/docs/', '/redoc/')) and '.*' not in e[0]]


GUIDE = """
API publik **Masjid UMKO** (masjid.umko.ac.id) untuk aplikasi seluler **MyUMKO**: jadwal sholat,
jadwal Jumat, kegiatan, berita & pengumuman, laporan kas, dan profil masjid.
Semua endpoint **hanya baca** dan **tanpa autentikasi** (tidak perlu token SSO; jangan kirim `Authorization`).

## Mulai cepat
1. `GET /meta/` saat fitur Masjid dibuka (nama, alamat, warna, tautan, sumber jadwal, fitur aktif).
2. Kartu beranda: `GET /sholat/` → jadwal hari ini + `berikutnya` (waktu sholat wajib berikutnya, hitung mundur).
3. Tab: Jadwal (`/sholat/bulan/`, `/jumat/`), Kegiatan (`/kegiatan/?upcoming=true`), Berita (`/berita/`),
   Kas (`/keuangan/`, hanya bila `meta.features.keuangan`), Profil (`/profil/`).

## Jadwal sholat
* Sumber bawaan: **jadwal resmi Kementerian Agama RI** untuk Kab. Lampung Utara (Kotabumi), disalin harian
  dari Bimas Islam. Bila tidak tersedia, server menghitung dengan kriteria Kemenag (Subuh -20°, Isya -18°,
  ihtiyat 2 menit) — selisih paling banyak 1 menit. `sumber` = `kemenag` / `hisab`.
* `waktu.*` = datetime ISO ber-zona (+07:00) untuk hitung mundur/alarm; `jam.*` = teks `HH:MM` siap tampil.
* Imsak = 10 menit sebelum Subuh. `terbit` bukan waktu sholat (batas akhir Subuh).
* `berikutnya.besok = true` setelah Isya (Subuh esok hari). Segarkan saat aplikasi kembali ke latar depan.
* Jadwal sama persis dengan situs web dan layar display masjid.

## Jadwal sesuai lokasi pengguna
Tanpa parameter = **lokasi masjid** (Kotabumi, Kab. Lampung Utara). `/sholat/` dan `/sholat/bulan/` menerima:
* `?kota=<kode>` — jadwal **resmi Kemenag** kab/kota itu (paling akurat). Cari kodenya dengan
  `GET /sholat/kota/?search=bandar lampung`. Jam dalam waktu setempat kota itu (WIB/WITA/WIT otomatis).
  Bila sumber Kemenag untuk kota itu sedang tidak dapat diambil → `503 jadwal_tidak_tersedia`
  (tawarkan lokasi GPS atau jadwal masjid).
* `?lat=&lon=` (GPS ponsel) — hisab kriteria Kemenag untuk titik itu. Kirim juga `&tz=` (zona IANA perangkat,
  mis. `Asia/Makassar`); tanpa `tz` server memperkirakan zona dari koordinat (wajib di luar Indonesia).
* `lokasi` pada respons: `{jenis: masjid|kota|koordinat, nama, kota_id, latitude, longitude, timezone}` —
  tampilkan "Jadwal untuk: …". Simpan pilihan pengguna di perangkat; jangan kirim lokasi ke layanan lain.

## Konvensi
* **Galat**: `{"detail": "pesan siap tampil", "code": "kode_mesin", "errors": {"param": ["pesan"]}}`.
* **Paginasi** (`/kegiatan/`, `/berita/`): `?page=` & `?page_size=` (bawaan 20, maks. 50) → `{count, next, previous, results}`.
* **Pilihan** `{"value": "upcoming", "label": "Akan Datang"}`. **Tanggal** ISO-8601, zona Asia/Jakarta.
* **Teks**: `isi`/`deskripsi` teks biasa; `*_html` versi HTML sederhana (paragraf) siap tampil.
* **URL** gambar selalu absolut. **Uang** dalam rupiah (angka bulat).
* **Cache**: GET berhasil membawa `Cache-Control: public, max-age=300` (`/sholat/`: 60 detik).
* **Batas laju**: 300 permintaan/menit per IP → `429` `throttled`.

## Kode galat
| HTTP | `code` | Arti |
|---|---|---|
| 400 | `invalid` | Parameter tidak valid; lihat `errors` |
| 404 | `not_found` | Data/alamat tidak ada, atau fitur (keuangan) disembunyikan pengurus |
| 405 | `method_not_allowed` | API hanya menerima GET |
| 429 | `throttled` | Terlalu banyak permintaan |
"""

TAGS = [
    ('Layanan', 'Informasi layanan dan profil masjid.'),
    ('Jadwal sholat', 'Jadwal sholat harian/bulanan (Kemenag RI) dan jadwal Jumat.'),
    ('Kegiatan', 'Kajian dan kegiatan masjid.'),
    ('Berita', 'Berita dan pengumuman masjid.'),
    ('Keuangan', 'Laporan kas bulanan yang juga tampil di situs web.'),
]

ERROR_SCHEMA = {
    'type': 'object',
    'required': ['detail', 'code'],
    'properties': {
        'detail': {'type': 'string', 'description': 'Pesan siap tampil.'},
        'code': {'type': 'string', 'description': 'Kode mesin, lihat tabel kode galat.'},
        'errors': {'type': 'object', 'additionalProperties': {'type': 'array', 'items': {'type': 'string'}}},
    },
    'example': {'detail': 'Parameter tidak valid.', 'code': 'invalid', 'errors': {'month': ['Format bulan harus YYYY-MM.']}},
}


def postprocess(result, generator, request, public):
    result['info']['description'] = GUIDE.strip()
    result['info']['contact'] = {'name': 'ICT UMKO', 'url': 'https://helpdesk.umko.ac.id/'}
    result['tags'] = [{'name': name, 'description': text} for name, text in TAGS]
    result.setdefault('components', {}).setdefault('schemas', {})['Error'] = ERROR_SCHEMA
    ref = {'$ref': '#/components/schemas/Error'}
    for path, methods in result.get('paths', {}).items():
        for op in methods.values():
            op['security'] = [{}]
            responses = op.setdefault('responses', {})
            for code, text in (('400', 'Parameter tidak valid'), ('404', 'Tidak ditemukan'),
                               ('429', 'Terlalu banyak permintaan')):
                responses.setdefault(code, {'description': text, 'content': {'application/json': {'schema': ref}}})
    return result


SCHEMA_SETTINGS = {
    'TITLE': 'Masjid UMKO · API MyUMKO',
    'DESCRIPTION': '',
    'VERSION': '1.0.0',
    'SCHEMA_PATH_PREFIX': '/api/mobile/v1',
    'TAGS': [],
    'PREPROCESSING_HOOKS': ['apps.mobile_api.schema.only_mobile'],
    'POSTPROCESSING_HOOKS': ['apps.mobile_api.schema.postprocess'],
    'SWAGGER_UI_DIST': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14',
    'REDOC_DIST': 'https://cdn.jsdelivr.net/npm/redoc@2.1.5',
    'SWAGGER_UI_SETTINGS': {'displayRequestDuration': True, 'docExpansion': 'list', 'deepLinking': True,
                            'defaultModelsExpandDepth': 0, 'tryItOutEnabled': True},
    'SERVERS': [{'url': 'https://masjid.umko.ac.id', 'description': 'Produksi'}],
}
