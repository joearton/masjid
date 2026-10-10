"""
Django settings for masjid project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

# Muat file .env
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-32)!7*4pobcy0ajw^%p68!e)-6en%wg76lu9w)#ipz_2%(mb=q')

DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Third party
    'crispy_forms',
    'crispy_bootstrap5',
    'rest_framework',
    'drf_spectacular',
    # Local apps
    'apps.core',
    'apps.profil',
    'apps.sholat',
    'apps.kegiatan',
    'apps.berita',
    'apps.keuangan',
    'apps.display',
    'apps.donatur',
    'apps.mobile_api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.LoginThrottleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'masjid.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'apps.core.context_processors.site_settings',
                'apps.sholat.context_processors.sholat_today',
            ],
        },
    },
]

WSGI_APPLICATION = 'masjid.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'id'
TIME_ZONE = 'Asia/Jakarta'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('id', _('Indonesian')),
    ('en', _('English')),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

# Login/Logout
LOGIN_URL = '/panel/login/'
LOGIN_REDIRECT_URL = '/panel/'
LOGOUT_REDIRECT_URL = '/'

# HTTPS (situs di balik Cloudflare + OpenLiteSpeed; pengalihan http→https dilakukan Cloudflare)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get(
    'CSRF_TRUSTED_ORIGINS', 'https://masjid.umko.ac.id,https://sadhanattaqwa.umko.ac.id').split(',') if o.strip()]
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 0 if DEBUG else 60 * 60 * 24 * 30
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'apps': {'handlers': ['console'], 'level': 'INFO'}},
}

# API aplikasi MyUMKO (/api/mobile/v1/, apps/mobile_api). Satu-satunya pengaturan DRF global hanya
# kelas skema; autentikasi, renderer, batas laju, dan galat dipasang per kelas view (common.py).
REST_FRAMEWORK = {'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema'}
MOBILE_API_THROTTLE_RATES = {'mobile_anon': os.environ.get('MOBILE_API_THROTTLE_ANON', '300/min')}
MOBILE_API_CACHE_SECONDS = int(os.environ.get('MOBILE_API_CACHE_SECONDS', '300'))
MASJID_PUBLIC_URL = os.environ.get('MASJID_PUBLIC_URL', 'https://masjid.umko.ac.id')

# Site info (used in context processor)
SITE_NAME = 'Masjid Al-Ikhlas'
SITE_TAGLINE = 'Masjid yang Makmur dan Sejahtera'
