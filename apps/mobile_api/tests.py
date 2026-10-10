import datetime as dt
from unittest import mock

from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from apps.berita.models import Berita, KategoriBerita
from apps.kegiatan.models import Kegiatan
from apps.keuangan.models import KategoriKeuangan, TransaksiKeuangan
from apps.profil.models import ProfilMasjid
from apps.sholat.models import JadwalJumat, SholatSettings

API = '/api/mobile/v1/'


class MobileApiTests(TestCase):
    def setUp(self):
        cache.clear()
        self.offline = mock.patch('urllib.request.urlopen', side_effect=OSError('offline'))
        self.offline.start()
        self.addCleanup(self.offline.stop)
        SholatSettings.objects.create()
        ProfilMasjid.objects.create(nama='Masjid Sadhana At-Taqwa', sejarah='s', visi='v', misi='m', alamat='Kotabumi')

    def get(self, path, **params):
        resp = self.client.get(API + path, params)
        return resp, resp.json()

    def test_meta_and_profil(self):
        resp, data = self.get('meta/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['name'], 'Masjid Sadhana At-Taqwa')
        self.assertEqual(data['jadwal_sholat']['sumber']['value'], 'kemenag')
        self.assertIn('public', resp['Cache-Control'])
        resp, data = self.get('profil/')
        self.assertEqual(data['profil']['alamat'], 'Kotabumi')

    def test_sholat_today_and_next(self):
        resp, data = self.get('sholat/', date='2026-10-10')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['tanggal'], '2026-10-10')
        self.assertEqual(set(data['jam']), {'imsak', 'subuh', 'terbit', 'dzuhur', 'ashar', 'maghrib', 'isya'})
        self.assertTrue(data['waktu']['maghrib'].endswith('+07:00'))
        self.assertIn(data['berikutnya']['key'], ('subuh', 'dzuhur', 'ashar', 'maghrib', 'isya'))
        self.assertGreater(data['berikutnya']['detik_lagi'], 0)

    def test_sholat_month_and_validation(self):
        _, data = self.get('sholat/bulan/', month='2026-02')
        self.assertEqual(len(data['results']), 28)
        resp, data = self.get('sholat/bulan/', month='2026-13')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['code'], 'invalid')
        self.assertIn('month', data['errors'])
        resp, data = self.get('sholat/', date='kemarin')
        self.assertEqual(resp.status_code, 400)

    def test_jumat_kegiatan_berita(self):
        today = timezone.localdate()
        JadwalJumat.objects.create(tanggal=today + dt.timedelta(days=3), khatib='Ust. A', imam='Ust. B')
        Kegiatan.objects.create(judul='Kajian Subuh', deskripsi='x' * 300, tanggal=today + dt.timedelta(days=1),
                                waktu_mulai=dt.time(5, 0), tempat='Masjid')
        Kegiatan.objects.create(judul='Lama', deskripsi='y', tanggal=today - dt.timedelta(days=5),
                                waktu_mulai=dt.time(8, 0), tempat='Masjid')
        kat = KategoriBerita.objects.create(nama='Pengumuman')
        Berita.objects.create(judul='Info Idul Adha', isi='Baris 1\n\nBaris 2', kategori=kat, is_published=True)
        Berita.objects.create(judul='Draf', isi='rahasia', is_published=False)

        _, data = self.get('jumat/')
        self.assertEqual(data['results'][0]['khatib'], 'Ust. A')
        _, data = self.get('kegiatan/', upcoming='true')
        self.assertEqual([k['judul'] for k in data['results']], ['Kajian Subuh'])
        self.assertTrue(data['results'][0]['ringkasan'].endswith('…'))
        _, data = self.get('kegiatan/')
        self.assertEqual(data['count'], 2)
        self.assertEqual(data['results'][1]['status']['value'], 'done')
        kid = data['results'][0]['id']
        _, detail = self.get(f'kegiatan/{kid}/')
        self.assertIn('deskripsi_html', detail)

        _, data = self.get('berita/')
        self.assertEqual(data['count'], 1)
        _, detail = self.get('berita/info-idul-adha/')
        self.assertIn('<p>Baris 1</p>', detail['isi_html'])
        resp, _ = self.get('berita/draf/')
        self.assertEqual(resp.status_code, 404)
        _, data = self.get('berita/kategori/')
        self.assertEqual(data['results'], [{'slug': 'pengumuman', 'nama': 'Pengumuman', 'count': 1}])

    def test_keuangan(self):
        masuk = KategoriKeuangan.objects.create(nama='Infaq Jumat', jenis='pemasukan')
        keluar = KategoriKeuangan.objects.create(nama='Listrik', jenis='pengeluaran')
        TransaksiKeuangan.objects.create(tanggal=dt.date(2026, 9, 5), kategori=masuk, keterangan='a', jumlah=500000)
        TransaksiKeuangan.objects.create(tanggal=dt.date(2026, 10, 2), kategori=masuk, keterangan='b', jumlah=250000)
        TransaksiKeuangan.objects.create(tanggal=dt.date(2026, 10, 3), kategori=keluar, keterangan='c', jumlah=100000)
        _, data = self.get('keuangan/', month='2026-10')
        self.assertEqual((data['saldo_awal'], data['pemasukan'], data['pengeluaran'], data['saldo_akhir']),
                         (500000, 250000, 100000, 650000))
        self.assertEqual(len(data['transaksi']), 2)

    def test_errors_are_uniform(self):
        resp, data = self.get('tidak-ada/')
        self.assertEqual((resp.status_code, data['code']), (404, 'not_found'))
        resp = self.client.post(API + 'meta/')
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json()['code'], 'method_not_allowed')

    def test_schema_and_docs(self):
        resp = self.client.get(API + 'schema/', {'format': 'json'})
        self.assertEqual(resp.status_code, 200)
        paths = resp.json()['paths']
        self.assertIn('/api/mobile/v1/sholat/', paths)
        self.assertNotIn('/api/mobile/v1/schema/', paths)
        self.assertEqual(self.client.get(API + 'docs/').status_code, 200)


def kota_response(url, *a, **k):
    """Tiruan myquran: daftar kota + jadwal bulanan Kota Makassar (WITA) & Lampung Utara."""
    import json as _json
    if url.endswith('/kota/semua'):
        body = {'status': True, 'data': [{'id': '1002', 'lokasi': 'KAB. LAMPUNG UTARA'},
                                         {'id': '2622', 'lokasi': 'KOTA MAKASSAR'}]}
    else:
        kota = url.split('/jadwal/')[1].split('/')[0]
        year, month = (int(x) for x in url.rstrip('/').split('/')[-2:])
        days = calendar.monthrange(year, month)[1]
        lokasi, daerah, base = (('KOTA MAKASSAR', 'SULAWESI SELATAN', '11:53') if kota == '2622'
                                else ('KAB. LAMPUNG UTARA', 'LAMPUNG', '11:51'))
        rows = [{'date': f'{year}-{month:02d}-{d:02d}', 'imsak': '04:00', 'subuh': '04:10', 'terbit': '05:25',
                 'dzuhur': base, 'ashar': '15:00', 'maghrib': '17:58', 'isya': '19:08'} for d in range(1, days + 1)]
        body = {'status': True, 'data': {'id': int(kota), 'lokasi': lokasi, 'daerah': daerah, 'jadwal': rows}}
    resp = mock.MagicMock()
    resp.__enter__.return_value.read.return_value = _json.dumps(body).encode()
    return resp


import calendar  # noqa: E402


class LokasiPenggunaTests(TestCase):
    def setUp(self):
        cache.clear()
        SholatSettings.objects.create()
        patcher = mock.patch('urllib.request.urlopen', side_effect=lambda req, *a, **k: kota_response(req.full_url))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_default_is_masjid_kotabumi(self):
        data = self.client.get(API + 'sholat/').json()
        self.assertEqual(data['lokasi']['jenis'], 'masjid')
        self.assertEqual(data['lokasi']['nama'], 'KAB. LAMPUNG UTARA')
        self.assertEqual(data['jam']['dzuhur'], '11:51')

    def test_city_search_and_official_city_schedule_in_local_time(self):
        data = self.client.get(API + 'sholat/kota/', {'search': 'makas'}).json()
        self.assertEqual(data['results'][0]['id'], '2622')
        data = self.client.get(API + 'sholat/', {'kota': '2622', 'date': '2026-10-10'}).json()
        self.assertEqual(data['lokasi']['jenis'], 'kota')
        self.assertEqual(data['lokasi']['timezone'], 'Asia/Makassar')
        self.assertEqual(data['jam']['dzuhur'], '11:53')
        self.assertTrue(data['waktu']['dzuhur'].endswith('+08:00'))
        month = self.client.get(API + 'sholat/bulan/', {'kota': '2622', 'month': '2026-10'}).json()
        self.assertEqual(len(month['results']), 31)

    def test_coordinates_use_hisab_and_zone(self):
        data = self.client.get(API + 'sholat/', {'lat': '-5.4294', 'lon': '105.2625', 'date': '2026-10-10'}).json()
        self.assertEqual((data['lokasi']['jenis'], data['sumber'], data['lokasi']['timezone']),
                         ('koordinat', 'hisab', 'Asia/Jakarta'))
        jayapura = self.client.get(API + 'sholat/', {'lat': '-2.533', 'lon': '140.717'}).json()
        self.assertEqual(jayapura['lokasi']['timezone'], 'Asia/Jayapura')
        self.assertTrue(jayapura['waktu']['subuh'].endswith('+09:00'))

    def test_location_validation(self):
        cases = [({'kota': '2622', 'lat': '1', 'lon': '1'}, 400), ({'kota': '9999'}, 404),
                 ({'lat': 'abc', 'lon': '1'}, 400), ({'lat': '48.85', 'lon': '2.35'}, 400),
                 ({'lat': '48.85', 'lon': '2.35', 'tz': 'Europe/Paris'}, 200), ({'lat': '1', 'lon': '1', 'tz': 'Mars/X'}, 400)]
        for params, status in cases:
            self.assertEqual(self.client.get(API + 'sholat/', params).status_code, status, params)

    def test_city_unavailable_is_503(self):
        with mock.patch('urllib.request.urlopen', side_effect=lambda req, *a, **k: (
                kota_response(req.full_url) if req.full_url.endswith('/kota/semua') else (_ for _ in ()).throw(OSError()))):
            cache.clear()
            resp = self.client.get(API + 'sholat/', {'kota': '2622'})
        self.assertEqual((resp.status_code, resp.json()['code']), (503, 'jadwal_tidak_tersedia'))
