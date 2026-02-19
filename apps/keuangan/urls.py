"""Keuangan URL patterns."""
from django.urls import path
from . import views

app_name = 'keuangan'

urlpatterns = [
    # Public
    path('', views.KeuanganPublicView.as_view(), name='index'),
    # Panel - Transaksi
    path('panel/', views.PanelTransaksiList.as_view(), name='panel_list'),
    path('panel/report/', views.PanelKeuanganReport.as_view(), name='panel_report'),
    path('panel/tambah/', views.PanelTransaksiCreate.as_view(), name='panel_create'),
    path('panel/<int:pk>/edit/', views.PanelTransaksiUpdate.as_view(), name='panel_edit'),
    path('panel/<int:pk>/hapus/', views.PanelTransaksiDelete.as_view(), name='panel_delete'),
    # Panel - Kategori
    path('panel/kategori/', views.PanelKategoriKeuanganList.as_view(), name='panel_kategori_list'),
    path('panel/kategori/tambah/', views.PanelKategoriKeuanganCreate.as_view(), name='panel_kategori_create'),
    path('panel/kategori/<int:pk>/edit/', views.PanelKategoriKeuanganUpdate.as_view(), name='panel_kategori_edit'),
    path('panel/kategori/<int:pk>/hapus/', views.PanelKategoriKeuanganDelete.as_view(), name='panel_kategori_delete'),
]
