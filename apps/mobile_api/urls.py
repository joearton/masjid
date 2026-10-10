"""API publik baca-saja Masjid UMKO untuk aplikasi MyUMKO, dipasang di /api/mobile/v1/."""
from django.urls import path, re_path

from . import docs, views
from .common import NotFoundView

app_name = 'mobile_api'

urlpatterns = [
    path('schema/', docs.SchemaView.as_view(), name='schema'),
    path('docs/', docs.SwaggerView.as_view(), name='docs'),
    path('redoc/', docs.RedocView.as_view(), name='redoc'),
    path('meta/', views.MetaView.as_view(), name='meta'),
    path('profil/', views.ProfilView.as_view(), name='profil'),
    path('sholat/', views.SholatView.as_view(), name='sholat'),
    path('sholat/bulan/', views.SholatBulanView.as_view(), name='sholat_bulan'),
    path('sholat/kota/', views.KotaView.as_view(), name='sholat_kota'),
    path('jumat/', views.JumatView.as_view(), name='jumat'),
    path('kegiatan/', views.KegiatanListView.as_view(), name='kegiatan'),
    path('kegiatan/<int:pk>/', views.KegiatanDetailView.as_view(), name='kegiatan_detail'),
    path('berita/', views.BeritaListView.as_view(), name='berita'),
    path('berita/kategori/', views.BeritaKategoriView.as_view(), name='berita_kategori'),
    path('berita/<str:slug>/', views.BeritaDetailView.as_view(), name='berita_detail'),
    path('keuangan/', views.KeuanganView.as_view(), name='keuangan'),
    re_path(r'^.*$', NotFoundView.as_view(), name='not_found'),
]
