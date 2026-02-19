from django.contrib import admin
from .models import DisplaySettings, DisplaySlide

@admin.register(DisplaySettings)
class DisplaySettingsAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tema', 'aktif', 'updated_at')
    list_filter = ('tema', 'aktif')
    search_fields = ('nama', 'running_text')

@admin.register(DisplaySlide)
class DisplaySlideAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tipe', 'urutan', 'durasi', 'aktif')
    list_editable = ('urutan', 'aktif')
    list_filter = ('tipe', 'aktif')
    search_fields = ('judul', 'konten_teks')
    ordering = ('urutan', 'updated_at')
