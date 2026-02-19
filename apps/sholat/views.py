"""Sholat views — public and admin panel."""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
import datetime

from apps.core.mixins import (
    PublicListView, PanelListView,
    PanelCreateView, PanelUpdateView, PanelDeleteView
)
from .models import JadwalJumat, SholatSettings
from .forms import JadwalJumatForm, SholatSettingsForm


# ─── Public Views ────────────────────────────────────────────────────────────

class JadwalSholatPublicView(TemplateView):
    template_name = 'public/sholat.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Jadwal Sholat')
        today = datetime.date.today()
        from apps.sholat.utils import get_prayer_times
        import calendar
        
        # Today's prayer times
        pt_today = get_prayer_times(today)
        if pt_today:
            context['jadwal_hari_ini'] = {
                'tanggal': today,
                'subuh': pt_today.fajr,
                'terbit': pt_today.sunrise,
                'dzuhur': pt_today.dhuhr,
                'ashar': pt_today.asr,
                'maghrib': pt_today.maghrib,
                'isya': pt_today.isha,
            }
        
        # Monthly schedule
        month_schedule = []
        __, num_days = calendar.monthrange(today.year, today.month)
        for d in range(1, num_days + 1):
             curr_date = datetime.date(today.year, today.month, d)
             pt = get_prayer_times(curr_date)
             if pt:
                 month_schedule.append({
                     'tanggal': curr_date,
                     'subuh': pt.fajr,
                     'terbit': pt.sunrise,
                     'dzuhur': pt.dhuhr,
                     'ashar': pt.asr,
                     'maghrib': pt.maghrib,
                     'isya': pt.isha
                 })

        context['jadwal_bulan_ini'] = month_schedule
        context['jadwal_jumat'] = JadwalJumat.objects.order_by('-tanggal')[:5]
        return context


class JadwalSholatPrintView(JadwalSholatPublicView):
    template_name = 'public/sholat_print.html'


# ─── Panel Views ─────────────────────────────────────────────────────────────


# ─── Panel Views ─────────────────────────────────────────────────────────────

class PanelSholatSettingsView(PanelUpdateView):
    model = SholatSettings
    form_class = SholatSettingsForm
    page_title = _('Pengaturan Sholat')
    form_title = _('Konfigurasi Sholat (AdhanPy)')
    back_url = reverse_lazy('panel:dashboard')
    success_url = reverse_lazy('sholat:panel_settings')

    def get_object(self, queryset=None):
        obj = SholatSettings.objects.first()
        if not obj:
            obj = SholatSettings.objects.create()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add prayer schedule preview for current month
        from .utils import get_prayer_times
        from datetime import date
        import calendar

        today = date.today()
        _, num_days = calendar.monthrange(today.year, today.month)
        
        jadwal_preview = []
        # Preview first 5 days + today + last day as sample, or just today
        preview_dates = [today]
        
        for d in preview_dates:
            pt = get_prayer_times(d)
            if pt:
                jadwal_preview.append({
                    'tanggal': d,
                    'subuh': pt.fajr,
                    'terbit': pt.sunrise,
                    'dzuhur': pt.dhuhr,
                    'ashar': pt.asr,
                    'maghrib': pt.maghrib,
                    'isya': pt.isha
                })
        
        context['jadwal_preview'] = jadwal_preview
        return context


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
