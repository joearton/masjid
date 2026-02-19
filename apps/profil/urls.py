"""Profil URL patterns."""
from django.urls import path
from . import views

app_name = 'profil'

urlpatterns = [
    # Public
    path('', views.ProfilPublicView.as_view(), name='index'),
    # Panel
    path('panel/', views.PanelProfilUpdateView.as_view(), name='panel_profil'),
    # Panel - Pengurus & Periode
    path('panel/pengurus/', views.PanelPengurusList.as_view(), name='panel_pengurus_list'),
    path('panel/pengurus/tambah/', views.PanelPengurusCreate.as_view(), name='panel_pengurus_create'),
    path('panel/pengurus/<int:pk>/edit/', views.PanelPengurusUpdate.as_view(), name='panel_pengurus_edit'),
    path('panel/pengurus/<int:pk>/hapus/', views.PanelPengurusDelete.as_view(), name='panel_pengurus_delete'),
    
    # Panel - Periode Pengurus
    path('panel/periode/', views.PanelPeriodePengurusList.as_view(), name='panel_periode_list'),
    path('panel/periode/tambah/', views.PanelPeriodePengurusCreate.as_view(), name='panel_periode_create'),
    path('panel/periode/<int:pk>/edit/', views.PanelPeriodePengurusUpdate.as_view(), name='panel_periode_edit'),
    path('panel/periode/<int:pk>/hapus/', views.PanelPeriodePengurusDelete.as_view(), name='panel_periode_delete'),
    path('panel/fasilitas/', views.PanelFasilitasList.as_view(), name='panel_fasilitas_list'),
    path('panel/fasilitas/tambah/', views.PanelFasilitasCreate.as_view(), name='panel_fasilitas_create'),
    path('panel/fasilitas/<int:pk>/edit/', views.PanelFasilitasUpdate.as_view(), name='panel_fasilitas_edit'),
    path('panel/fasilitas/<int:pk>/hapus/', views.PanelFasilitasDelete.as_view(), name='panel_fasilitas_delete'),
]
