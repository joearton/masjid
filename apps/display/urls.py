from django.urls import path

from . import views
from .views import (
    DisplayView, DisplayUpdateAPIView, MonitorVersionView,
    PanelDisplaySettingsList, PanelDisplaySettingsCreate,
    PanelDisplaySettingsUpdate, PanelDisplaySettingsDelete,
    PanelDisplaySlideList, PanelDisplaySlideCreate, 
    PanelDisplaySlideUpdate, PanelDisplaySlideDelete
)

app_name = 'display'

urlpatterns = [

    # Public Display
    path('', DisplayView.as_view(), name='index'),
    path('<int:pk>/', DisplayView.as_view(), name='detail'),
    path('versi/', MonitorVersionView.as_view(), name='versi'),
    path('<int:pk>/update/', DisplayUpdateAPIView.as_view(), name='api_update'),

    # Panel Display Settings
    path('panel/settings/', PanelDisplaySettingsList.as_view(), name='panel_settings_list'),
    path('panel/settings/create/', PanelDisplaySettingsCreate.as_view(), name='panel_settings_create'),
    path('panel/settings/<int:pk>/edit/', PanelDisplaySettingsUpdate.as_view(), name='panel_settings_edit'),
    path('panel/settings/<int:pk>/delete/', PanelDisplaySettingsDelete.as_view(), name='panel_settings_delete'),
    
    # Slide Management (Nested under Display ID)
    path('panel/settings/<int:display_pk>/slides/', PanelDisplaySlideList.as_view(), name='panel_slide_list'),
    path('panel/settings/<int:display_pk>/slides/create/', PanelDisplaySlideCreate.as_view(), name='panel_slide_create'),
    path('panel/settings/slides/<int:pk>/edit/', PanelDisplaySlideUpdate.as_view(), name='panel_slide_edit'),
    path('panel/settings/slides/<int:pk>/delete/', PanelDisplaySlideDelete.as_view(), name='panel_slide_delete'),
    
    # Editor AJAX
    path('panel/settings/<int:pk>/save/', views.ajax_display_save, name='ajax_display_save'),
    path('panel/settings/<int:pk>/duplicate/', views.ajax_display_duplicate, name='ajax_display_duplicate'),
    path('panel/settings/<int:display_pk>/slides/ajax/create/', views.ajax_slide_create, name='ajax_slide_create'),
    path('panel/settings/<int:display_pk>/slides/ajax/reorder/', views.ajax_slide_reorder, name='ajax_slide_reorder'),
    path('panel/settings/slides/<int:pk>/ajax/update/', views.ajax_slide_update, name='ajax_slide_update'),
    path('panel/settings/slides/<int:pk>/ajax/delete/', views.ajax_slide_delete, name='ajax_slide_delete'),
    path('panel/settings/slides/<int:pk>/ajax/duplicate/', views.ajax_slide_duplicate, name='ajax_slide_duplicate'),

    # Legacy/Shortcut for compatibility if needed (can be removed or redirected)
    # path('panel/settings/', PanelDisplaySettingsList.as_view(), name='panel_settings'), 
]
