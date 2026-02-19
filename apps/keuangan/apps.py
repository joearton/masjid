from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class KeuanganConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.keuangan'
    verbose_name = _('Keuangan Masjid')
