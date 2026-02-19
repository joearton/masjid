"""Core admin configuration."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    """Admin for the singleton SiteSetting model."""

    fieldsets = (
        (_('Tema & Warna'), {
            'fields': ('tema', 'warna_primary', 'warna_accent'),
        }),
        (_('Hero Section'), {
            'fields': (
                'hero_style', 'hero_overlay_color', 'hero_overlay_opacity',
                'hero_gambar', 'hero_video_url',
                'hero_judul', 'hero_subjudul',
            ),
        }),
        (_('Layout Homepage'), {
            'fields': ('homepage_layout',),
        }),
        (_('Navbar & Logo'), {
            'fields': ('tampilkan_logo', 'logo', 'favicon'),
        }),
        (_('Footer'), {
            'fields': ('footer_text', 'footer_show_social'),
        }),
        (_('Sosial Media'), {
            'fields': (
                'facebook_url', 'instagram_url', 'youtube_url',
                'tiktok_url', 'twitter_url',
            ),
        }),
        (_('Fitur Beranda'), {
            'fields': (
                'tampilkan_jadwal_sholat', 'tampilkan_kegiatan',
                'tampilkan_berita', 'tampilkan_keuangan',
                'tampilkan_donasi',
            ),
        }),
        (_('Donasi'), {
            'fields': ('donasi_teks', 'rekening_info', 'qris_image'),
            'classes': ('collapse',),
        }),
        (_('SEO & Meta'), {
            'fields': ('meta_description', 'meta_keywords', 'google_analytics_id'),
            'classes': ('collapse',),
        }),
        (_('Lanjutan'), {
            'fields': (
                'maintenance_mode', 'maintenance_message',
                'custom_css', 'custom_js',
            ),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        """Only allow one instance."""
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion."""
        return False
