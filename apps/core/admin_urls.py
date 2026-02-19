"""Core admin/panel URLs."""
from django.urls import path
from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.PanelDashboardView.as_view(), name='dashboard'),
    path('login/', views.PanelLoginView.as_view(), name='login'),
    path('logout/', views.PanelLogoutView.as_view(), name='logout'),
    path('pengaturan/', views.PanelSiteSettingView.as_view(), name='site_setting'),
]
