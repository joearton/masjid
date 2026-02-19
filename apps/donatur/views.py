from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from apps.core.mixins import PanelListView, PanelCreateView, PanelUpdateView, PanelDeleteView
from .models import Donatur
from .forms import DonaturForm, PublicDonaturForm
from django.views.generic import CreateView
from django.contrib import messages

# Panel Views
class PanelDonaturList(PanelListView):
    model = Donatur
    template_name = 'panel/donatur/list.html'
    page_title = _('Daftar Donatur')
    create_url = reverse_lazy('donatur:panel_create')
    back_url = reverse_lazy('panel:dashboard')
    search_fields = ['nama', 'telepon', 'alamat']

class PanelDonaturCreate(PanelCreateView):
    model = Donatur
    form_class = DonaturForm
    page_title = _('Tambah Donatur')
    form_title = _('Tambah Data Donatur')
    back_url = reverse_lazy('donatur:panel_list')
    success_url = reverse_lazy('donatur:panel_list')

class PanelDonaturUpdate(PanelUpdateView):
    model = Donatur
    form_class = DonaturForm
    page_title = _('Edit Donatur')
    form_title = _('Edit Data Donatur')
    back_url = reverse_lazy('donatur:panel_list')
    success_url = reverse_lazy('donatur:panel_list')

class PanelDonaturDelete(PanelDeleteView):
    model = Donatur
    page_title = _('Hapus Donatur')
    back_url = reverse_lazy('donatur:panel_list')
    success_url = reverse_lazy('donatur:panel_list')
    
# Public Views
class PublicDonaturRegisterView(CreateView):
    model = Donatur
    form_class = PublicDonaturForm
    template_name = 'public/donatur_register.html' 
    
    def get_success_url(self):
        messages.success(self.request, _('Terima kasih, pendaftaran donatur berhasil! Pengurus akan menghubungi Anda segera.'))
        return reverse('core:home') + '#donatur-section'

    def form_invalid(self, form):
        messages.error(self.request, _('Mohon periksa kembali isian form Anda.'))
        # If invalid, redirect back to home might lose form data unless we handle sessions manually.
        # For now, let's render the template again (which we might need to exist or reuse home if we adjust HomeView).
        # To make it simple, let's redirect to home but with errors (hard to do without session/dedicated view).
        # Let's assume the user will be redirected to a dedicated page if form is invalid, OR we make this view execute on POST to itself.
        return super().form_invalid(form)
