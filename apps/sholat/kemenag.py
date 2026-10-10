"""
Ambil jadwal sholat resmi Kemenag RI per bulan dan simpan di basis data.

Sumber: API publik myQuran (api.myquran.com) yang menyalin jadwal Bimas Islam Kemenag.
Jaringan hanya dipakai bila data bulan tersebut belum ada; kegagalan ditahan 30 menit
agar halaman tidak lambat saat sumber sedang tidak bisa dihubungi.
"""
import json
import logging
import urllib.request
from datetime import date, time

from django.core.cache import cache
from django.db import transaction

from .models import JadwalSholatResmi, KotaKemenag

logger = logging.getLogger(__name__)

API_URL = 'https://api.myquran.com/v2/sholat/jadwal/{kota}/{year}/{month:02d}'
CITIES_URL = 'https://api.myquran.com/v2/sholat/kota/semua'
TIMEOUT = 8
RETRY_AFTER = 30 * 60
FIELDS = ('imsak', 'subuh', 'terbit', 'dzuhur', 'ashar', 'maghrib', 'isya')


# Jam di jadwal Kemenag adalah waktu setempat; zona ditentukan dari provinsi.
WITA = ('BALI', 'NUSA TENGGARA', 'NTB', 'NTT', 'KALIMANTAN SELATAN', 'KALIMANTAN TIMUR', 'KALIMANTAN UTARA',
        'SULAWESI', 'GORONTALO')
WIT = ('MALUKU', 'PAPUA')


def timezone_for(daerah):
    name = (daerah or '').upper()
    if any(name.startswith(p) for p in WIT):
        return 'Asia/Jayapura'
    if any(name.startswith(p) for p in WITA):
        return 'Asia/Makassar'
    return 'Asia/Jakarta'


def _get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'masjid.umko.ac.id', 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.load(resp)


def sync_cities(force=False):
    """Simpan daftar kab/kota Kemenag. Kembalikan jumlahnya (0 bila gagal)."""
    fail_key = 'kemenag-kota-gagal'
    if not force and cache.get(fail_key):
        return 0
    try:
        rows = _get_json(CITIES_URL)['data']
        cities = {str(r['id']): r['lokasi'].strip() for r in rows if r.get('id') and r.get('lokasi')}
        if not cities:
            raise ValueError('daftar kota kosong')
    except Exception as exc:
        logger.warning('Gagal mengambil daftar kota Kemenag: %s', exc)
        cache.set(fail_key, 1, RETRY_AFTER)
        return 0
    with transaction.atomic():
        existing = set(KotaKemenag.objects.values_list('id', flat=True))
        KotaKemenag.objects.bulk_create([KotaKemenag(id=i, nama=n) for i, n in cities.items() if i not in existing])
        for city in KotaKemenag.objects.filter(id__in=existing & set(cities)):
            if city.nama != cities[city.id]:
                city.nama = cities[city.id]
                city.save(update_fields=['nama', 'diperbarui'])
    return len(cities)


def find_city(kota_id):
    if not KotaKemenag.objects.exists():
        sync_cities()
    return KotaKemenag.objects.filter(id=str(kota_id)).first()


def search_cities(query=''):
    if not KotaKemenag.objects.exists():
        sync_cities()
    qs = KotaKemenag.objects.all()
    for word in query.split():
        qs = qs.filter(nama__icontains=word)
    return qs


def _parse_time(value):
    h, m = value.strip().split(':')[:2]
    return time(int(h), int(m))


def fetch_month(kota_id, year, month, force=False):
    """Simpan jadwal satu bulan. Kembalikan jumlah hari tersimpan (0 bila gagal)."""
    fail_key = f'kemenag-gagal:{kota_id}:{year}-{month}'
    if not force and cache.get(fail_key):
        return 0
    url = API_URL.format(kota=kota_id, year=year, month=month)
    try:
        payload = _get_json(url)
        rows = payload['data']['jadwal']
        parsed = []
        for row in rows:
            d = date.fromisoformat(row['date'])
            if (d.year, d.month) != (year, month):
                continue
            parsed.append((d, {f: _parse_time(row[f]) for f in FIELDS}))
        if not parsed:
            raise ValueError('jadwal kosong')
    except Exception as exc:  # jaringan, JSON, atau format berubah
        logger.warning('Gagal mengambil jadwal Kemenag %s %s-%02d: %s', kota_id, year, month, exc)
        cache.set(fail_key, 1, RETRY_AFTER)
        return 0
    info = payload.get('data') or {}
    with transaction.atomic():
        if info.get('lokasi'):
            KotaKemenag.objects.update_or_create(
                id=str(kota_id), defaults={'nama': info['lokasi'].strip(), 'daerah': (info.get('daerah') or '').strip()})
        for d, values in parsed:
            JadwalSholatResmi.objects.update_or_create(kota_id=kota_id, tanggal=d, defaults=values)
    return len(parsed)


def get_day(kota_id, target_date):
    row = JadwalSholatResmi.objects.filter(kota_id=kota_id, tanggal=target_date).first()
    if row is None and fetch_month(kota_id, target_date.year, target_date.month):
        row = JadwalSholatResmi.objects.filter(kota_id=kota_id, tanggal=target_date).first()
    return row


def get_month(kota_id, year, month):
    rows = {r.tanggal: r for r in JadwalSholatResmi.objects.filter(
        kota_id=kota_id, tanggal__year=year, tanggal__month=month)}
    if not rows and fetch_month(kota_id, year, month):
        rows = {r.tanggal: r for r in JadwalSholatResmi.objects.filter(
            kota_id=kota_id, tanggal__year=year, tanggal__month=month)}
    return rows
