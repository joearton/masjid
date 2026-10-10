from django.db import models
from django.utils.translation import gettext_lazy as _

from . import catalog

class DisplaySettings(models.Model):
    THEME_CHOICES = catalog.THEME_CHOICES
    LAYOUT_CHOICES = catalog.LAYOUT_CHOICES

    NOTIFICATION_CHOICES = [
        ('sholat-lembut.wav', _('Lonceng Lembut')),
        ('notification-1.mp3', _('Notifikasi 1 (Soft)')),
        ('notification-2.mp3', _('Notifikasi 2 (Glass)')),
        ('notification-3.mp3', _('Notifikasi 3 (Bell)')),
        ('notification-4.mp3', _('Notifikasi 4 (Chime)')),
        ('', _('Tidak Ada Suara')),
    ]
    
    nama = models.CharField(_('Nama Setting'), max_length=100, default='Utama')
    tema = models.CharField(_('Tema Tampilan'), max_length=50, choices=THEME_CHOICES, default='default')
    layout = models.CharField(_('Layout Tampilan'), max_length=50, choices=LAYOUT_CHOICES, default='classic')
    running_text = models.TextField(_('Running Text'), help_text=_('Teks berjalan di bawah layar'), blank=True)
    video_url = models.URLField(_('URL Video Background'), blank=True, null=True, help_text=_('Opsional: Link video YouTube atau file video'))
    
    # Audio settings
    sholat_notification = models.CharField(_('Suara Masuk Sholat'), max_length=100, choices=NOTIFICATION_CHOICES, default='notification-1.mp3', blank=True)
    custom_notification = models.FileField(_('Upload Suara Custom'), upload_to='display/audio/', blank=True, null=True, help_text=_('Opsional: Upload file audio sendiri'))
    
    # Adzan, iqamah & sholat berjamaah (menit)
    peringatan_menit = models.PositiveSmallIntegerField(_('Peringatan menjelang adzan'), default=10, help_text=_('Menit sebelum adzan untuk menampilkan hitung mundur. 0 = nonaktif'))
    iqamah_subuh = models.PositiveSmallIntegerField(_('Iqamah Subuh'), default=10)
    iqamah_dzuhur = models.PositiveSmallIntegerField(_('Iqamah Dzuhur'), default=10)
    iqamah_ashar = models.PositiveSmallIntegerField(_('Iqamah Ashar'), default=10)
    iqamah_maghrib = models.PositiveSmallIntegerField(_('Iqamah Maghrib'), default=7)
    iqamah_isya = models.PositiveSmallIntegerField(_('Iqamah Isya'), default=10)
    durasi_sholat = models.PositiveSmallIntegerField(_('Layar sholat berlangsung'), default=10, help_text=_('Menit layar diredupkan setelah iqamah. 0 = nonaktif'))
    durasi_jumat = models.PositiveSmallIntegerField(_('Layar khutbah Jumat'), default=40, help_text=_('Menit layar khutbah sejak adzan Jumat. 0 = nonaktif'))
    tampilkan_imsak = models.BooleanField(_('Tampilkan Imsak'), default=False, help_text=_('Mis. selama Ramadan'))

    is_default = models.BooleanField(_('Default Display'), default=False, help_text=_('Jika dicentang, display ini akan muncul di URL /display/ tanpa ID'))
    aktif = models.BooleanField(_('Aktif'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Pengaturan Display')
        verbose_name_plural = _('Pengaturan Display')

    def __str__(self):
        return self.nama
        
    def iqamah_minutes(self):
        return {'Subuh': self.iqamah_subuh, 'Dzuhur': self.iqamah_dzuhur, 'Ashar': self.iqamah_ashar,
                'Maghrib': self.iqamah_maghrib, 'Isya': self.iqamah_isya}

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other displays to not default
            DisplaySettings.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class DisplaySlide(models.Model):
    TIPE_CHOICES = [
        ('sholat', _('Jadwal Sholat')),
        ('kas', _('Informasi Kas')),
        ('berita', _('Berita & Pengumuman')),
        ('kegiatan', _('Kegiatan Mendatang')),
        ('teks', _('Teks Kustom')),
        ('gambar', _('Gambar')),
        ('donasi', _('Info Donasi')),
        ('jumat', _('Petugas Jumat')),
    ]

    display = models.ForeignKey(DisplaySettings, on_delete=models.CASCADE, related_name='slides', verbose_name=_('Tampilan'), null=True, blank=True)
    judul = models.CharField(_('Judul Slide'), max_length=200)
    tipe = models.CharField(_('Tipe Konten'), max_length=50, choices=TIPE_CHOICES, default='teks')
    konten_teks = models.TextField(_('Konten Teks'), blank=True, help_text=_('Untuk tipe Teks Kustom'))
    gambar = models.ImageField(_('Gambar Slide'), upload_to='display/slides/', blank=True, null=True)
    durasi = models.PositiveIntegerField(_('Durasi (detik)'), default=15, help_text=_('Lama slide ditampilkan'))
    urutan = models.PositiveIntegerField(_('Urutan Tampil'), default=0)
    aktif = models.BooleanField(_('Aktif'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Slide Display')
        verbose_name_plural = _('Slide Display')
        ordering = ['urutan', 'updated_at']

    TIPE_IKON = {
        'sholat': 'bi-clock', 'kas': 'bi-wallet2', 'berita': 'bi-newspaper', 'kegiatan': 'bi-calendar-event',
        'teks': 'bi-fonts', 'gambar': 'bi-image', 'donasi': 'bi-heart', 'jumat': 'bi-mic',
    }

    @property
    def ikon(self):
        return self.TIPE_IKON.get(self.tipe, 'bi-card-text')

    def __str__(self):
        return f"{self.judul} ({self.get_tipe_display()})"
