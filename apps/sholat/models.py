"""Jadwal Sholat models."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class SholatSettings(models.Model):
    SUMBER_KEMENAG = 'kemenag'
    SUMBER_HISAB = 'hisab'
    SUMBER_CHOICES = [
        (SUMBER_KEMENAG, _('Jadwal resmi Kemenag RI (otomatis, cadangan: hisab)')),
        (SUMBER_HISAB, _('Hisab dari koordinat masjid')),
    ]
    sumber = models.CharField(
        _('Sumber Jadwal'), max_length=10, choices=SUMBER_CHOICES, default=SUMBER_KEMENAG,
        help_text=_('Jadwal resmi Kemenag sama persis dengan jadwal yang diumumkan Kemenag untuk kabupaten/kota.'))
    kota_kemenag_id = models.CharField(
        _('Kode Kab/Kota Kemenag'), max_length=10, default='1002',
        help_text=_('Kode lokasi jadwal Kemenag. 1002 = Kab. Lampung Utara (Kotabumi).'))
    kota_kemenag_nama = models.CharField(_('Nama Kab/Kota'), max_length=100, default='KAB. LAMPUNG UTARA', blank=True)

    # Konfigurasi Lokasi (dipakai untuk hisab)
    latitude = models.FloatField(_('Latitude'), default=-4.82)
    longitude = models.FloatField(_('Longitude'), default=104.884)
    elevasi = models.FloatField(_('Ketinggian (m dpl)'), default=20)
    timezone = models.CharField(_('Zona Waktu'), max_length=50, default='Asia/Jakarta')
    ihtiyat = models.PositiveSmallIntegerField(
        _('Ihtiyat (menit)'), default=2,
        help_text=_('Waktu pengaman hisab. Kemenag memakai 2 menit.'))

    # Koreksi tambahan (menit), ditambahkan ke jadwal dari sumber mana pun
    koreksi_subuh = models.IntegerField(_('Koreksi Subuh'), default=0)
    koreksi_dzuhur = models.IntegerField(_('Koreksi Dzuhur'), default=0)
    koreksi_ashar = models.IntegerField(_('Koreksi Ashar'), default=0)
    koreksi_maghrib = models.IntegerField(_('Koreksi Maghrib'), default=0)
    koreksi_isya = models.IntegerField(_('Koreksi Isya'), default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Pengaturan Sholat')
        verbose_name_plural = _('Pengaturan Sholat')

    def __str__(self):
        return "Pengaturan Sholat"


class JadwalSholatResmi(models.Model):
    """Salinan jadwal resmi Kemenag per hari, diambil per bulan."""
    kota_id = models.CharField(max_length=10)
    tanggal = models.DateField()
    imsak = models.TimeField()
    subuh = models.TimeField()
    terbit = models.TimeField()
    dzuhur = models.TimeField()
    ashar = models.TimeField()
    maghrib = models.TimeField()
    isya = models.TimeField()
    diambil = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Jadwal Resmi Kemenag')
        verbose_name_plural = _('Jadwal Resmi Kemenag')
        constraints = [models.UniqueConstraint(fields=['kota_id', 'tanggal'], name='jadwal_resmi_unik')]
        ordering = ['tanggal']

    def __str__(self):
        return f"{self.kota_id} {self.tanggal}"


class KotaKemenag(models.Model):
    """Daftar kab/kota jadwal Kemenag (untuk jadwal sesuai lokasi pengguna)."""
    id = models.CharField(primary_key=True, max_length=10)
    nama = models.CharField(max_length=100)
    daerah = models.CharField(_('Provinsi'), max_length=100, blank=True)
    diperbarui = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Kab/Kota Kemenag')
        verbose_name_plural = _('Kab/Kota Kemenag')
        ordering = ['nama']

    def __str__(self):
        return f"{self.nama} ({self.id})"


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
