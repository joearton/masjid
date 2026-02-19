"""Berita views — public and admin panel."""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import (
    PublicListView, PublicDetailView,
    PanelListView, PanelCreateView, PanelUpdateView, PanelDeleteView
)
from .models import Berita, KategoriBerita
from .forms import BeritaForm, KategoriBeritaForm


# ─── Public Views ────────────────────────────────────────────────────────────

class BeritaListView(PublicListView):
    model = Berita
    template_name = 'public/berita_list.html'
    context_object_name = 'berita_list'
    page_title = _('Berita & Pengumuman')

    def get_queryset(self):
        qs = Berita.objects.filter(is_published=True)
        kategori = self.request.GET.get('kategori')
        tipe = self.request.GET.get('tipe')
        if kategori:
            qs = qs.filter(kategori__slug=kategori)
        if tipe == 'pengumuman':
            qs = qs.filter(is_pengumuman=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kategori_list'] = KategoriBerita.objects.all()
        return context


class BeritaDetailView(PublicDetailView):
    model = Berita
    template_name = 'public/berita_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Berita.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['berita_terkait'] = Berita.objects.filter(
            is_published=True,
            kategori=self.object.kategori
        ).exclude(pk=self.object.pk)[:3]
        return context


# ─── Panel Views ─────────────────────────────────────────────────────────────

class PanelBeritaList(PanelListView):
    model = Berita
    template_name = 'panel/berita/list.html'
    page_title = _('Manajemen Berita')
    create_url = reverse_lazy('berita:panel_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['judul', 'konten']


class PanelBeritaCreate(PanelCreateView):
    model = Berita
    form_class = BeritaForm
    page_title = _('Tambah Berita')
    form_title = _('Tambah Berita Baru')
    back_url = reverse_lazy('berita:panel_list')
    success_url = reverse_lazy('berita:panel_list')


class PanelBeritaUpdate(PanelUpdateView):
    model = Berita
    form_class = BeritaForm
    page_title = _('Edit Berita')
    form_title = _('Edit Berita')
    back_url = reverse_lazy('berita:panel_list')
    success_url = reverse_lazy('berita:panel_list')


class PanelBeritaDelete(PanelDeleteView):
    model = Berita
    page_title = _('Hapus Berita')
    back_url = reverse_lazy('berita:panel_list')
    success_url = reverse_lazy('berita:panel_list')


class PanelKategoriList(PanelListView):
    model = KategoriBerita
    template_name = 'panel/berita/kategori_list.html'
    page_title = _('Kategori Berita')
    create_url = reverse_lazy('berita:panel_kategori_create')
    back_url = reverse_lazy('berita:panel_list')
    search_fields = ['nama']


class PanelKategoriCreate(PanelCreateView):
    model = KategoriBerita
    form_class = KategoriBeritaForm
    page_title = _('Tambah Kategori')
    form_title = _('Tambah Kategori Berita')
    back_url = reverse_lazy('berita:panel_kategori_list')
    success_url = reverse_lazy('berita:panel_kategori_list')


class PanelKategoriUpdate(PanelUpdateView):
    model = KategoriBerita
    form_class = KategoriBeritaForm
    page_title = _('Edit Kategori')
    form_title = _('Edit Kategori Berita')
    back_url = reverse_lazy('berita:panel_kategori_list')
    success_url = reverse_lazy('berita:panel_kategori_list')


class PanelKategoriDelete(PanelDeleteView):
    model = KategoriBerita
    page_title = _('Hapus Kategori')
    back_url = reverse_lazy('berita:panel_kategori_list')
    success_url = reverse_lazy('berita:panel_kategori_list')
