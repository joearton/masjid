"""Kegiatan URL patterns."""
from django.urls import path
from . import views

app_name = 'kegiatan'

urlpatterns = [
    # Public
    path('', views.KegiatanListView.as_view(), name='list'),
    path('<int:pk>/', views.KegiatanDetailView.as_view(), name='detail'),
    # Panel
    path('panel/', views.PanelKegiatanList.as_view(), name='panel_list'),
    path('panel/tambah/', views.PanelKegiatanCreate.as_view(), name='panel_create'),
    path('panel/<int:pk>/edit/', views.PanelKegiatanUpdate.as_view(), name='panel_edit'),
    path('panel/<int:pk>/hapus/', views.PanelKegiatanDelete.as_view(), name='panel_delete'),
]
