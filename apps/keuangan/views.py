"""Keuangan views — public and admin panel."""
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from django.db.models import Sum, Q
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import json

from apps.core.mixins import (
    PublicListView, PanelListView,
    PanelCreateView, PanelUpdateView, PanelDeleteView
)
from .models import TransaksiKeuangan, KategoriKeuangan
from .forms import TransaksiKeuanganForm, KategoriKeuanganForm


NAMA_BULAN = [
    '', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember',
]


# ─── Public Views ────────────────────────────────────────────────────────────

class KeuanganPublicView(TemplateView):
    template_name = 'public/keuangan.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Laporan Keuangan')
        today = datetime.date.today()
        bulan = int(self.request.GET.get('bulan', today.month))
        tahun = int(self.request.GET.get('tahun', today.year))

        transaksi = TransaksiKeuangan.objects.filter(
            tanggal__year=tahun, tanggal__month=bulan
        ).select_related('kategori').order_by('-tanggal')

        total_masuk = transaksi.filter(
            kategori__jenis='pemasukan'
        ).aggregate(total=Sum('jumlah'))['total'] or 0

        total_keluar = transaksi.filter(
            kategori__jenis='pengeluaran'
        ).aggregate(total=Sum('jumlah'))['total'] or 0

        context.update({
            'transaksi_list': transaksi,
            'total_masuk': total_masuk,
            'total_keluar': total_keluar,
            'saldo': total_masuk - total_keluar,
            'bulan': bulan,
            'tahun': tahun,
        })
        return context


# ─── Panel Views ─────────────────────────────────────────────────────────────

class PanelTransaksiList(PanelListView):
    model = TransaksiKeuangan
    template_name = 'panel/keuangan/list.html'
    page_title = _('Transaksi Keuangan')
    create_url = reverse_lazy('keuangan:panel_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['keterangan', 'kategori__nama']

    def get_queryset(self):
        qs = super().get_queryset().select_related('kategori').order_by('-tanggal')

        # Year/Month filter
        tahun = self.request.GET.get('tahun', '')
        bulan = self.request.GET.get('bulan', '')
        if tahun:
            try:
                qs = qs.filter(tanggal__year=int(tahun))
            except (ValueError, TypeError):
                pass
        if bulan:
            try:
                qs = qs.filter(tanggal__month=int(bulan))
            except (ValueError, TypeError):
                pass

        jenis = self.request.GET.get('jenis', '')
        if jenis in ('pemasukan', 'pengeluaran'):
            qs = qs.filter(kategori__jenis=jenis)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Compute totals from FULL queryset (before pagination)
        full_qs = self.get_queryset()
        total_masuk = full_qs.filter(kategori__jenis='pemasukan').aggregate(t=Sum('jumlah'))['t'] or 0
        total_keluar = full_qs.filter(kategori__jenis='pengeluaran').aggregate(t=Sum('jumlah'))['t'] or 0
        context['total_masuk'] = total_masuk
        context['total_keluar'] = total_keluar
        context['saldo'] = total_masuk - total_keluar
        context['selected_jenis'] = self.request.GET.get('jenis', '')

        # Year & Month filter context
        today = datetime.date.today()
        selected_tahun = self.request.GET.get('tahun', '')
        selected_bulan = self.request.GET.get('bulan', '')
        context['selected_tahun'] = selected_tahun
        context['selected_bulan'] = selected_bulan

        # Available years (from earliest transaction to current year)
        years = TransaksiKeuangan.objects.dates('tanggal', 'year', order='DESC')
        year_list = sorted(set([d.year for d in years] + [today.year]), reverse=True)
        context['year_list'] = year_list

        # Month names
        context['bulan_choices'] = [(i, NAMA_BULAN[i]) for i in range(1, 13)]

        return context


class PanelTransaksiCreate(PanelCreateView):
    model = TransaksiKeuangan
    form_class = TransaksiKeuanganForm
    page_title = _('Tambah Transaksi')
    form_title = _('Tambah Transaksi Keuangan')
    back_url = reverse_lazy('keuangan:panel_list')
    success_url = reverse_lazy('keuangan:panel_list')


class PanelTransaksiUpdate(PanelUpdateView):
    model = TransaksiKeuangan
    form_class = TransaksiKeuanganForm
    page_title = _('Edit Transaksi')
    form_title = _('Edit Transaksi Keuangan')
    back_url = reverse_lazy('keuangan:panel_list')
    success_url = reverse_lazy('keuangan:panel_list')


class PanelTransaksiDelete(PanelDeleteView):
    model = TransaksiKeuangan
    page_title = _('Hapus Transaksi')
    back_url = reverse_lazy('keuangan:panel_list')
    success_url = reverse_lazy('keuangan:panel_list')


# ─── Report View ─────────────────────────────────────────────────────────────

class PanelKeuanganReport(LoginRequiredMixin, TemplateView):
    template_name = 'panel/keuangan/report.html'
    login_url = '/panel/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Laporan Keuangan')

        today = datetime.date.today()
        try:
            tahun = int(self.request.GET.get('tahun', today.year))
        except (ValueError, TypeError):
            tahun = today.year

        context['selected_tahun'] = tahun

        # Available years
        years = TransaksiKeuangan.objects.dates('tanggal', 'year', order='DESC')
        year_list = sorted(set([d.year for d in years] + [today.year]), reverse=True)
        context['year_list'] = year_list

        # ── Monthly pemasukan & pengeluaran for bar chart ──
        monthly_masuk = []
        monthly_keluar = []
        monthly_labels = []
        for m in range(1, 13):
            monthly_labels.append(NAMA_BULAN[m][:3])
            masuk = TransaksiKeuangan.objects.filter(
                tanggal__year=tahun, tanggal__month=m,
                kategori__jenis='pemasukan'
            ).aggregate(t=Sum('jumlah'))['t'] or 0
            keluar = TransaksiKeuangan.objects.filter(
                tanggal__year=tahun, tanggal__month=m,
                kategori__jenis='pengeluaran'
            ).aggregate(t=Sum('jumlah'))['t'] or 0
            monthly_masuk.append(float(masuk))
            monthly_keluar.append(float(keluar))

        context['chart_labels'] = json.dumps(monthly_labels)
        context['chart_masuk'] = json.dumps(monthly_masuk)
        context['chart_keluar'] = json.dumps(monthly_keluar)

        # ── Totals for the year ──
        qs_year = TransaksiKeuangan.objects.filter(tanggal__year=tahun).select_related('kategori')
        total_masuk = qs_year.filter(kategori__jenis='pemasukan').aggregate(t=Sum('jumlah'))['t'] or 0
        total_keluar = qs_year.filter(kategori__jenis='pengeluaran').aggregate(t=Sum('jumlah'))['t'] or 0
        context['total_masuk'] = total_masuk
        context['total_keluar'] = total_keluar
        context['saldo'] = total_masuk - total_keluar

        # ── Category breakdown (doughnut chart) ──
        kategori_masuk = list(
            qs_year.filter(kategori__jenis='pemasukan')
            .values('kategori__nama')
            .annotate(total=Sum('jumlah'))
            .order_by('-total')
        )
        kategori_keluar = list(
            qs_year.filter(kategori__jenis='pengeluaran')
            .values('kategori__nama')
            .annotate(total=Sum('jumlah'))
            .order_by('-total')
        )
        context['kat_masuk_labels'] = json.dumps([k['kategori__nama'] for k in kategori_masuk])
        context['kat_masuk_data'] = json.dumps([float(k['total']) for k in kategori_masuk])
        context['kat_keluar_labels'] = json.dumps([k['kategori__nama'] for k in kategori_keluar])
        context['kat_keluar_data'] = json.dumps([float(k['total']) for k in kategori_keluar])

        # ── Monthly detail table ──
        monthly_detail = []
        running_saldo = 0
        for m in range(1, 13):
            masuk = monthly_masuk[m - 1]
            keluar = monthly_keluar[m - 1]
            running_saldo += masuk - keluar
            monthly_detail.append({
                'bulan': NAMA_BULAN[m],
                'masuk': masuk,
                'keluar': keluar,
                'selisih': masuk - keluar,
                'saldo': running_saldo,
            })
        context['monthly_detail'] = monthly_detail

        return context


# ─── Kategori Views ──────────────────────────────────────────────────────────

class PanelKategoriKeuanganList(PanelListView):
    model = KategoriKeuangan
    template_name = 'panel/keuangan/kategori_list.html'
    page_title = _('Kategori Keuangan')
    create_url = reverse_lazy('keuangan:panel_kategori_create')
    back_url = reverse_lazy('keuangan:panel_list')
    search_fields = ['nama']


class PanelKategoriKeuanganCreate(PanelCreateView):
    model = KategoriKeuangan
    form_class = KategoriKeuanganForm
    page_title = _('Tambah Kategori')
    form_title = _('Tambah Kategori Keuangan')
    back_url = reverse_lazy('keuangan:panel_kategori_list')
    success_url = reverse_lazy('keuangan:panel_kategori_list')


class PanelKategoriKeuanganUpdate(PanelUpdateView):
    model = KategoriKeuangan
    form_class = KategoriKeuanganForm
    page_title = _('Edit Kategori')
    form_title = _('Edit Kategori Keuangan')
    back_url = reverse_lazy('keuangan:panel_kategori_list')
    success_url = reverse_lazy('keuangan:panel_kategori_list')


class PanelKategoriKeuanganDelete(PanelDeleteView):
    model = KategoriKeuangan
    page_title = _('Hapus Kategori')
    back_url = reverse_lazy('keuangan:panel_kategori_list')
    success_url = reverse_lazy('keuangan:panel_kategori_list')
