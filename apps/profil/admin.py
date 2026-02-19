from django.contrib import admin
from .models import ProfilMasjid, Pengurus, Fasilitas, PeriodePengurus

@admin.register(ProfilMasjid)
class ProfilMasjidAdmin(admin.ModelAdmin):
    list_display = ('nama', 'updated_at')
    fieldsets = (
        (None, {'fields': ('nama', 'tagline', 'foto', 'website', 'email', 'telepon', 'alamat', 'maps_embed')}),
        ('Konten', {'fields': ('sejarah', 'visi', 'misi')}),
    )

@admin.register(PeriodePengurus)
class PeriodePengurusAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tahun_mulai', 'tahun_selesai', 'aktif')
    list_editable = ('aktif',)
    ordering = ('-tahun_mulai',)

@admin.register(Pengurus)
class PengurusAdmin(admin.ModelAdmin):
    list_display = ('nama', 'jabatan', 'periode', 'urutan', 'aktif')
    list_editable = ('urutan', 'aktif')
    list_filter = ('jabatan', 'aktif', 'periode')
    search_fields = ('nama',)

@admin.register(Fasilitas)
class FasilitasAdmin(admin.ModelAdmin):
    list_display = ('nama', 'aktif')
    list_editable = ('aktif',)
    list_filter = ('aktif',)
