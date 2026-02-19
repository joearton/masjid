from django.contrib import admin
from .models import SholatSettings, JadwalJumat

@admin.register(SholatSettings)
class SholatSettingsAdmin(admin.ModelAdmin):
    list_display = ('latitude', 'longitude', 'timezone', 'updated_at')
    
@admin.register(JadwalJumat)
class JadwalJumatAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'khatib', 'imam', 'tema')
    ordering = ('-tanggal',)
