from django.views.generic import TemplateView
from django.utils import timezone
from django.db.models import Sum
from apps.display.models import DisplaySettings, DisplaySlide
from apps.sholat.utils import get_prayer_times
from apps.profil.models import ProfilMasjid
from apps.keuangan.models import TransaksiKeuangan
from django.utils.translation import gettext_lazy as _

from django.shortcuts import get_object_or_404

class DisplayView(TemplateView):
    template_name = 'display/index.html'

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
                        defaults={'tema': 'default', 'running_text': 'Selamat Datang di Masjid Al-Ikhlas', 'is_default': True}
                    )
        
        context['display_settings'] = display_settings
        
        # All active displays for prev/next navigation
        all_displays = list(DisplaySettings.objects.filter(aktif=True).order_by('pk'))
        context['all_displays'] = all_displays
        current_idx = next((i for i, d in enumerate(all_displays) if d.pk == display_settings.pk), 0)
        context['prev_display'] = all_displays[current_idx - 1] if current_idx > 0 else None
        context['next_display'] = all_displays[current_idx + 1] if current_idx < len(all_displays) - 1 else None
        
        # Theme & Layout choices for overlay controls
        context['theme_choices'] = DisplaySettings.THEME_CHOICES
        context['layout_choices'] = DisplaySettings.LAYOUT_CHOICES
        
        # Get Prayer Times
        pt = get_prayer_times(timezone.now())
        context['prayer_times'] = pt
        
        context['profil'] = ProfilMasjid.objects.first()

        # Calculate Saldo
        pemasukan = TransaksiKeuangan.objects.filter(kategori__jenis='pemasukan').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        pengeluaran = TransaksiKeuangan.objects.filter(kategori__jenis='pengeluaran').aggregate(Sum('jumlah'))['jumlah__sum'] or 0
        context['saldo_akhir'] = pemasukan - pengeluaran
        
        # Get Slides for THIS display
        context['slides'] = display_settings.slides.filter(aktif=True).order_by('urutan')
        
        # Context for specific slide types
        from apps.kegiatan.models import Kegiatan
        from apps.berita.models import Berita
        import datetime
        
        context['kegiatan_list'] = Kegiatan.objects.filter(tanggal__gte=datetime.date.today()).order_by('tanggal')[:5]
        context['berita_list'] = Berita.objects.filter(is_published=True).order_by('-created_at')[:5]

        return context


from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


@method_decorator(csrf_exempt, name='dispatch')
class DisplayUpdateAPIView(View):
    """Quick AJAX endpoint to switch theme/layout for a display."""
    def post(self, request, pk):
        display = get_object_or_404(DisplaySettings, pk=pk)
        tema = request.POST.get('tema')
        layout = request.POST.get('layout')
        valid_themes = [c[0] for c in DisplaySettings.THEME_CHOICES]
        valid_layouts = [c[0] for c in DisplaySettings.LAYOUT_CHOICES]
        if tema and tema in valid_themes:
            display.tema = tema
        if layout and layout in valid_layouts:
            display.layout = layout
        display.save()
        return JsonResponse({'ok': True, 'tema': display.tema, 'layout': display.layout})


# ─── Panel Views ─────────────────────────────────────────────────────────────

from django.urls import reverse_lazy, reverse
from apps.core.mixins import PanelUpdateView, PanelListView, PanelCreateView, PanelDeleteView
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

class PanelDisplaySettingsCreate(PanelCreateView):
    model = DisplaySettings
    form_class = DisplaySettingsForm
    page_title = _('Tambah Display')
    form_title = _('Buat Display Baru')
    back_url = reverse_lazy('display:panel_settings_list')
    success_url = reverse_lazy('display:panel_settings_list')

class PanelDisplaySettingsUpdate(PanelUpdateView):
    model = DisplaySettings
    form_class = DisplaySettingsForm
    template_name = 'panel/display/settings.html' # Keep using the detailed form template
    page_title = _('Edit Pengaturan Display')
    form_title = _('Edit Display')
    back_url = reverse_lazy('display:panel_settings_list')
    success_url = reverse_lazy('display:panel_settings_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass link to slide management for THIS display
        context['manage_slides_url'] = reverse('display:panel_slide_list', kwargs={'display_pk': self.object.pk})
        context['preview_url'] = reverse('display:detail', kwargs={'pk': self.object.pk})
        return context

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
