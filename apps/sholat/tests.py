import datetime as dt
import json
from unittest import mock

from django.core.cache import cache
from django.test import TestCase

from .hisab import hisab
from .models import JadwalSholatResmi, SholatSettings
from .utils import get_month_schedule, get_prayer_times

# Cuplikan jadwal resmi Kemenag Kab. Lampung Utara (kode 1002).
KEMENAG = {
    '2026-01-15': ('04:28', '04:38', '05:55', '12:13', '15:37', '18:24', '19:38'),
    '2026-04-15': ('04:35', '04:45', '05:57', '12:04', '15:21', '18:04', '19:13'),
    '2026-07-15': ('04:40', '04:50', '06:07', '12:10', '15:32', '18:06', '19:19'),
    '2026-10-10': ('04:17', '04:27', '05:39', '11:51', '14:54', '17:56', '19:05'),
}
KEYS = ('imsak', 'subuh', 'terbit', 'dzuhur', 'ashar', 'maghrib', 'isya')


def minutes(hhmm):
    h, m = map(int, hhmm.split(':'))
    return h * 60 + m


class HisabTests(TestCase):
    def test_kotabumi_close_to_kemenag(self):
        for day, ref in KEMENAG.items():
            out = hisab(dt.date.fromisoformat(day), -4.82, 104.884, 7, 20, 2)
            for key, value in zip(KEYS, ref):
                self.assertLessEqual(abs(out[key] - minutes(value)), 1, f'{day} {key}')

    def test_default_settings_are_kotabumi_not_jakarta(self):
        s = SholatSettings()
        self.assertEqual(s.kota_kemenag_id, '1002')
        self.assertAlmostEqual(s.latitude, -4.82, places=2)
        self.assertEqual(s.koreksi_maghrib, 0)


def fake_response(year, month):
    rows = []
    for day, ref in KEMENAG.items():
        d = dt.date.fromisoformat(day)
        if (d.year, d.month) == (year, month):
            rows.append(dict(zip(KEYS, ref), date=day))
    body = json.dumps({'status': True, 'data': {'jadwal': rows}}).encode()
    resp = mock.MagicMock()
    resp.__enter__.return_value.read.return_value = body
    return resp


class OfficialScheduleTests(TestCase):
    def setUp(self):
        cache.clear()
        SholatSettings.objects.create()

    def test_uses_official_times_and_caches_them(self):
        with mock.patch('urllib.request.urlopen', return_value=fake_response(2026, 10)) as urlopen:
            pt = get_prayer_times(dt.date(2026, 10, 10))
            get_prayer_times(dt.date(2026, 10, 10))
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(pt.source, 'kemenag')
        self.assertEqual(pt.maghrib.strftime('%H:%M'), '17:56')
        self.assertEqual(pt.fajr.strftime('%H:%M'), '04:27')  # nama atribut lama tetap ada
        self.assertTrue(JadwalSholatResmi.objects.filter(tanggal='2026-10-10').exists())

    def test_falls_back_to_hisab_and_backs_off(self):
        with mock.patch('urllib.request.urlopen', side_effect=OSError('offline')) as urlopen:
            pt = get_prayer_times(dt.date(2026, 10, 10))
            get_prayer_times(dt.date(2026, 10, 11))
        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(pt.source, 'hisab')
        self.assertLessEqual(abs(pt.maghrib.hour * 60 + pt.maghrib.minute - minutes('17:56')), 1)

    def test_manual_correction_is_applied(self):
        SholatSettings.objects.update(koreksi_maghrib=3)
        with mock.patch('urllib.request.urlopen', return_value=fake_response(2026, 10)):
            pt = get_prayer_times(dt.date(2026, 10, 10))
        self.assertEqual(pt.maghrib.strftime('%H:%M'), '17:59')

    def test_month_schedule_has_every_day(self):
        with mock.patch('urllib.request.urlopen', side_effect=OSError('offline')):
            month = get_month_schedule(2026, 2)
        self.assertEqual(len(month), 28)

    def test_datetime_argument_uses_local_date(self):
        utc_evening = dt.datetime(2026, 10, 9, 20, 0, tzinfo=dt.timezone.utc)  # 10 Okt 03:00 WIB
        with mock.patch('urllib.request.urlopen', side_effect=OSError('offline')):
            self.assertEqual(get_prayer_times(utc_evening).tanggal, dt.date(2026, 10, 10))


class PublicPagesTests(TestCase):
    def test_pages_render(self):
        with mock.patch('urllib.request.urlopen', side_effect=OSError('offline')):
            for url in ('/', '/sholat/', '/sholat/cetak/', '/display/', '/keuangan/?bulan=abc&tahun=0'):
                self.assertEqual(self.client.get(url).status_code, 200, url)
