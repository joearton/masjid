"""URL configuration for masjid project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('', include('apps.core.urls', namespace='core')),
    path('profil/', include('apps.profil.urls', namespace='profil')),
    path('sholat/', include('apps.sholat.urls', namespace='sholat')),
    path('kegiatan/', include('apps.kegiatan.urls', namespace='kegiatan')),
    path('berita/', include('apps.berita.urls', namespace='berita')),
    path('keuangan/', include('apps.keuangan.urls', namespace='keuangan')),
    path('panel/', include('apps.core.admin_urls', namespace='panel')),
    path('display/', include('apps.display.urls', namespace='display')),
    path('donatur/', include('apps.donatur.urls', namespace='donatur')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
