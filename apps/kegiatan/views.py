"""Kegiatan views — public and admin panel."""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from apps.core.mixins import (
    PublicListView, PublicDetailView,
    PanelListView, PanelCreateView, PanelUpdateView, PanelDeleteView
)
from .models import Kegiatan
from .forms import KegiatanForm


# ─── Public Views ────────────────────────────────────────────────────────────

class KegiatanListView(PublicListView):
    model = Kegiatan
    template_name = 'public/kegiatan_list.html'
    context_object_name = 'kegiatan_list'
    page_title = _('Kegiatan & Agenda')

    def get_queryset(self):
        qs = Kegiatan.objects.all()
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs


class KegiatanDetailView(PublicDetailView):
    model = Kegiatan
    template_name = 'public/kegiatan_detail.html'


# ─── Panel Views ─────────────────────────────────────────────────────────────

class PanelKegiatanList(PanelListView):
    model = Kegiatan
    template_name = 'panel/kegiatan/list.html'
    page_title = _('Manajemen Kegiatan')
    create_url = reverse_lazy('kegiatan:panel_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['judul', 'tempat']


class PanelKegiatanCreate(PanelCreateView):
    model = Kegiatan
    form_class = KegiatanForm
    page_title = _('Tambah Kegiatan')
    form_title = _('Tambah Kegiatan Baru')
    back_url = reverse_lazy('kegiatan:panel_list')
    success_url = reverse_lazy('kegiatan:panel_list')


class PanelKegiatanUpdate(PanelUpdateView):
    model = Kegiatan
    form_class = KegiatanForm
    page_title = _('Edit Kegiatan')
    form_title = _('Edit Kegiatan')
    back_url = reverse_lazy('kegiatan:panel_list')
    success_url = reverse_lazy('kegiatan:panel_list')


class PanelKegiatanDelete(PanelDeleteView):
    model = Kegiatan
    page_title = _('Hapus Kegiatan')
    back_url = reverse_lazy('kegiatan:panel_list')
    success_url = reverse_lazy('kegiatan:panel_list')
