"""Pengaturan khusus pengujian: DB di memori dan media sementara, tidak menyentuh data produksi."""
import tempfile

from .settings import *  # noqa: F401,F403

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
MEDIA_ROOT = tempfile.mkdtemp(prefix='masjid-test-media-')
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'masjid-test'}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost']
