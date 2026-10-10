"""Jadwal sholat: jadwal resmi Kemenag bila tersedia, hisab kriteria Kemenag sebagai cadangan."""
import calendar
import datetime as dt
from zoneinfo import ZoneInfo

from django.utils import timezone as dj_timezone

from . import kemenag
from .hisab import hisab, minutes_to_time
from .models import SholatSettings

KEYS = ('imsak', 'subuh', 'terbit', 'dzuhur', 'ashar', 'maghrib', 'isya')
KOREKSI = {'subuh': 'koreksi_subuh', 'dzuhur': 'koreksi_dzuhur', 'ashar': 'koreksi_ashar',
           'maghrib': 'koreksi_maghrib', 'isya': 'koreksi_isya'}


class PrayerSchedule:
    """Waktu sholat satu hari sebagai datetime ber-zona waktu.

    Atribut adhanpy (fajr, sunrise, dhuhr, asr, maghrib, isha) tetap tersedia untuk templat lama.
    """
    def __init__(self, tanggal, times, source):
        self.tanggal = tanggal
        self.source = source
        for key, value in times.items():
            setattr(self, key, value)

    fajr = property(lambda self: self.subuh)
    sunrise = property(lambda self: self.terbit)
    dhuhr = property(lambda self: self.dzuhur)
    asr = property(lambda self: self.ashar)
    isha = property(lambda self: self.isya)

    def as_dict(self):
        data = {'tanggal': self.tanggal, 'sumber': self.source}
        data.update({key: getattr(self, key) for key in KEYS})
        return data


class JadwalTidakTersedia(Exception):
    """Jadwal resmi kota pilihan pengguna belum dapat diambil (tidak ada koordinat untuk hisab)."""


class LokasiKota:
    """Jadwal resmi Kemenag untuk kab/kota pilihan pengguna (tanpa koreksi masjid)."""
    sumber = SholatSettings.SUMBER_KEMENAG
    wajib_resmi = True
    ihtiyat = 2
    elevasi = 0
    latitude = longitude = None

    def __init__(self, kota):
        self.kota = kota
        self.kota_kemenag_id = kota.id

    @property
    def kota_kemenag_nama(self):
        return self.kota.nama

    @property
    def timezone(self):
        if not self.kota.daerah:  # mungkin baru tersimpan saat jadwal diambil
            self.kota.refresh_from_db(fields=['daerah'])
        return kemenag.timezone_for(self.kota.daerah)


class LokasiKoordinat:
    """Hisab kriteria Kemenag untuk koordinat pengguna (mis. GPS ponsel)."""
    sumber = SholatSettings.SUMBER_HISAB
    wajib_resmi = False
    kota_kemenag_id = kota_kemenag_nama = ''
    ihtiyat = 2

    def __init__(self, latitude, longitude, timezone, elevasi=0):
        self.latitude, self.longitude, self.timezone, self.elevasi = latitude, longitude, timezone, elevasi


def zona_indonesia(latitude, longitude):
    """Perkiraan zona waktu Indonesia dari koordinat; None bila di luar Indonesia.

    Perkiraan (batas provinsi tidak lurus); klien sebaiknya mengirim zona waktu perangkat.
    """
    if not (-11.5 <= latitude <= 6.5 and 94.5 <= longitude <= 141.5):
        return None
    if longitude >= 127 or (longitude >= 125 and -4 <= latitude <= 0):  # Maluku, Maluku Utara, Papua
        return 'Asia/Jayapura'
    if longitude >= 114.5:  # Bali, Nusa Tenggara, Kalsel/Kaltim/Kaltara, Sulawesi
        return 'Asia/Makassar'
    return 'Asia/Jakarta'


def get_settings():
    return SholatSettings.objects.first() or SholatSettings()


def _to_date(value):
    if value is None:
        return dj_timezone.localdate()
    if isinstance(value, dt.datetime):
        return dj_timezone.localtime(value).date() if dj_timezone.is_aware(value) else value.date()
    return value


def _build(target_date, settings, official=None):
    tz = ZoneInfo(settings.timezone or 'Asia/Jakarta')
    if official is not None:
        clock = {key: getattr(official, key) for key in KEYS}
        source = 'kemenag'
    else:
        offset = tz.utcoffset(dt.datetime.combine(target_date, dt.time(12))).total_seconds() / 3600
        minutes = hisab(target_date, settings.latitude, settings.longitude, offset,
                        settings.elevasi or 0, settings.ihtiyat)
        clock = {key: minutes_to_time(minutes[key]) for key in KEYS}
        source = 'hisab'
    times = {}
    for key in KEYS:
        value = dt.datetime.combine(target_date, clock[key], tzinfo=tz)
        koreksi = getattr(settings, KOREKSI[key], 0) if key in KOREKSI else 0
        times[key] = value + dt.timedelta(minutes=koreksi or 0)
    return PrayerSchedule(target_date, times, source)


def get_prayer_times(target_date=None, settings=None):
    """Jadwal sholat untuk satu tanggal (date atau datetime). None hanya bila terjadi galat tak terduga."""
    target_date = _to_date(target_date)
    settings = settings or get_settings()
    official = None
    if settings.sumber == SholatSettings.SUMBER_KEMENAG and settings.kota_kemenag_id:
        official = kemenag.get_day(settings.kota_kemenag_id, target_date)
    if official is None and getattr(settings, 'wajib_resmi', False):
        raise JadwalTidakTersedia(settings.kota_kemenag_id)
    return _build(target_date, settings, official)


def get_month_schedule(year, month, settings=None):
    settings = settings or get_settings()
    official = {}
    if settings.sumber == SholatSettings.SUMBER_KEMENAG and settings.kota_kemenag_id:
        official = kemenag.get_month(settings.kota_kemenag_id, year, month)
    days = calendar.monthrange(year, month)[1]
    if getattr(settings, 'wajib_resmi', False) and len(official) < days:
        raise JadwalTidakTersedia(settings.kota_kemenag_id)
    return [_build(d, settings, official.get(d))
            for d in (dt.date(year, month, n) for n in range(1, days + 1))]
