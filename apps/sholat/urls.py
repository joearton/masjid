"""Sholat URL patterns."""
from django.urls import path
from . import views

app_name = 'sholat'

urlpatterns = [
    # Public
    path('', views.JadwalSholatPublicView.as_view(), name='index'),
    path('cetak/', views.JadwalSholatPrintView.as_view(), name='print'),
    # Panel - Settings
    path('panel/settings/', views.PanelSholatSettingsView.as_view(), name='panel_settings'),
    # Panel - Jadwal Jumat (redirect panel index here or to settings)
    path('panel/', views.PanelJadwalJumatList.as_view(), name='panel_list'), 
    # Panel - Jadwal Jumat
    path('panel/jumat/', views.PanelJadwalJumatList.as_view(), name='panel_jumat_list'),
    path('panel/jumat/tambah/', views.PanelJadwalJumatCreate.as_view(), name='panel_jumat_create'),
    path('panel/jumat/<int:pk>/edit/', views.PanelJadwalJumatUpdate.as_view(), name='panel_jumat_edit'),
    path('panel/jumat/<int:pk>/hapus/', views.PanelJadwalJumatDelete.as_view(), name='panel_jumat_delete'),
]
