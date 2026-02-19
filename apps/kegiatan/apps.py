from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class KegiatanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.kegiatan'
    verbose_name = _('Kegiatan & Agenda')
