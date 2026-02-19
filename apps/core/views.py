"""Core views — homepage and utility views."""

from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from apps.berita.models import Berita
from apps.kegiatan.models import Kegiatan
from apps.core.models import SiteSetting
from apps.core.forms import SiteSettingForm
from apps.donatur.forms import PublicDonaturForm
import datetime

class HomeView(TemplateView):
    template_name = 'public/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Beranda')
        context['berita_terbaru'] = Berita.objects.filter(
            is_published=True
        ).order_by('-created_at')[:3]
        context['kegiatan_mendatang'] = Kegiatan.objects.filter(
            tanggal__gte=datetime.date.today()
        ).order_by('tanggal')[:4]
        # context['jadwal_hari_ini'] is handled globally by context_processor
        context['donatur_form'] = PublicDonaturForm()
        return context



class PanelLoginView(LoginView):
    template_name = 'panel/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return settings.LOGIN_REDIRECT_URL

    def form_invalid(self, form):
        messages.error(self.request, _('Username atau password salah.'))
        return super().form_invalid(form)


class PanelLogoutView(LogoutView):
    next_page = '/'


class PanelDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Dashboard')
        context['total_berita'] = Berita.objects.count()
        context['total_kegiatan'] = Kegiatan.objects.count()
        context['kegiatan_mendatang'] = Kegiatan.objects.filter(
            tanggal__gte=datetime.date.today()
        ).order_by('tanggal')[:5]
        context['berita_terbaru'] = Berita.objects.order_by('-created_at')[:5]
        
        from apps.donatur.models import Donatur
        context['total_donatur'] = Donatur.objects.count()
        context['total_donatur_tetap'] = Donatur.objects.filter(tipe='tetap', status='aktif').count()

        return context


class PanelSiteSettingView(LoginRequiredMixin, UpdateView):
    """Panel view for editing the SiteSetting singleton."""
    template_name = 'panel/core/site_setting.html'
    form_class = SiteSettingForm
    success_url = '/panel/pengaturan/'

    def get_object(self, queryset=None):
        return SiteSetting.load()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Pengaturan Website')
        context['form_title'] = _('Pengaturan Tampilan Website')
        context['back_url'] = reverse_lazy('panel:dashboard')
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Pengaturan website berhasil disimpan.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Terjadi kesalahan. Periksa kembali form Anda.'))
        return super().form_invalid(form)
