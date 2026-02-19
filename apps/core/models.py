"""Core app models — Site-wide settings."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class SiteSetting(models.Model):
    """
    Singleton model untuk pengaturan tampilan website.
    Hanya satu instance yang digunakan — dipanggil via SiteSetting.load().
    """

    # ─── Tema & Warna ────────────────────────────────────────────
    THEME_CHOICES = [
        ('default', _('Default (Hijau)')),
        ('blue', _('Biru')),
        ('dark', _('Gelap')),
        ('maroon', _('Merah Marun')),
        ('teal', _('Teal')),
        ('purple', _('Ungu')),
    ]
    tema = models.CharField(
        _('Tema Website'), max_length=20,
        choices=THEME_CHOICES, default='default',
        help_text=_('Tema warna utama website.')
    )

    warna_primary = models.CharField(
        _('Warna Primary'), max_length=7, default='#1a6b3c',
        help_text=_('Kode warna HEX untuk warna utama. Contoh: #1a6b3c')
    )
    warna_accent = models.CharField(
        _('Warna Aksen'), max_length=7, default='#f0a500',
        help_text=_('Kode warna HEX untuk warna aksen/tombol CTA.')
    )

    # ─── Hero Section ────────────────────────────────────────────
    HERO_STYLE_CHOICES = [
        ('gradient', _('Gradient Overlay')),
        ('solid', _('Warna Solid')),
        ('image', _('Gambar Saja (tanpa overlay)')),
        ('video', _('Video Background')),
    ]
    hero_style = models.CharField(
        _('Gaya Hero Section'), max_length=20,
        choices=HERO_STYLE_CHOICES, default='gradient',
    )
    hero_overlay_color = models.CharField(
        _('Warna Overlay Hero'), max_length=7, default='#1a6b3c',
        help_text=_('Warna dasar untuk overlay hero (gradien).')
    )
    hero_overlay_opacity = models.FloatField(
        _('Opasitas Overlay Hero'), default=0.85,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Tingkat kegelapan overlay (0 = transparan, 1 = gelap penuh).')
    )
    hero_gambar = models.ImageField(
        _('Gambar Hero'), upload_to='hero/', blank=True, null=True,
        help_text=_('Gambar latar belakang hero section. Jika kosong, menggunakan foto masjid.')
    )
    hero_video_url = models.URLField(
        _('URL Video Hero'), blank=True,
        help_text=_('URL video untuk latar belakang hero (MP4).')
    )
    hero_judul = models.CharField(
        _('Judul Hero'), max_length=200, blank=True,
        help_text=_('Judul besar di hero section. Kosongkan untuk menggunakan nama masjid.')
    )
    hero_subjudul = models.CharField(
        _('Sub-Judul Hero'), max_length=300, blank=True,
        help_text=_('Sub-judul/tagline di hero section. Kosongkan untuk menggunakan tagline masjid.')
    )

    # ─── Template Homepage ───────────────────────────────────────
    HOMEPAGE_LAYOUT_CHOICES = [
        ('default', _('Default (Hero + Jadwal + Kegiatan + Berita)')),
        ('compact', _('Kompak (Hero kecil + Konten grid)')),
        ('fullscreen', _('Fullscreen Hero + Scroll Sections')),
        ('dashboard', _('Dashboard (Tanpa Hero, langsung info)')),
    ]
    homepage_layout = models.CharField(
        _('Layout Homepage'), max_length=20,
        choices=HOMEPAGE_LAYOUT_CHOICES, default='default',
        help_text=_('Pilih tata letak halaman utama.')
    )

    # ─── Navbar ──────────────────────────────────────────────────
    tampilkan_logo = models.BooleanField(
        _('Tampilkan Logo di Navbar'), default=True,
    )
    logo = models.ImageField(
        _('Logo Website'), upload_to='logo/', blank=True, null=True,
        help_text=_('Logo untuk navbar. Ukuran disarankan: 40×40 px.')
    )
    favicon = models.ImageField(
        _('Favicon'), upload_to='favicon/', blank=True, null=True,
        help_text=_('Ikon kecil untuk tab browser. Ukuran: 32×32 px.')
    )

    # ─── Footer ──────────────────────────────────────────────────
    footer_text = models.CharField(
        _('Teks Footer'), max_length=500, blank=True,
        help_text=_('Teks hak cipta di footer. Kosongkan untuk default.')
    )
    footer_show_social = models.BooleanField(
        _('Tampilkan Sosial Media di Footer'), default=True,
    )

    # ─── Sosial Media ────────────────────────────────────────────
    facebook_url = models.URLField(_('Facebook'), blank=True)
    instagram_url = models.URLField(_('Instagram'), blank=True)
    youtube_url = models.URLField(_('YouTube'), blank=True)
    tiktok_url = models.URLField(_('TikTok'), blank=True)
    twitter_url = models.URLField(_('Twitter/X'), blank=True)

    # ─── Fitur Tampilkan/Sembunyikan ─────────────────────────────
    tampilkan_jadwal_sholat = models.BooleanField(
        _('Tampilkan Jadwal Sholat di Beranda'), default=True,
    )
    tampilkan_kegiatan = models.BooleanField(
        _('Tampilkan Kegiatan di Beranda'), default=True,
    )
    tampilkan_berita = models.BooleanField(
        _('Tampilkan Berita di Beranda'), default=True,
    )
    tampilkan_keuangan = models.BooleanField(
        _('Tampilkan Link Keuangan di Menu'), default=True,
    )
    tampilkan_donasi = models.BooleanField(
        _('Tampilkan Tombol Donasi'), default=False,
    )

    # ─── Donasi / Rekening ───────────────────────────────────────
    donasi_teks = models.CharField(
        _('Teks Ajakan Donasi'), max_length=300, blank=True,
        default='Salurkan donasi terbaik Anda untuk masjid.',
    )
    rekening_info = models.TextField(
        _('Informasi Rekening'), blank=True,
        help_text=_('Informasi rekening bank untuk donasi (bisa pakai format HTML).')
    )
    qris_image = models.ImageField(
        _('QRIS/QR Code Donasi'), upload_to='donasi/', blank=True, null=True,
        help_text=_('Gambar QRIS untuk pembayaran donasi.')
    )

    # ─── Meta & SEO ──────────────────────────────────────────────
    meta_description = models.CharField(
        _('Meta Description'), max_length=300, blank=True,
        help_text=_('Deskripsi singkat website untuk SEO.')
    )
    meta_keywords = models.CharField(
        _('Meta Keywords'), max_length=500, blank=True,
        help_text=_('Kata kunci SEO, pisahkan dengan koma.')
    )
    google_analytics_id = models.CharField(
        _('Google Analytics ID'), max_length=50, blank=True,
        help_text=_('Contoh: G-XXXXXXXXXX')
    )

    # ─── Umum ────────────────────────────────────────────────────
    maintenance_mode = models.BooleanField(
        _('Mode Maintenance'), default=False,
        help_text=_('Tampilkan halaman maintenance ke publik.')
    )
    maintenance_message = models.TextField(
        _('Pesan Maintenance'), blank=True,
        default='Website sedang dalam perbaikan. Silakan kembali beberapa saat lagi.',
    )
    custom_css = models.TextField(
        _('Custom CSS'), blank=True,
        help_text=_('CSS tambahan yang akan di-inject ke semua halaman.')
    )
    custom_js = models.TextField(
        _('Custom JavaScript'), blank=True,
        help_text=_('JavaScript tambahan (tanpa tag script).')
    )

    updated_at = models.DateTimeField(_('Terakhir Diubah'), auto_now=True)

    class Meta:
        verbose_name = _('Pengaturan Website')
        verbose_name_plural = _('Pengaturan Website')

    def __str__(self):
        return 'Pengaturan Website'

    def save(self, *args, **kwargs):
        """Enforce singleton — always use pk=1."""
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton."""
        pass

    @classmethod
    def load(cls):
        """Load or create the singleton instance."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    # ─── Computed Properties ─────────────────────────────────────
    @property
    def hero_overlay_css(self):
        """Generate the CSS for the hero overlay based on settings."""
        color = self.hero_overlay_color
        opacity = self.hero_overlay_opacity
        # Convert hex to rgba
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        return f'rgba({r}, {g}, {b}, {opacity})'

    @property
    def hero_gradient_css(self):
        """Generate a gradient CSS string for the hero overlay."""
        color = self.hero_overlay_color
        opacity = self.hero_overlay_opacity
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        # Darker shade
        r2 = max(0, r - 30)
        g2 = max(0, g - 30)
        b2 = max(0, b - 30)
        return (
            f'linear-gradient(135deg, '
            f'rgba({r}, {g}, {b}, {opacity}) 0%, '
            f'rgba({r2}, {g2}, {b2}, {opacity - 0.05:.2f}) 50%, '
            f'rgba(26, 26, 46, {opacity}) 100%)'
        )

    @property
    def social_links(self):
        """Return a list of social media links for template iteration."""
        links = []
        if self.facebook_url:
            links.append({'name': 'Facebook', 'url': self.facebook_url, 'icon': 'bi-facebook'})
        if self.instagram_url:
            links.append({'name': 'Instagram', 'url': self.instagram_url, 'icon': 'bi-instagram'})
        if self.youtube_url:
            links.append({'name': 'YouTube', 'url': self.youtube_url, 'icon': 'bi-youtube'})
        if self.tiktok_url:
            links.append({'name': 'TikTok', 'url': self.tiktok_url, 'icon': 'bi-tiktok'})
        if self.twitter_url:
            links.append({'name': 'Twitter', 'url': self.twitter_url, 'icon': 'bi-twitter-x'})
        return links

    @property
    def css_variables(self):
        """Generate CSS custom properties from settings."""
        return (
            f'--primary: {self.warna_primary};'
            f'--primary-dark: {self.warna_primary_dark};'
            f'--accent: {self.warna_accent};'
        )

    @property
    def warna_primary_dark(self):
        """Compute a darker shade of primary color."""
        color = self.warna_primary
        try:
            r = max(0, int(color[1:3], 16) - 30)
            g = max(0, int(color[3:5], 16) - 30)
            b = max(0, int(color[5:7], 16) - 30)
            return f'#{r:02x}{g:02x}{b:02x}'
        except (ValueError, IndexError):
            return '#145530'
