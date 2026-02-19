from django.utils import timezone
from .utils import get_prayer_times

def sholat_today(request):
    """
    Inject jadwal sholat hari ini ke semua template.
    Source: AdhanPy Calculation (SholatSettings)
    """
    try:
        today = timezone.localdate()
    except Exception:
        today = timezone.now().date()
        
    jadwal = None
    # Calculate dynamically using utils
    try:
        pt = get_prayer_times(today)
        if pt:
            # Return object-like for template (using datetime objects)
            jadwal = {
                'subuh': pt.fajr,
                'terbit': pt.sunrise, 
                'dzuhur': pt.dhuhr,
                'ashar': pt.asr,
                'maghrib': pt.maghrib,
                'isya': pt.isha,
            }
    except Exception:
        jadwal = None
        
    return {'jadwal_hari_ini': jadwal}
