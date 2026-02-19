from django.db import models
from django.utils.translation import gettext_lazy as _

class DisplaySettings(models.Model):
    THEME_CHOICES = [
        ('default', _('Default (Hijau Masjid)')),
        ('blue', _('Biru Laut')),
        ('dark', _('Dark Mode (Monokrom)')),
        ('gold', _('Emas Elegan')),
        ('purple', _('Ungu Modern')),
        ('nature', _('Nuansa Alam (Coklat)')),
    ]
    
    LAYOUT_CHOICES = [
        ('classic', _('Classic (Jadwal Kiri, Slide Kanan)')),
        ('modern', _('Modern (Jadwal Bawah)')),
        ('sidebar_right', _('Sidebar Kanan')),
        ('full_slider', _('Full Slider (Jadwal Overlay)')),
        ('masjid_info', _('Fokus Info Masjid')),
        ('simple', _('Simple Minimalis')),
        ('big_clock', _('Jam Besar')),
    ]

    NOTIFICATION_CHOICES = [
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
    
    is_default = models.BooleanField(_('Default Display'), default=False, help_text=_('Jika dicentang, display ini akan muncul di URL /display/ tanpa ID'))
    aktif = models.BooleanField(_('Aktif'), default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Pengaturan Display')
        verbose_name_plural = _('Pengaturan Display')

    def __str__(self):
        return self.nama
        
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

    def __str__(self):
        return f"{self.judul} ({self.get_tipe_display()})"
