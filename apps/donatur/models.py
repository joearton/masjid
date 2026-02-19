from django.db import models
from django.utils.translation import gettext_lazy as _

class Donatur(models.Model):
    TIPE_CHOICES = [
        ('tetap', _('Donatur Tetap')),
        ('tidak_tetap', _('Donatur Tidak Tetap')),
    ]
    
    STATUS_CHOICES = [
        ('aktif', _('Aktif')),
        ('nonaktif', _('Nonaktif')),
    ]

    nama = models.CharField(_('Nama Donatur'), max_length=200)
    tipe = models.CharField(_('Tipe Donatur'), max_length=20, choices=TIPE_CHOICES, default='tidak_tetap')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='aktif')
    
    # Detail Information
    alamat = models.TextField(_('Alamat'), blank=True, null=True)
    telepon = models.CharField(_('No. Telepon/WA'), max_length=20, blank=True, null=True)
    
    # Commitment for Regular Donors
    komitmen_rutin = models.DecimalField(_('Komitmen Rutin (Rp)'), max_digits=12, decimal_places=0, default=0, help_text=_("Jumlah donasi rutin (jika donatur tetap)"))
    tipe_rutin = models.CharField(_('Periode Rutin'), max_length=20, choices=[('bulanan', 'Bulanan'), ('mingguan', 'Mingguan'), ('tahunan', 'Tahunan')], default='bulanan', blank=True, null=True)
    
    keterangan = models.TextField(_('Keterangan Tambahan'), blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Donatur')
        verbose_name_plural = _('Data Donatur')
        ordering = ['nama']

    def __str__(self):
        return f"{self.nama} ({self.get_tipe_display()})"
