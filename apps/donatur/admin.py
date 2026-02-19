from django.contrib import admin
from .models import Donatur

@admin.register(Donatur)
class DonaturAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tipe', 'status', 'telepon', 'updated_at')
    list_filter = ('tipe', 'status')
    search_fields = ('nama', 'alamat', 'telepon')
