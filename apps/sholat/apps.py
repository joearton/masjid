from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class SholatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sholat'
    verbose_name = _('Jadwal Sholat')
