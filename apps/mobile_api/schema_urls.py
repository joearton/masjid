"""Urlconf khusus pembuatan skema OpenAPI (path lengkap /api/mobile/v1/…)."""
from django.urls import include, path

urlpatterns = [path('api/mobile/v1/', include('apps.mobile_api.urls'))]
