"""Core admin/panel URLs."""
from django.urls import path
from . import user_admin, views

app_name = 'panel'

urlpatterns = [
    path('', views.PanelDashboardView.as_view(), name='dashboard'),
    path('login/', views.PanelLoginView.as_view(), name='login'),
    path('logout/', views.PanelLogoutView.as_view(), name='logout'),
    path('pengaturan/', views.PanelSiteSettingView.as_view(), name='site_setting'),
    path('pengguna/', user_admin.PanelUserList.as_view(), name='user_list'),
    path('pengguna/tambah/', user_admin.PanelUserCreate.as_view(), name='user_create'),
    path('pengguna/<int:pk>/ubah/', user_admin.PanelUserUpdate.as_view(), name='user_edit'),
]
