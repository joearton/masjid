from django.contrib import admin
from .models import SholatSettings, JadwalJumat, JadwalSholatResmi

@admin.register(SholatSettings)
class SholatSettingsAdmin(admin.ModelAdmin):
    list_display = ('sumber', 'kota_kemenag_nama', 'latitude', 'longitude', 'timezone', 'updated_at')


@admin.register(JadwalSholatResmi)
class JadwalSholatResmiAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'kota_id', 'subuh', 'dzuhur', 'ashar', 'maghrib', 'isya', 'diambil')
    list_filter = ('kota_id',)
    date_hierarchy = 'tanggal'

    
@admin.register(JadwalJumat)
class JadwalJumatAdmin(admin.ModelAdmin):
    list_display = ('tanggal', 'khatib', 'imam', 'tema')
    ordering = ('-tanggal',)
