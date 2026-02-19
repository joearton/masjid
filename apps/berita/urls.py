"""Berita URL patterns."""
from django.urls import path
from . import views

app_name = 'berita'

urlpatterns = [
    # Panel (harus di atas <slug:slug>/ agar tidak tertangkap sebagai slug)
    path('panel/', views.PanelBeritaList.as_view(), name='panel_list'),
    path('panel/tambah/', views.PanelBeritaCreate.as_view(), name='panel_create'),
    path('panel/<int:pk>/edit/', views.PanelBeritaUpdate.as_view(), name='panel_edit'),
    path('panel/<int:pk>/hapus/', views.PanelBeritaDelete.as_view(), name='panel_delete'),
    path('panel/kategori/', views.PanelKategoriList.as_view(), name='panel_kategori_list'),
    path('panel/kategori/tambah/', views.PanelKategoriCreate.as_view(), name='panel_kategori_create'),
    path('panel/kategori/<int:pk>/edit/', views.PanelKategoriUpdate.as_view(), name='panel_kategori_edit'),
    path('panel/kategori/<int:pk>/hapus/', views.PanelKategoriDelete.as_view(), name='panel_kategori_delete'),
    # Public
    path('', views.BeritaListView.as_view(), name='list'),
    path('<slug:slug>/', views.BeritaDetailView.as_view(), name='detail'),
]
