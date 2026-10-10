"""
Katalog template monitor: tema warna, layout, preset sekali klik, dan template slide.

Satu sumber untuk pilihan model, tampilan monitor (variabel CSS), dan editor panel.
"""
from django.utils.translation import gettext_lazy as _

# key: (label, primary, accent, latar)
THEMES = {
    'default': (_('Hijau Masjid'), '#1a6b3c', '#f0a500', '#0f172a'),
    'emerald': (_('Zamrud'), '#047857', '#6ee7b7', '#022c22'),
    'forest': (_('Hutan'), '#14532d', '#86efac', '#04140b'),
    'mint': (_('Mint Segar'), '#059669', '#a7f3d0', '#03201a'),
    'nature': (_('Nuansa Alam'), '#3f6212', '#bef264', '#0f1c05'),
    'teal': (_('Tosca'), '#0f766e', '#5eead4', '#042f2e'),
    'blue': (_('Biru Laut'), '#0284c7', '#38bdf8', '#082f49'),
    'ocean': (_('Samudra'), '#1d4ed8', '#67e8f9', '#020b2a'),
    'royal': (_('Biru Kerajaan'), '#312e81', '#a5b4fc', '#0c0a24'),
    'ramadan': (_('Malam Ramadan'), '#1e3a8a', '#facc15', '#0b1026'),
    'purple': (_('Ungu Modern'), '#6d28d9', '#c4b5fd', '#2e1065'),
    'rose': (_('Mawar'), '#be185d', '#f9a8d4', '#1f0614'),
    'maroon': (_('Marun'), '#7f1d1d', '#fca5a5', '#1c0a0a'),
    'crimson': (_('Merah Emas'), '#9f1239', '#fcd34d', '#1a0509'),
    'sunset': (_('Senja'), '#c2410c', '#fdba74', '#1c0d05'),
    'copper': (_('Tembaga'), '#9a3412', '#fcd9b6', '#170c06'),
    'gold': (_('Emas Elegan'), '#713f12', '#fbbf24', '#1c1917'),
    'sand': (_('Gurun Pasir'), '#92400e', '#fde68a', '#1f1607'),
    'slate': (_('Abu Elegan'), '#475569', '#e2e8f0', '#0f172a'),
    'dark': (_('Monokrom'), '#334155', '#94a3b8', '#020617'),
}

_R = '<rect x="{}" y="{}" width="{}" height="{}" rx="2" class="{}"/>'


def _svg(*rects):
    body = ''.join(_R.format(*r) for r in rects)
    return f'<svg viewBox="0 0 160 90" aria-hidden="true"><rect width="160" height="90" class="tb-bg"/>{body}</svg>'


_PRAYERS_COL = [(8, 22 + i * 10, 34, 8, 'tb-p') for i in range(6)]
_PRAYERS_ROW = lambda y, x0=8, w=144: [(x0 + i * (w / 6), y, w / 6 - 3, 12, 'tb-p') for i in range(6)]
_HEAD = [(8, 6, 50, 6, 'tb-h'), (124, 5, 28, 9, 'tb-a')]

# key: (label, keterangan, thumbnail SVG)
LAYOUTS = {
    'classic': (_('Klasik'), _('Jadwal di kiri, slide di kanan'),
                _svg(*_HEAD, *_PRAYERS_COL, (48, 22, 104, 58, 'tb-s'))),
    'sidebar_right': (_('Sidebar Kanan'), _('Slide di kiri, jadwal di kanan'),
                      _svg(*_HEAD, *[(118, y, 34, w, c) for (_x, y, _w, w, c) in _PRAYERS_COL], (8, 22, 104, 58, 'tb-s'))),
    'modern': (_('Modern'), _('Slide besar, jadwal berjajar di bawah'),
               _svg(*_HEAD, (8, 20, 144, 44, 'tb-s'), *_PRAYERS_ROW(68))),
    'top_bar': (_('Jadwal Atas'), _('Jadwal berjajar di atas slide'),
                _svg(*_HEAD, *_PRAYERS_ROW(20), (8, 36, 144, 46, 'tb-s'))),
    'full_slider': (_('Slide Penuh'), _('Slide selebar layar, jadwal melayang'),
                    _svg((0, 0, 160, 90, 'tb-s'), *_HEAD, (30, 66, 100, 12, 'tb-p'))),
    'masjid_info': (_('Fokus Info'), _('Slide lebar dengan teks besar'),
                    _svg(*_HEAD, (8, 22, 112, 58, 'tb-s'), *[(124, 22 + i * 10, 28, 8, 'tb-p') for i in range(6)])),
    'simple': (_('Simple'), _('Judul & jam di tengah, rapi'),
               _svg((55, 5, 50, 5, 'tb-h'), (66, 12, 28, 7, 'tb-a'), *[(8, 24 + i * 9, 30, 7, 'tb-p') for i in range(6)], (44, 24, 108, 56, 'tb-s'))),
    'big_clock': (_('Jam Digital LED'), _('Jam LED merah besar & jadwal'),
                  _svg((50, 4, 60, 6, 'tb-h'), (40, 14, 80, 20, 'tb-led'), *[(22 + (i % 3) * 40, 42 + (i // 3) * 16, 36, 12, 'tb-p') for i in range(6)])),
    'countdown': (_('Hitung Mundur'), _('Sholat berikutnya & hitung mundur raksasa'),
                  _svg(*_HEAD, (30, 24, 100, 10, 'tb-h'), (24, 38, 112, 20, 'tb-a'), *_PRAYERS_ROW(68))),
    'analog': (_('Jam Analog'), _('Jam dinding analog & jadwal'),
               '<svg viewBox="0 0 160 90" aria-hidden="true"><rect width="160" height="90" class="tb-bg"/>'
               '<rect x="55" y="4" width="50" height="5" rx="2" class="tb-h"/>'
               '<circle cx="80" cy="36" r="22" class="tb-ring"/><path d="M80 36V20M80 36l10 6" class="tb-hand"/>'
               + ''.join(_R.format(x, 68, 21, 12, 'tb-p') for x in (8, 32.5, 57, 81.5, 106, 130.5)) + '</svg>'),
    'portrait': (_('TV Vertikal'), _('Untuk monitor yang dipasang tegak (portrait)'),
                 '<svg viewBox="0 0 160 90" aria-hidden="true"><rect width="160" height="90" class="tb-bg"/>'
                 '<rect x="55" y="2" width="50" height="86" rx="3" class="tb-frame"/>'
                 '<rect x="62" y="6" width="36" height="5" rx="2" class="tb-h"/><rect x="66" y="13" width="28" height="8" rx="2" class="tb-a"/>'
                 + ''.join(_R.format(60 + (i % 3) * 13.5, 25 + (i // 3) * 10, 12, 8, 'tb-p') for i in range(6))
                 + '<rect x="60" y="46" width="40" height="38" rx="2" class="tb-s"/></svg>'),
    'minimal': (_('Minimalis'), _('Latar polos, jam besar, tanpa slide'),
                _svg((60, 10, 40, 5, 'tb-h'), (36, 22, 88, 26, 'tb-a'), *_PRAYERS_ROW(62, 14, 132))),
    'ornamen': (_('Bingkai Ornamen'), _('Klasik dengan bingkai ornamen Islami'),
                '<svg viewBox="0 0 160 90" aria-hidden="true"><rect width="160" height="90" class="tb-orn"/>'
                '<rect x="5" y="5" width="150" height="80" class="tb-bg"/>'
                + ''.join(_R.format(*r) for r in [(12, 9, 50, 6, 'tb-h'), (122, 8, 28, 9, 'tb-a'),
                                                   *[(12, 24 + i * 9, 32, 7, 'tb-p') for i in range(6)], (48, 24, 102, 54, 'tb-s')])
                + '</svg>'),
}

# Preset sekali klik: kombinasi tema + layout (+ pengaturan lain)
PRESETS = [
    {'key': 'klasik', 'nama': _('Klasik Hijau'), 'ikon': 'bi-moon-stars', 'nilai': {'tema': 'default', 'layout': 'classic'}},
    {'key': 'modern', 'nama': _('Modern Biru'), 'ikon': 'bi-layout-text-window', 'nilai': {'tema': 'blue', 'layout': 'modern'}},
    {'key': 'ramadan', 'nama': _('Malam Ramadan'), 'ikon': 'bi-stars', 'nilai': {'tema': 'ramadan', 'layout': 'countdown', 'tampilkan_imsak': True}},
    {'key': 'jumat', 'nama': _('Jumat Berkah'), 'ikon': 'bi-flower1', 'nilai': {'tema': 'emerald', 'layout': 'ornamen'}},
    {'key': 'led', 'nama': _('Jam Digital LED'), 'ikon': 'bi-alarm', 'nilai': {'tema': 'default', 'layout': 'big_clock'}},
    {'key': 'analog', 'nama': _('Jam Analog Emas'), 'ikon': 'bi-clock', 'nilai': {'tema': 'gold', 'layout': 'analog'}},
    {'key': 'vertikal', 'nama': _('TV Vertikal'), 'ikon': 'bi-phone', 'nilai': {'tema': 'teal', 'layout': 'portrait'}},
    {'key': 'galeri', 'nama': _('Galeri Penuh'), 'ikon': 'bi-images', 'nilai': {'tema': 'ocean', 'layout': 'full_slider'}},
    {'key': 'kajian', 'nama': _('Info Kajian'), 'ikon': 'bi-megaphone', 'nilai': {'tema': 'royal', 'layout': 'masjid_info'}},
    {'key': 'minimalis', 'nama': _('Minimalis Gelap'), 'ikon': 'bi-circle-half', 'nilai': {'tema': 'slate', 'layout': 'minimal'}},
    {'key': 'senja', 'nama': _('Senja Hangat'), 'ikon': 'bi-sunset', 'nilai': {'tema': 'sunset', 'layout': 'sidebar_right'}},
    {'key': 'mundur', 'nama': _('Hitung Mundur Besar'), 'ikon': 'bi-hourglass-split', 'nilai': {'tema': 'maroon', 'layout': 'countdown'}},
    {'key': 'atas', 'nama': _('Jadwal Atas'), 'ikon': 'bi-layout-three-columns', 'nilai': {'tema': 'mint', 'layout': 'top_bar'}},
    {'key': 'gurun', 'nama': _('Gurun Pasir'), 'ikon': 'bi-brightness-high', 'nilai': {'tema': 'sand', 'layout': 'simple'}},
    {'key': 'mawar', 'nama': _('Mawar Elegan'), 'ikon': 'bi-heart', 'nilai': {'tema': 'rose', 'layout': 'ornamen'}},
    {'key': 'hutan', 'nama': _('Hutan Tenang'), 'ikon': 'bi-tree', 'nilai': {'tema': 'forest', 'layout': 'top_bar'}},
]

# Template slide siap pakai (bisa diubah sebelum disimpan)
SLIDE_TEMPLATES = [
    {'key': 'jadwal', 'ikon': 'bi-clock', 'judul': _('Jadwal Sholat Hari Ini'), 'tipe': 'sholat', 'durasi': 15, 'konten_teks': ''},
    {'key': 'jumat', 'ikon': 'bi-mic', 'judul': _('Petugas Jumat'), 'tipe': 'jumat', 'durasi': 15, 'konten_teks': ''},
    {'key': 'kegiatan', 'ikon': 'bi-calendar-event', 'judul': _('Kegiatan Mendatang'), 'tipe': 'kegiatan', 'durasi': 15, 'konten_teks': ''},
    {'key': 'berita', 'ikon': 'bi-newspaper', 'judul': _('Berita & Pengumuman'), 'tipe': 'berita', 'durasi': 15, 'konten_teks': ''},
    {'key': 'kas', 'ikon': 'bi-wallet2', 'judul': _('Laporan Kas Masjid'), 'tipe': 'kas', 'durasi': 12, 'konten_teks': ''},
    {'key': 'donasi', 'ikon': 'bi-heart', 'judul': _('Salurkan Infaq & Sedekah'), 'tipe': 'donasi', 'durasi': 15, 'konten_teks': ''},
    {'key': 'doa_masuk', 'ikon': 'bi-door-open', 'judul': _('Doa Masuk Masjid'), 'tipe': 'teks', 'durasi': 12,
     'konten_teks': 'اللَّهُمَّ افْتَحْ لِي أَبْوَابَ رَحْمَتِكَ\n\nAllahummaftah lii abwaaba rahmatik\n\n'
                    '“Ya Allah, bukakanlah untukku pintu-pintu rahmat-Mu.” (HR. Muslim)'},
    {'key': 'doa_keluar', 'ikon': 'bi-door-closed', 'judul': _('Doa Keluar Masjid'), 'tipe': 'teks', 'durasi': 12,
     'konten_teks': 'اللَّهُمَّ إِنِّي أَسْأَلُكَ مِنْ فَضْلِكَ\n\nAllahumma innii as-aluka min fadhlik\n\n'
                    '“Ya Allah, sesungguhnya aku memohon karunia-Mu.” (HR. Muslim)'},
    {'key': 'berjamaah', 'ikon': 'bi-people', 'judul': _('Keutamaan Sholat Berjamaah'), 'tipe': 'teks', 'durasi': 12,
     'konten_teks': '“Sholat berjamaah lebih utama dua puluh tujuh derajat daripada sholat sendirian.”\n\n(HR. Bukhari dan Muslim)'},
    {'key': 'tahiyat', 'ikon': 'bi-person-raised-hand', 'judul': _('Sholat Tahiyatul Masjid'), 'tipe': 'teks', 'durasi': 12,
     'konten_teks': '“Apabila salah seorang di antara kalian masuk masjid, hendaklah ia sholat dua rakaat sebelum duduk.”\n\n(HR. Bukhari dan Muslim)'},
    {'key': 'adab', 'ikon': 'bi-list-check', 'judul': _('Adab di Masjid'), 'tipe': 'teks', 'durasi': 12,
     'konten_teks': '• Nonaktifkan nada dering ponsel\n• Jaga kebersihan dan ketenangan\n• Luruskan dan rapatkan shaf\n• Simpan alas kaki pada tempatnya'},
    {'key': 'selamat_datang', 'ikon': 'bi-emoji-smile', 'judul': _('Ahlan wa Sahlan'), 'tipe': 'teks', 'durasi': 10,
     'konten_teks': 'Selamat datang di rumah Allah.\nSelamat beribadah, semoga Allah menerima amal kita semua.'},
    {'key': 'pengumuman', 'ikon': 'bi-megaphone', 'judul': _('Pengumuman'), 'tipe': 'teks', 'durasi': 15,
     'konten_teks': _('Tulis pengumuman di sini…')},
    {'key': 'poster', 'ikon': 'bi-image', 'judul': _('Poster / Pamflet'), 'tipe': 'gambar', 'durasi': 15, 'konten_teks': ''},
]

THEME_CHOICES = [(k, v[0]) for k, v in THEMES.items()]
LAYOUT_CHOICES = [(k, v[0]) for k, v in LAYOUTS.items()]


def theme_vars(key):
    _label, primary, accent, bg = THEMES.get(key, THEMES['default'])
    return f'--primary:{primary};--accent:{accent};--bg-dark:{bg}'
