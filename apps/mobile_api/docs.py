"""Dokumentasi publik (Swagger UI, ReDoc, skema) dengan pengaturan skema API MyUMKO Masjid."""
from drf_spectacular.settings import patched_settings
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from .schema import SCHEMA_SETTINGS


class DocsAccessMixin:
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = []

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        with patched_settings(SCHEMA_SETTINGS):
            return super().get(request, *args, **kwargs)


class SchemaView(DocsAccessMixin, SpectacularAPIView):
    custom_settings = SCHEMA_SETTINGS
    urlconf = 'apps.mobile_api.schema_urls'


class SwaggerView(DocsAccessMixin, SpectacularSwaggerView):
    url_name = 'mobile_api:schema'
    title = SCHEMA_SETTINGS['TITLE']


class RedocView(DocsAccessMixin, SpectacularRedocView):
    url_name = 'mobile_api:schema'
    title = SCHEMA_SETTINGS['TITLE']
