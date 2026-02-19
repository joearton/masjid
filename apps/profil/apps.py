from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ProfilConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profil'
    verbose_name = _('Profil Masjid')
