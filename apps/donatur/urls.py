from django.urls import path
from . import views

app_name = 'donatur'

urlpatterns = [
    # Panel URLs
    path('panel/list/', views.PanelDonaturList.as_view(), name='panel_list'),
    path('panel/create/', views.PanelDonaturCreate.as_view(), name='panel_create'),
    path('panel/<int:pk>/edit/', views.PanelDonaturUpdate.as_view(), name='panel_edit'),
    path('panel/<int:pk>/delete/', views.PanelDonaturDelete.as_view(), name='panel_delete'),
    
    # Public URLs
    path('register/', views.PublicDonaturRegisterView.as_view(), name='public_register'),
]
