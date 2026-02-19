import adhanpy
from adhanpy.calculation.CalculationMethod import CalculationMethod
from adhanpy.calculation.CalculationParameters import CalculationParameters
from adhanpy.PrayerTimes import PrayerTimes
from datetime import datetime, date
from zoneinfo import ZoneInfo
from .models import SholatSettings

def get_prayer_times(target_date=None):
    """
    Menghitung waktu sholat berdasarkan konfigurasi SholatSettings.
    """
    if target_date is None:
        target_date = date.today()
        
    settings = SholatSettings.objects.first()
    
    # Default values
    latitude = -6.2088
    longitude = 106.8456
    timezone = 'Asia/Jakarta'
    fajr_adj = 2
    dhuhr_adj = 2
    asr_adj = 2
    maghrib_adj = 2
    isha_adj = 2

    if settings:
        latitude = settings.latitude
        longitude = settings.longitude
        timezone = settings.timezone
        fajr_adj = settings.koreksi_subuh
        dhuhr_adj = settings.koreksi_dzuhur
        asr_adj = settings.koreksi_ashar
        maghrib_adj = settings.koreksi_maghrib
        isha_adj = settings.koreksi_isya

    # Setup Calculation Parameters (Using Singapore method as per user preference/standard)
    params = CalculationParameters(method=CalculationMethod.SINGAPORE)
    
    # Apply adjustments manually
    params.adjustments.fajr = fajr_adj
    params.adjustments.sunrise = 2 
    params.adjustments.dhuhr = dhuhr_adj
    params.adjustments.asr = asr_adj
    params.adjustments.maghrib = maghrib_adj
    params.adjustments.isha = isha_adj

    # Calculate
    try:
        pt = PrayerTimes(
            coordinates=(latitude, longitude),
            date=target_date,
            calculation_parameters=params,
            time_zone=ZoneInfo(timezone)
        )
        return pt
    except Exception as e:
        # Fallback or error logging
        print(f"Error calculating prayer times: {e}")
        return None
