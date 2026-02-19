from django.urls import path
from .views import (
    DisplayView, DisplayUpdateAPIView,
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
    
    # Legacy/Shortcut for compatibility if needed (can be removed or redirected)
    # path('panel/settings/', PanelDisplaySettingsList.as_view(), name='panel_settings'), 
]
