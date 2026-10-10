"""Sholat views — public and admin panel."""
import datetime

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.core.mixins import (
    PanelListView, PanelCreateView, PanelUpdateView, PanelDeleteView,
)
from .models import JadwalJumat, SholatSettings
from .forms import JadwalJumatForm, SholatSettingsForm
from . import kemenag
from .utils import get_month_schedule, get_prayer_times, get_settings


# ─── Public Views ────────────────────────────────────────────────────────────

class JadwalSholatPublicView(TemplateView):
    template_name = 'public/sholat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Jadwal Sholat')
        today = timezone.localdate()
        settings = get_settings()
        month = get_month_schedule(today.year, today.month, settings)
        today_pt = next((pt for pt in month if pt.tanggal == today), None)
        context['jadwal_hari_ini'] = today_pt.as_dict() if today_pt else None
        context['jadwal_bulan_ini'] = [pt.as_dict() for pt in month]
        context['sumber_jadwal'] = 'kemenag' if month and all(pt.source == 'kemenag' for pt in month) else 'hisab'
        context['sholat_settings'] = settings
        context['jadwal_jumat'] = JadwalJumat.objects.order_by('-tanggal')[:5]
        return context


class JadwalSholatPrintView(JadwalSholatPublicView):
    template_name = 'public/sholat_print.html'


class PanelSholatSettingsView(PanelUpdateView):
    model = SholatSettings
    form_class = SholatSettingsForm
    page_title = _('Pengaturan Sholat')
    form_title = _('Sumber jadwal, lokasi, dan koreksi waktu')
    template_name = 'panel/sholat/settings.html'
    back_url = reverse_lazy('panel:dashboard')
    success_url = reverse_lazy('sholat:panel_settings')

    def get_object(self, queryset=None):
        obj = SholatSettings.objects.first()
        if not obj:
            obj = SholatSettings.objects.create()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.localdate()
        context['jadwal_preview'] = [
            get_prayer_times(today + datetime.timedelta(days=i), self.object).as_dict() for i in range(7)
        ]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        obj = self.object
        if obj.sumber == SholatSettings.SUMBER_KEMENAG:
            today = timezone.localdate()
            if not kemenag.fetch_month(obj.kota_kemenag_id, today.year, today.month, force=True):
                messages.warning(self.request, _('Jadwal resmi Kemenag belum dapat diambil; sementara memakai hisab dari koordinat masjid.'))
        return response


class PanelJadwalJumatList(PanelListView):
    model = JadwalJumat
    template_name = 'panel/sholat/jumat_list.html'
    page_title = _('Jadwal Jumat')
    create_url = reverse_lazy('sholat:panel_jumat_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['khatib', 'imam', 'tema']


class PanelJadwalJumatCreate(PanelCreateView):
    model = JadwalJumat
    form_class = JadwalJumatForm
    page_title = _('Tambah Jadwal Jumat')
    form_title = _('Tambah Jadwal Jumat')
    back_url = reverse_lazy('sholat:panel_jumat_list')
    success_url = reverse_lazy('sholat:panel_jumat_list')


class PanelJadwalJumatUpdate(PanelUpdateView):
    model = JadwalJumat
    form_class = JadwalJumatForm
    page_title = _('Edit Jadwal Jumat')
    form_title = _('Edit Jadwal Jumat')
    back_url = reverse_lazy('sholat:panel_jumat_list')
    success_url = reverse_lazy('sholat:panel_jumat_list')


class PanelJadwalJumatDelete(PanelDeleteView):
    model = JadwalJumat
    page_title = _('Hapus Jadwal Jumat')
    back_url = reverse_lazy('sholat:panel_jumat_list')
    success_url = reverse_lazy('sholat:panel_jumat_list')
