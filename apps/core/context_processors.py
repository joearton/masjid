"""Context processors for global template variables."""
from django.conf import settings
from apps.profil.models import ProfilMasjid
from apps.core.models import SiteSetting


def site_settings(request):
    """Inject site-wide settings into all templates."""
    profil = ProfilMasjid.objects.first()

    if profil:
        site_name = profil.nama
        site_tagline = profil.tagline
    else:
        site_name = getattr(settings, 'SITE_NAME', 'Masjid')
        site_tagline = getattr(settings, 'SITE_TAGLINE', '')

    # Load singleton SiteSetting
    try:
        site_setting = SiteSetting.load()
    except Exception:
        site_setting = None

    return {
        'SITE_NAME': site_name,
        'SITE_TAGLINE': site_tagline,
        'profil_masjid': profil,
        'site_setting': site_setting,
    }

