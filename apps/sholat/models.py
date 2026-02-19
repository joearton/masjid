"""Jadwal Sholat models."""
from django.db import models
from django.utils.translation import gettext_lazy as _



class SholatSettings(models.Model):
    # Konfigurasi Lokasi & Jadwal Sholat
    latitude = models.FloatField(_('Latitude'), default=-6.2088)
    longitude = models.FloatField(_('Longitude'), default=106.8456)
    timezone = models.CharField(_('Zona Waktu'), max_length=50, default='Asia/Jakarta')
    
    # Koreksi Waktu (Menit)
    koreksi_subuh = models.IntegerField(_('Koreksi Subuh'), default=2)
    koreksi_dzuhur = models.IntegerField(_('Koreksi Dzuhur'), default=2)
    koreksi_ashar = models.IntegerField(_('Koreksi Ashar'), default=2)
    koreksi_maghrib = models.IntegerField(_('Koreksi Maghrib'), default=2)
    koreksi_isya = models.IntegerField(_('Koreksi Isya'), default=2)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Pengaturan Sholat')
        verbose_name_plural = _('Pengaturan Sholat')

    def __str__(self):
        return "Pengaturan Sholat"


class JadwalJumat(models.Model):
    tanggal = models.DateField(_('Tanggal'))
    khatib = models.CharField(_('Khatib'), max_length=200)
    imam = models.CharField(_('Imam'), max_length=200)
    tema = models.CharField(_('Tema Khutbah'), max_length=300, blank=True)

    class Meta:
        verbose_name = _('Jadwal Jumat')
        verbose_name_plural = _('Jadwal Jumat')
        ordering = ['-tanggal']

    def __str__(self):
        return f"Jumat {self.tanggal} - {self.khatib}"
