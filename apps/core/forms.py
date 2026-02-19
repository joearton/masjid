"""Core app forms."""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import SiteSetting


class SiteSettingForm(forms.ModelForm):
    """Form for editing the SiteSetting singleton."""

    class Meta:
        model = SiteSetting
        exclude = ['updated_at']
        widgets = {
            'tema': forms.Select(attrs={'class': 'form-select'}),
            'warna_primary': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'warna_accent': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'hero_style': forms.Select(attrs={'class': 'form-select'}),
            'hero_overlay_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'hero_overlay_opacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.05', 'min': '0', 'max': '1'}),
            'hero_judul': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_subjudul': forms.TextInput(attrs={'class': 'form-control'}),
            'hero_video_url': forms.URLInput(attrs={'class': 'form-control'}),
            'homepage_layout': forms.Select(attrs={'class': 'form-select'}),
            'footer_text': forms.TextInput(attrs={'class': 'form-control'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://facebook.com/...'}),
            'instagram_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://instagram.com/...'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://youtube.com/...'}),
            'tiktok_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://tiktok.com/...'}),
            'twitter_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://x.com/...'}),
            'donasi_teks': forms.TextInput(attrs={'class': 'form-control'}),
            'rekening_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'meta_description': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'google_analytics_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'G-XXXXXXXXXX'}),
            'maintenance_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'custom_css': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 6, 'placeholder': '/* CSS tambahan */'}),
            'custom_js': forms.Textarea(attrs={'class': 'form-control font-monospace', 'rows': 6, 'placeholder': '// JavaScript tambahan'}),
        }
