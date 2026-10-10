"""
Hisab waktu sholat dengan kriteria Kementerian Agama RI.

Dipakai sebagai cadangan bila jadwal resmi Kemenag tidak dapat diambil.
Kriteria: Subuh -20°, Isya -18°, Ashar bayangan = 1 × tinggi benda + bayangan saat
istiwa (Syafi'i), terbit/terbenam memakai semidiameter + refraksi + kerendahan ufuk
(ketinggian tempat), ihtiyat ditambahkan lalu detik dibulatkan ke atas
(terbit: ihtiyat dikurangkan lalu dibulatkan ke bawah). Dzuhur = istiwa + 1 menit
(piringan matahari tergelincir) + ihtiyat.
Dicocokkan dengan jadwal resmi Kemenag Kab. Lampung Utara 2026: selisih paling
banyak 1 menit, dan tepat sama pada sebagian besar hari.
"""
import math
from datetime import time


def _julian_day(d, hour_utc):
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    jdn = d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn - 0.5 + hour_utc / 24


def _sun(jd):
    """Deklinasi (derajat) dan perata waktu (menit), algoritma Meeus."""
    t = (jd - 2451545.0) / 36525
    l0 = (280.46646 + t * (36000.76983 + 0.0003032 * t)) % 360
    m = math.radians(357.52911 + t * (35999.05029 - 0.0001537 * t))
    e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    c = ((1.914602 - t * (0.004817 + 0.000014 * t)) * math.sin(m)
         + (0.019993 - 0.000101 * t) * math.sin(2 * m) + 0.000289 * math.sin(3 * m))
    omega = math.radians(125.04 - 1934.136 * t)
    lam = math.radians(l0 + c - 0.00569 - 0.00478 * math.sin(omega))
    eps0 = 23 + (26 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60) / 60
    eps = math.radians(eps0 + 0.00256 * math.cos(omega))
    dec = math.degrees(math.asin(math.sin(eps) * math.sin(lam)))
    y = math.tan(eps / 2) ** 2
    l0r = math.radians(l0)
    eot = (y * math.sin(2 * l0r) - 2 * e * math.sin(m) + 4 * e * y * math.sin(m) * math.cos(2 * l0r)
           - 0.5 * y * y * math.sin(4 * l0r) - 1.25 * e * e * math.sin(2 * m))
    return dec, math.degrees(eot) * 4


def hisab(target_date, latitude, longitude, tz_offset_hours, elevation=0, ihtiyat=2):
    """Kembalikan dict menit-sejak-tengah-malam (int) untuk tiap waktu."""
    lat = math.radians(latitude)

    def transit(hour_local):
        _, eot = _sun(_julian_day(target_date, hour_local - tz_offset_hours))
        return 12 + tz_offset_hours - longitude / 15 - eot / 60

    def event(altitude, sign, guess):
        t = guess
        for _ in range(3):
            dec, eot = _sun(_julian_day(target_date, t - tz_offset_hours))
            noon = 12 + tz_offset_hours - longitude / 15 - eot / 60
            alt = altitude(dec) if callable(altitude) else altitude
            d = math.radians(dec)
            cos_h = (math.sin(math.radians(alt)) - math.sin(lat) * math.sin(d)) / (math.cos(lat) * math.cos(d))
            t = noon + sign * math.degrees(math.acos(max(-1.0, min(1.0, cos_h)))) / 15
        return t

    horizon = -(0.8333 + 0.0347 * math.sqrt(max(elevation, 0)))

    def asr_altitude(dec):
        return math.degrees(math.atan(1 / (1 + math.tan(abs(lat - math.radians(dec))))))

    up = lambda hours, extra: math.ceil(hours * 60 + extra - 1e-9)
    subuh = up(event(-20, -1, 5), ihtiyat)
    return {
        'imsak': subuh - 10,
        'subuh': subuh,
        'terbit': math.floor(event(horizon, -1, 6) * 60 - ihtiyat + 1e-9),
        'dzuhur': up(transit(12), 1 + ihtiyat),
        'ashar': up(event(asr_altitude, 1, 15), ihtiyat),
        'maghrib': up(event(horizon, 1, 18), ihtiyat),
        'isya': up(event(-18, 1, 19), ihtiyat),
    }


def minutes_to_time(minutes):
    minutes %= 24 * 60
    return time(minutes // 60, minutes % 60)
