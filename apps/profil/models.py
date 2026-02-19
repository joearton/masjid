"""Profil Masjid models."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class ProfilMasjid(models.Model):
    nama = models.CharField(_('Nama Masjid'), max_length=200)
    tagline = models.CharField(_('Tagline'), max_length=300, blank=True)
    sejarah = models.TextField(_('Sejarah'))
    visi = models.TextField(_('Visi'))
    misi = models.TextField(_('Misi'))
    alamat = models.TextField(_('Alamat'))
    telepon = models.CharField(_('Telepon'), max_length=20, blank=True)
    email = models.EmailField(_('Email'), blank=True)
    website = models.URLField(_('Website'), blank=True)
    foto = models.ImageField(_('Foto Masjid'), upload_to='profil/', blank=True, null=True)
    maps_embed = models.TextField(_('Google Maps Embed'), blank=True)
    
    created_at = models.DateTimeField(_('Dibuat'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diperbarui'), auto_now=True)

    class Meta:
        verbose_name = _('Profil Masjid')
        verbose_name_plural = _('Profil Masjid')

    def __str__(self):
        return self.nama


class PeriodePengurus(models.Model):
    nama = models.CharField(_('Nama Periode'), max_length=100, help_text="Contoh: Periode 2024-2029")
    tahun_mulai = models.IntegerField(_('Tahun Mulai'))
    tahun_selesai = models.IntegerField(_('Tahun Selesai'))
    aktif = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        verbose_name = _('Periode Pengurus')
        verbose_name_plural = _('Periode Pengurus')
        ordering = ['-tahun_mulai']

    def __str__(self):
        return self.nama


class Pengurus(models.Model):
    JABATAN_CHOICES = [
        ('ketua', _('Ketua')),
        ('wakil_ketua', _('Wakil Ketua')),
        ('sekretaris', _('Sekretaris')),
        ('bendahara', _('Bendahara')),
        ('anggota', _('Anggota')),
    ]

    periode = models.ForeignKey(PeriodePengurus, on_delete=models.SET_NULL, related_name='pengurus_list', null=True, blank=True, verbose_name=_('Periode'))
    nama = models.CharField(_('Nama'), max_length=200)
    jabatan = models.CharField(_('Jabatan'), max_length=50, choices=JABATAN_CHOICES)
    foto = models.ImageField(_('Foto'), upload_to='pengurus/', blank=True, null=True)
    urutan = models.PositiveIntegerField(_('Urutan'), default=0)
    aktif = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        verbose_name = _('Pengurus')
        verbose_name_plural = _('Pengurus')
        ordering = ['urutan', 'nama']

    def __str__(self):
        return f"{self.nama} - {self.get_jabatan_display()}"


class Fasilitas(models.Model):
    nama = models.CharField(_('Nama Fasilitas'), max_length=200)
    deskripsi = models.TextField(_('Deskripsi'), blank=True)
    icon = models.CharField(_('Icon (Bootstrap Icon class)'), max_length=100, default='bi-building')
    aktif = models.BooleanField(_('Aktif'), default=True)

    class Meta:
        verbose_name = _('Fasilitas')
        verbose_name_plural = _('Fasilitas')
        ordering = ['nama']

    def __str__(self):
        return self.nama
