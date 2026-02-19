from adhanpy.calculation.CalculationMethod import CalculationMethod
from adhanpy.calculation.CalculationParameters import CalculationParameters
from adhanpy.PrayerTimes import PrayerTimes
from datetime import datetime
from zoneinfo import ZoneInfo

# Koordinat Lampung Utara (Kotabumi)
LATITUDE  = -4.82505
LONGITUDE = 104.8817
TZ_NAME   = "Asia/Jakarta"

print(f"Menggunakan library adhanpy (Local Calculation)...")
print(f"Lokasi   : Lampung Utara ({LATITUDE}, {LONGITUDE})")
print(f"Tanggal  : {datetime.now().strftime('%d-%m-%Y')}")

# Gunakan CalculationMethod.SINGAPORE
# Parameter: Fajr 20°, Isha 18° (Sama dengan Standar Kemenag RI / MABIMS)
# Catatan: Metode ini memiliki adjustment bawaan Dhuhr +1 menit.
# Maghrib default = Sunset (tanpa adjustment/ihtiyati tambahan).
params = CalculationParameters(method=CalculationMethod.SINGAPORE)

# OPSIONAL: Jika ingin menyamakan dengan jadwal cetak Kemenag (+2 menit ihtiyati):
# params.adjustments.fajr = 2
# params.adjustments.sunrise = 2 
# params.adjustments.dhuhr = 2     # Total jadi 1+2 = 3 menit
# params.adjustments.asr = 2
# params.adjustments.maghrib = 2
# params.adjustments.isha = 2

# Hitung waktu sholat
# PrayerTimes membutuhkan (coords, date, params, timezone)
pt = PrayerTimes(
    coordinates=(LATITUDE, LONGITUDE),
    date=datetime.now(),
    calculation_parameters=params,
    time_zone=ZoneInfo(TZ_NAME)
)

print(f"Metode   : SINGAPORE (Fajr 20°, Isha 18°) -> Standar Kemenag/MABIMS")
print(f"Info     : Waktu Maghrib adalah Sunset astronomis murni (18:22)") 
print("-" * 60)

def fmt(dt):
    return dt.strftime("%H:%M")

print(f"Fajr      : {fmt(pt.fajr)}")
print(f"Sunrise   : {fmt(pt.sunrise)}")
print(f"Dhuhr     : {fmt(pt.dhuhr)}")
print(f"Asr       : {fmt(pt.asr)}")
print(f"Maghrib   : {fmt(pt.maghrib)}")
print(f"Isha      : {fmt(pt.isha)}")
