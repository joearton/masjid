from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class BeritaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.berita'
    verbose_name = _('Berita & Pengumuman')
