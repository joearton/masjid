"""Profil views — public and admin panel."""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.core.mixins import (
    PublicDetailView, PanelListView,
    PanelCreateView, PanelUpdateView, PanelDeleteView
)
from .models import ProfilMasjid, Pengurus, Fasilitas, PeriodePengurus
from .forms import ProfilMasjidForm, PengurusForm, FasilitasForm, PeriodePengurusForm


# ─── Public Views ────────────────────────────────────────────────────────────

class ProfilPublicView(TemplateView):
    template_name = 'public/profil.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Profil Masjid')
        context['profil'] = ProfilMasjid.objects.first()
        
        # Get active period
        active_period = PeriodePengurus.objects.filter(aktif=True).first()
        context['periode'] = active_period
        
        if active_period:
            context['pengurus'] = Pengurus.objects.filter(aktif=True, periode=active_period).order_by('urutan')
        else:
            context['pengurus'] = Pengurus.objects.filter(aktif=True).order_by('urutan')
            
        context['fasilitas'] = Fasilitas.objects.filter(aktif=True)
        return context


# ─── Panel Views ─────────────────────────────────────────────────────────────

class PanelProfilUpdateView(PanelUpdateView):
    model = ProfilMasjid
    form_class = ProfilMasjidForm
    page_title = _('Profil Masjid')
    form_title = _('Edit Profil Masjid')
    back_url = reverse_lazy('panel:dashboard')
    success_url = reverse_lazy('profil:panel_profil')

    def get_object(self, queryset=None):
        obj, _ = ProfilMasjid.objects.get_or_create(
            pk=1, defaults={'nama': 'Masjid Al-Ikhlas', 'sejarah': '-', 'visi': '-', 'misi': '-', 'alamat': '-'}
        )
        return obj


class PanelPeriodePengurusList(PanelListView):
    model = PeriodePengurus
    template_name = 'panel/profil/periode_list.html'
    page_title = _('Periode Pengurus')
    create_url = reverse_lazy('profil:panel_periode_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['nama']

class PanelPeriodePengurusCreate(PanelCreateView):
    model = PeriodePengurus
    form_class = PeriodePengurusForm
    page_title = _('Tambah Periode')
    form_title = _('Tambah Periode Pengurus')
    back_url = reverse_lazy('profil:panel_periode_list')
    success_url = reverse_lazy('profil:panel_periode_list')

class PanelPeriodePengurusUpdate(PanelUpdateView):
    model = PeriodePengurus
    form_class = PeriodePengurusForm
    page_title = _('Edit Periode')
    form_title = _('Edit Periode Pengurus')
    back_url = reverse_lazy('profil:panel_periode_list')
    success_url = reverse_lazy('profil:panel_periode_list')

class PanelPeriodePengurusDelete(PanelDeleteView):
    model = PeriodePengurus
    page_title = _('Hapus Periode')
    back_url = reverse_lazy('profil:panel_periode_list')
    success_url = reverse_lazy('profil:panel_periode_list')


class PanelPengurusList(PanelListView):
    model = Pengurus
    template_name = 'panel/profil/pengurus_list.html'
    page_title = _('Pengurus Masjid')
    create_url = reverse_lazy('profil:panel_pengurus_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['nama']


class PanelPengurusCreate(PanelCreateView):
    model = Pengurus
    form_class = PengurusForm
    page_title = _('Tambah Pengurus')
    form_title = _('Tambah Pengurus Baru')
    back_url = reverse_lazy('profil:panel_pengurus_list')
    success_url = reverse_lazy('profil:panel_pengurus_list')


class PanelPengurusUpdate(PanelUpdateView):
    model = Pengurus
    form_class = PengurusForm
    page_title = _('Edit Pengurus')
    form_title = _('Edit Data Pengurus')
    back_url = reverse_lazy('profil:panel_pengurus_list')
    success_url = reverse_lazy('profil:panel_pengurus_list')


class PanelPengurusDelete(PanelDeleteView):
    model = Pengurus
    page_title = _('Hapus Pengurus')
    back_url = reverse_lazy('profil:panel_pengurus_list')
    success_url = reverse_lazy('profil:panel_pengurus_list')


class PanelFasilitasList(PanelListView):
    model = Fasilitas
    template_name = 'panel/profil/fasilitas_list.html'
    page_title = _('Fasilitas Masjid')
    create_url = reverse_lazy('profil:panel_fasilitas_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['nama']


class PanelFasilitasCreate(PanelCreateView):
    model = Fasilitas
    form_class = FasilitasForm
    page_title = _('Tambah Fasilitas')
    form_title = _('Tambah Fasilitas Baru')
    back_url = reverse_lazy('profil:panel_fasilitas_list')
    success_url = reverse_lazy('profil:panel_fasilitas_list')


class PanelFasilitasUpdate(PanelUpdateView):
    model = Fasilitas
    form_class = FasilitasForm
    page_title = _('Edit Fasilitas')
    form_title = _('Edit Fasilitas')
    back_url = reverse_lazy('profil:panel_fasilitas_list')
    success_url = reverse_lazy('profil:panel_fasilitas_list')


class PanelFasilitasDelete(PanelDeleteView):
    model = Fasilitas
    page_title = _('Hapus Fasilitas')
    back_url = reverse_lazy('profil:panel_fasilitas_list')
    success_url = reverse_lazy('profil:panel_fasilitas_list')
