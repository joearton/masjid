"""Keuangan Masjid models."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class KategoriKeuangan(models.Model):
    JENIS_CHOICES = [
        ('pemasukan', _('Pemasukan')),
        ('pengeluaran', _('Pengeluaran')),
    ]
    nama = models.CharField(_('Nama Kategori'), max_length=200)
    jenis = models.CharField(_('Jenis'), max_length=20, choices=JENIS_CHOICES)

    class Meta:
        verbose_name = _('Kategori Keuangan')
        verbose_name_plural = _('Kategori Keuangan')
        ordering = ['jenis', 'nama']

    def __str__(self):
        return f"{self.nama} ({self.get_jenis_display()})"


class TransaksiKeuangan(models.Model):
    tanggal = models.DateField(_('Tanggal'))
    kategori = models.ForeignKey(
        KategoriKeuangan, on_delete=models.PROTECT,
        verbose_name=_('Kategori')
    )
    keterangan = models.CharField(_('Keterangan'), max_length=500)
    jumlah = models.DecimalField(_('Jumlah (Rp)'), max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(_('Dibuat'), auto_now_add=True)

    class Meta:
        verbose_name = _('Transaksi Keuangan')
        verbose_name_plural = _('Transaksi Keuangan')
        ordering = ['-tanggal', '-created_at']

    def __str__(self):
        return f"{self.tanggal} - {self.keterangan} - Rp {self.jumlah:,.0f}"
