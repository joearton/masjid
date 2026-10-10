import hashlib
from datetime import timedelta

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic import TemplateView

from . import catalog
from django.utils import timezone
from django.db.models import Sum
from apps.display.models import DisplaySettings, DisplaySlide
from apps.sholat.utils import get_prayer_times
from apps.profil.models import ProfilMasjid
from apps.keuangan.models import TransaksiKeuangan
from django.utils.translation import gettext_lazy as _

from django.shortcuts import get_object_or_404, render

def monitor_version():
    """Sidik jari isi monitor: berubah bila pengurus mengubah apa pun yang tampil di layar."""
    from django.db.models import Count, Max
    from apps.berita.models import Berita
    from apps.core.models import SiteSetting
    from apps.kegiatan.models import Kegiatan
    from apps.sholat.models import JadwalJumat, SholatSettings

    parts = [
        DisplaySettings.objects.aggregate(Max('updated_at'), Count('id')),
        DisplaySlide.objects.aggregate(Max('updated_at'), Count('id')),
        SiteSetting.objects.aggregate(Max('updated_at')),
        ProfilMasjid.objects.aggregate(Max('updated_at')),
        SholatSettings.objects.aggregate(Max('updated_at')),
        Kegiatan.objects.aggregate(Max('updated_at'), Count('id')),
        Berita.objects.aggregate(Max('updated_at'), Count('id')),
        TransaksiKeuangan.objects.aggregate(Max('id'), Count('id'), Sum('jumlah')),
        JadwalJumat.objects.aggregate(Max('id'), Count('id')),
    ]
    return hashlib.md5(repr(parts).encode()).hexdigest()[:12]


def nama_masjid():
    profil = ProfilMasjid.objects.first()
    return profil.nama if profil and profil.nama else settings.SITE_NAME


@method_decorator(xframe_options_sameorigin, name='dispatch')  # pratinjau langsung di editor panel
class DisplayView(TemplateView):
    """Monitor. Tanpa ?embed/?preview: bingkai luar (shell) yang memegang layar penuh dan memuat isi
    monitor di iframe; isi itu yang memuat ulang sendiri saat ada perubahan, sehingga fullscreen tidak lepas."""
    template_name = 'display/index.html'

    def get(self, request, *args, **kwargs):
        if request.GET.get('embed') != '1' and request.GET.get('preview') != '1':
            pk = kwargs.get('pk')
            if pk:
                get_object_or_404(DisplaySettings, pk=pk, aktif=True)
            return render(request, 'display/shell.html', {'nama': nama_masjid(), 'embed_url': request.path + '?embed=1'})
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Determine which display to show
        display_id = self.kwargs.get('pk')
        if display_id:
            display_settings = get_object_or_404(DisplaySettings, pk=display_id, aktif=True)
        else:
            # Get default display
            display_settings = DisplaySettings.objects.filter(is_default=True, aktif=True).first()
            if not display_settings:
                # Fallback to any active or create default
                display_settings = DisplaySettings.objects.filter(aktif=True).first()
                if not display_settings:
                     display_settings, _ = DisplaySettings.objects.get_or_create(
                        nama='Default',
                        defaults={'tema': 'default', 'is_default': True,
                                  'running_text': f'Selamat datang di {nama_masjid()}. Jagalah kebersihan dan ketertiban.'}
                    )
        
        context['display_settings'] = display_settings
        context['preview'] = self.request.GET.get('preview') == '1'
        if context['preview']:
            # Pratinjau template tanpa menyimpan (galeri/editor); tidak mengubah database
            if self.request.GET.get('tema') in catalog.THEMES:
                display_settings.tema = self.request.GET['tema']
            if self.request.GET.get('layout') in catalog.LAYOUTS:
                display_settings.layout = self.request.GET['layout']
            if self.request.GET.get('imsak') == '1':
                display_settings.tampilkan_imsak = True
        context['theme_style'] = catalog.theme_vars(display_settings.tema)
        fase = self.request.GET.get('fase', '')
        context['preview_fase'] = fase if context['preview'] and fase in ('normal', 'menjelang', 'iqamah', 'sholat', 'khutbah') else ''
        
        # All active displays for prev/next navigation
        all_displays = list(DisplaySettings.objects.filter(aktif=True).order_by('pk'))
        context['all_displays'] = all_displays
        current_idx = next((i for i, d in enumerate(all_displays) if d.pk == display_settings.pk), 0)
        context['prev_display'] = all_displays[current_idx - 1] if current_idx > 0 else None
        context['next_display'] = all_displays[current_idx + 1] if current_idx < len(all_displays) - 1 else None
        
        # Theme & Layout choices for overlay controls
        context['theme_choices'] = DisplaySettings.THEME_CHOICES
        context['layout_choices'] = DisplaySettings.LAYOUT_CHOICES
        
        # Jadwal hari ini + Subuh besok (hitung mundur setelah Isya)
        today = timezone.localdate()
        pt = get_prayer_times(today)
        context['prayer_times'] = pt
        context['besok'] = get_prayer_times(today + timedelta(days=1))
        context['is_jumat'] = today.weekday() == 4
        context['masjid_tz'] = str(pt.subuh.tzinfo)
        context['monitor_version'] = monitor_version()
        context['server_now_ms'] = int(timezone.now().timestamp() * 1000)
        context['monitor_config'] = {
            'peringatan': display_settings.peringatan_menit,
            'iqamah': display_settings.iqamah_minutes(),
            'sholat': display_settings.durasi_sholat,
            'jumat': display_settings.durasi_jumat if today.weekday() == 4 else 0,
        }

        context['profil'] = ProfilMasjid.objects.first()

        # Saldo kas + ringkasan bulan berjalan
        kas = TransaksiKeuangan.objects
        pemasukan = kas.filter(kategori__jenis='pemasukan').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        pengeluaran = kas.filter(kategori__jenis='pengeluaran').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        context['saldo_akhir'] = pemasukan - pengeluaran
        bulan = kas.filter(tanggal__year=today.year, tanggal__month=today.month)
        context['kas_bulan_masuk'] = bulan.filter(kategori__jenis='pemasukan').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        context['kas_bulan_keluar'] = bulan.filter(kategori__jenis='pengeluaran').aggregate(Sum('jumlah'))['jumlah__sum'] or 0

        # Get Slides for THIS display
        context['slides'] = display_settings.slides.filter(aktif=True).order_by('urutan')

        # Context for specific slide types
        from apps.kegiatan.models import Kegiatan
        from apps.berita.models import Berita
        from apps.sholat.models import JadwalJumat

        context['kegiatan_list'] = Kegiatan.objects.filter(tanggal__gte=today).exclude(status='cancelled').order_by('tanggal', 'waktu_mulai')[:5]
        context['berita_list'] = Berita.objects.filter(is_published=True).order_by('-created_at')[:5]
        context['jumat'] = JadwalJumat.objects.filter(tanggal__gte=today).order_by('tanggal').first()

        return context


from django.http import JsonResponse
from django.views import View


class MonitorVersionView(View):
    """Ditanya monitor tiap beberapa detik; bila versi berubah, layar memuat ulang sendiri."""
    http_method_names = ['get']

    def get(self, request):
        response = JsonResponse({'versi': monitor_version()})
        response['Cache-Control'] = 'no-store'
        return response


class DisplayUpdateAPIView(View):
    """Quick AJAX endpoint to switch theme/layout for a display (pengurus saja)."""
    http_method_names = ['post']

    def post(self, request, pk):
        if not request.user.is_staff:
            return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
        display = get_object_or_404(DisplaySettings, pk=pk)
        tema = request.POST.get('tema')
        layout = request.POST.get('layout')
        valid_themes = [c[0] for c in DisplaySettings.THEME_CHOICES]
        valid_layouts = [c[0] for c in DisplaySettings.LAYOUT_CHOICES]
        if tema and tema in valid_themes:
            display.tema = tema
        if layout and layout in valid_layouts:
            display.layout = layout
        display.save(update_fields=['tema', 'layout', 'updated_at'])
        return JsonResponse({'ok': True, 'tema': display.tema, 'layout': display.layout})


# ─── Panel Views ─────────────────────────────────────────────────────────────

from django.urls import reverse_lazy, reverse
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from apps.core.mixins import PanelUpdateView, PanelListView, PanelCreateView, PanelDeleteView, StaffRequiredMixin
from .forms import DisplaySettingsForm, DisplaySlideForm
from django.shortcuts import get_object_or_404

# Display Lists (Settings)
class PanelDisplaySettingsList(PanelListView):
    model = DisplaySettings
    template_name = 'panel/display/settings_list.html'
    page_title = _('Kelola Display')
    create_url = reverse_lazy('display:panel_settings_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['nama']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for d in context['object_list']:
            label, p, a, b = catalog.THEMES.get(d.tema, catalog.THEMES['default'])
            d.theme_style = f'--p:{p};--a:{a};--b:{b}'
            d.layout_svg = mark_safe(catalog.LAYOUTS.get(d.layout, catalog.LAYOUTS['classic'])[2])
            d.slide_total = d.slides.count()
            d.slide_aktif = d.slides.filter(aktif=True).count()
        return context

class PanelDisplaySettingsCreate(PanelCreateView):
    model = DisplaySettings
    form_class = DisplaySettingsForm
    page_title = _('Tambah Display')
    form_title = _('Buat Display Baru')
    back_url = reverse_lazy('display:panel_settings_list')

    def get_success_url(self):
        return reverse('display:panel_settings_edit', kwargs={'pk': self.object.pk})

class PanelDisplayEditor(StaffRequiredMixin, DetailView):
    """Editor interaktif: setiap perubahan tersimpan via AJAX, pratinjau langsung di sampingnya."""
    model = DisplaySettings
    template_name = 'panel/display/editor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = self.object
        context.update({
            'page_title': _('Atur Display: %s') % d.nama,
            'themes': [(k, v[0], v[1], v[2], v[3]) for k, v in catalog.THEMES.items()],
            'layouts': [(k, v[0], v[1], mark_safe(v[2])) for k, v in catalog.LAYOUTS.items()],
            'presets': catalog.PRESETS,
            'slide_templates': catalog.SLIDE_TEMPLATES,
            'presets_json': {p['key']: p['nilai'] for p in catalog.PRESETS},
            'themes_json': {k: [v[1], v[2], v[3], str(v[0])] for k, v in catalog.THEMES.items()},
            'layout_labels_json': {k: str(v[0]) for k, v in catalog.LAYOUTS.items()},
            'slide_templates_json': {t['key']: {k: str(t[k]) if k in ('judul', 'konten_teks') else t[k]
                                                for k in ('judul', 'tipe', 'durasi', 'konten_teks')}
                                     for t in catalog.SLIDE_TEMPLATES},
            'notification_choices': DisplaySettings.NOTIFICATION_CHOICES,
            'slide_types': DisplaySlide.TIPE_CHOICES,
            'iqamah_fields': [('iqamah_subuh', 'Subuh'), ('iqamah_dzuhur', 'Dzuhur'), ('iqamah_ashar', 'Ashar'),
                              ('iqamah_maghrib', 'Maghrib'), ('iqamah_isya', 'Isya')],
            'slides': d.slides.order_by('urutan', 'pk'),
            'preview_url': reverse('display:detail', kwargs={'pk': d.pk}),
        })
        return context


# Kompatibel dengan nama lama
PanelDisplaySettingsUpdate = PanelDisplayEditor


class PanelDisplaySettingsDelete(PanelDeleteView):
    model = DisplaySettings
    page_title = _('Hapus Display')
    back_url = reverse_lazy('display:panel_settings_list')
    success_url = reverse_lazy('display:panel_settings_list')


# Slide Management (Nested under Display)
class PanelDisplaySlideList(PanelListView):
    model = DisplaySlide
    template_name = 'panel/display/slide_list.html'
    page_title = _('Kelola Slide Display')
    search_fields = ['judul']
    
    def get_queryset(self):
        self.display = get_object_or_404(DisplaySettings, pk=self.kwargs['display_pk'])
        return DisplaySlide.objects.filter(display=self.display).order_by('urutan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['display_settings'] = self.display
        context['page_title'] = _(f'Slide: {self.display.nama}')
        context['create_url'] = reverse('display:panel_slide_create', kwargs={'display_pk': self.display.pk})
        context['back_url'] = reverse('display:panel_settings_edit', kwargs={'pk': self.display.pk})
        return context

class PanelDisplaySlideCreate(PanelCreateView):
    model = DisplaySlide
    form_class = DisplaySlideForm
    page_title = _('Tambah Slide')
    form_title = _('Tambah Slide Baru')

    def get_initial(self):
        initial = super().get_initial()
        self.display = get_object_or_404(DisplaySettings, pk=self.kwargs['display_pk'])
        initial['display'] = self.display
        return initial

    def form_valid(self, form):
        form.instance.display_id = self.kwargs['display_pk']
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_id = self.kwargs['display_pk']
        context['back_url'] = reverse('display:panel_slide_list', kwargs={'display_pk': display_id})
        return context

    def get_success_url(self):
        return reverse('display:panel_slide_list', kwargs={'display_pk': self.kwargs['display_pk']})

class PanelDisplaySlideUpdate(PanelUpdateView):
    model = DisplaySlide
    form_class = DisplaySlideForm
    page_title = _('Edit Slide')
    form_title = _('Edit Slide')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_id = self.object.display.pk
        context['back_url'] = reverse('display:panel_slide_list', kwargs={'display_pk': display_id})
        return context

    def get_success_url(self):
        return reverse('display:panel_slide_list', kwargs={'display_pk': self.object.display.pk})

class PanelDisplaySlideDelete(PanelDeleteView):
    model = DisplaySlide
    page_title = _('Hapus Slide')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        display_id = self.object.display.pk
        context['back_url'] = reverse('display:panel_slide_list', kwargs={'display_pk': display_id})
        return context

    def get_success_url(self):
        return reverse('display:panel_slide_list', kwargs={'display_pk': self.object.display.pk})


# ─── AJAX editor (JSON, khusus pengurus) ─────────────────────────────────────

from functools import wraps

from django.db import models

from django.forms import modelform_factory
from django.template.loader import render_to_string

EDITABLE_FIELDS = [
    'nama', 'tema', 'layout', 'running_text', 'video_url', 'sholat_notification', 'custom_notification',
    'is_default', 'aktif', 'peringatan_menit', 'iqamah_subuh', 'iqamah_dzuhur', 'iqamah_ashar',
    'iqamah_maghrib', 'iqamah_isya', 'durasi_sholat', 'durasi_jumat', 'tampilkan_imsak',
]
SLIDE_FIELDS = ['judul', 'tipe', 'durasi', 'konten_teks', 'gambar', 'aktif']
AUDIO_EXT = ('.mp3', '.ogg', '.wav', '.m4a')
MAX_AUDIO = 5 * 1024 * 1024


def staff_json(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
        if request.method != 'POST':
            return JsonResponse({'ok': False, 'error': 'method'}, status=405)
        return view(request, *args, **kwargs)
    return wrapper


def _errors(form):
    return JsonResponse({'ok': False, 'errors': {k: [str(e) for e in v] for k, v in form.errors.items()}}, status=400)


def _display_state(d):
    return {
        'id': d.pk, 'nama': d.nama, 'tema': d.tema, 'layout': d.layout, 'aktif': d.aktif, 'is_default': d.is_default,
        'tampilkan_imsak': d.tampilkan_imsak,
        'custom_notification': d.custom_notification.url if d.custom_notification else None,
    }


def _slides_payload(request, display):
    slides = display.slides.order_by('urutan', 'pk')
    return {'ok': True, 'count': slides.count(), 'aktif': slides.filter(aktif=True).count(),
            'html': render_to_string('panel/display/_slides.html', {'slides': slides}, request)}


@staff_json
def ajax_display_save(request, pk):
    """Simpan sebagian kolom (yang dikirim saja)."""
    display = get_object_or_404(DisplaySettings, pk=pk)
    fields = [f for f in EDITABLE_FIELDS if f in request.POST or f in request.FILES]
    hapus_suara = request.POST.get('hapus_suara') == 'true'
    if not fields and not hapus_suara:
        return JsonResponse({'ok': False, 'error': 'Tidak ada perubahan.'}, status=400)
    upload = request.FILES.get('custom_notification')
    if upload:
        if not upload.name.lower().endswith(AUDIO_EXT):
            return JsonResponse({'ok': False, 'errors': {'custom_notification': ['Format harus MP3, OGG, WAV, atau M4A.']}}, status=400)
        if upload.size > MAX_AUDIO:
            return JsonResponse({'ok': False, 'errors': {'custom_notification': ['Ukuran maksimal 5 MB.']}}, status=400)
    if fields:
        form = modelform_factory(DisplaySettings, fields=fields)(request.POST, request.FILES, instance=display)
        if not form.is_valid():
            return _errors(form)
        display = form.save()
    if hapus_suara and display.custom_notification:
        display.custom_notification.delete(save=False)
        display.custom_notification = None
        display.save()
    return JsonResponse({'ok': True, 'display': _display_state(display)})


@staff_json
def ajax_display_duplicate(request, pk):
    src = get_object_or_404(DisplaySettings, pk=pk)
    slides = list(src.slides.all())
    src.pk = None
    src.nama = f'{src.nama} (salinan)'[:100]
    src.is_default = False
    src.save()
    for slide in slides:
        slide.pk = None
        slide.display = src
        slide.save()
    return JsonResponse({'ok': True, 'url': reverse('display:panel_settings_edit', kwargs={'pk': src.pk})})


@staff_json
def ajax_slide_create(request, display_pk):
    display = get_object_or_404(DisplaySettings, pk=display_pk)
    form = modelform_factory(DisplaySlide, fields=SLIDE_FIELDS)(request.POST, request.FILES)
    if not form.is_valid():
        return _errors(form)
    slide = form.save(commit=False)
    slide.display = display
    last = display.slides.order_by('-urutan').first()
    slide.urutan = last.urutan + 1 if last else 0
    slide.save()
    return JsonResponse(_slides_payload(request, display))


@staff_json
def ajax_slide_update(request, pk):
    """Ubah slide; hanya kolom yang dikirim (mis. aktif/durasi dari daftar, atau semua dari modal)."""
    slide = get_object_or_404(DisplaySlide, pk=pk)
    fields = [f for f in SLIDE_FIELDS if f in request.POST or f in request.FILES]
    if request.POST.get('hapus_gambar') == 'true' and slide.gambar:
        slide.gambar = None
        slide.save(update_fields=['gambar', 'updated_at'])
    if fields:
        form = modelform_factory(DisplaySlide, fields=fields)(request.POST, request.FILES, instance=slide)
        if not form.is_valid():
            return _errors(form)
        form.save()
    return JsonResponse(_slides_payload(request, slide.display))


@staff_json
def ajax_slide_delete(request, pk):
    slide = get_object_or_404(DisplaySlide, pk=pk)
    display = slide.display
    slide.delete()
    return JsonResponse(_slides_payload(request, display))


@staff_json
def ajax_slide_duplicate(request, pk):
    slide = get_object_or_404(DisplaySlide, pk=pk)
    display = slide.display
    display.slides.filter(urutan__gt=slide.urutan).update(urutan=models.F('urutan') + 1)
    slide.pk = None
    slide.judul = f'{slide.judul} (salinan)'[:200]
    slide.urutan += 1
    slide.save()
    return JsonResponse(_slides_payload(request, display))


@staff_json
def ajax_slide_reorder(request, display_pk):
    display = get_object_or_404(DisplaySettings, pk=display_pk)
    ids = [int(i) for i in request.POST.getlist('ids') if i.isdigit()]
    slides = {s.pk: s for s in display.slides.filter(pk__in=ids)}
    for urutan, pk in enumerate(ids):
        if pk in slides and slides[pk].urutan != urutan:
            slides[pk].urutan = urutan
            slides[pk].save(update_fields=['urutan', 'updated_at'])
    return JsonResponse(_slides_payload(request, display))


# Operator Display boleh memakai seluruh menu display (lihat apps.core.roles)
for _view in (PanelDisplaySettingsList, PanelDisplaySettingsCreate, PanelDisplayEditor, PanelDisplaySettingsDelete,
              PanelDisplaySlideList, PanelDisplaySlideCreate, PanelDisplaySlideUpdate, PanelDisplaySlideDelete):
    _view.allow_display_operator = True
