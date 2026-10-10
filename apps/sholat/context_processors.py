import logging

from .utils import get_prayer_times

logger = logging.getLogger(__name__)


def sholat_today(request):
    """Inject jadwal sholat hari ini ke semua template."""
    try:
        pt = get_prayer_times()
    except Exception:
        logger.exception('Gagal menyiapkan jadwal sholat hari ini')
        return {'jadwal_hari_ini': None}
    return {'jadwal_hari_ini': pt.as_dict()}
