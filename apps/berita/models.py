"""Berita & Pengumuman models."""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse


class KategoriBerita(models.Model):
    nama = models.CharField(_('Nama Kategori'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, blank=True)

    class Meta:
        verbose_name = _('Kategori Berita')
        verbose_name_plural = _('Kategori Berita')
        ordering = ['nama']

    def __str__(self):
        return self.nama

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nama)
        super().save(*args, **kwargs)


class Berita(models.Model):
    judul = models.CharField(_('Judul'), max_length=300)
    slug = models.SlugField(_('Slug'), unique=True, blank=True, max_length=350)
    kategori = models.ForeignKey(
        KategoriBerita, on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('Kategori')
    )
    isi = models.TextField(_('Isi'))
    gambar = models.ImageField(_('Gambar'), upload_to='berita/', blank=True, null=True)
    is_published = models.BooleanField(_('Dipublikasikan'), default=False)
    is_pengumuman = models.BooleanField(_('Pengumuman'), default=False)
    created_at = models.DateTimeField(_('Dibuat'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Diperbarui'), auto_now=True)

    class Meta:
        verbose_name = _('Berita')
        verbose_name_plural = _('Berita')
        ordering = ['-created_at']

    def __str__(self):
        return self.judul

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.judul)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('berita:detail', kwargs={'slug': self.slug})
