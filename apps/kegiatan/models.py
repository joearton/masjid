"""Kegiatan & Agenda models."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Kegiatan(models.Model):
    STATUS_CHOICES = [
        ('upcoming', _('Akan Datang')),
        ('ongoing', _('Berlangsung')),
        ('done', _('Selesai')),
        ('cancelled', _('Dibatalkan')),
    ]

    judul = models.CharField(_('Judul Kegiatan'), max_length=300)
    deskripsi = models.TextField(_('Deskripsi'))
    tanggal = models.DateField(_('Tanggal'))
    waktu_mulai = models.TimeField(_('Waktu Mulai'))
    waktu_selesai = models.TimeField(_('Waktu Selesai'), blank=True, null=True)
    tempat = models.CharField(_('Tempat'), max_length=300)
    narasumber = models.CharField(_('Narasumber / Pemateri'), max_length=300, blank=True)
    gambar = models.ImageField(_('Gambar'), upload_to='kegiatan/', blank=True, null=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='upcoming')
    created_at = models.DateTimeField(_('Dibuat'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diperbarui'), auto_now=True)

    class Meta:
        verbose_name = _('Kegiatan')
        verbose_name_plural = _('Kegiatan')
        ordering = ['-tanggal']

    def __str__(self):
        return self.judul

    def get_absolute_url(self):
        return reverse('kegiatan:detail', kwargs={'pk': self.pk})
