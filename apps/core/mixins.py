"""
Core mixins for DRY views.
All views should inherit from these mixins for consistent behavior.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.utils.translation import gettext_lazy as _


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to restrict access to staff/admin users only."""

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, _('Anda tidak memiliki akses ke halaman ini.'))
            from django.shortcuts import redirect
            return redirect('core:panel_dashboard')
        return super().handle_no_permission()


class PublicListView(ListView):
    """Base list view for public pages."""
    paginate_by = 10
    template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = getattr(self, 'page_title', '')
        return context


class PublicDetailView(DetailView):
    """Base detail view for public pages."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = str(self.object)
        return context


class PanelListView(StaffRequiredMixin, ListView):
    """Base list view for admin panel."""
    paginate_by = 20
    template_name = None
    search_fields = []  # Subclasses define e.g. ['nama', 'keterangan']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q and self.search_fields:
            from django.db.models import Q
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f'{field}__icontains': q})
            qs = qs.filter(query)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = getattr(self, 'page_title', '')
        context['create_url'] = getattr(self, 'create_url', None)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class PanelCreateView(StaffRequiredMixin, CreateView):
    """Base create view for admin panel."""
    template_name = 'panel/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = getattr(self, 'page_title', _('Tambah Data'))
        context['form_title'] = getattr(self, 'form_title', _('Tambah Data Baru'))
        context['back_url'] = getattr(self, 'back_url', None)
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data berhasil disimpan.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Terjadi kesalahan. Periksa kembali form Anda.'))
        return super().form_invalid(form)


class PanelUpdateView(StaffRequiredMixin, UpdateView):
    """Base update view for admin panel."""
    template_name = 'panel/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = getattr(self, 'page_title', _('Edit Data'))
        context['form_title'] = getattr(self, 'form_title', _('Edit Data'))
        context['back_url'] = getattr(self, 'back_url', None)
        context['is_update'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data berhasil diperbarui.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Terjadi kesalahan. Periksa kembali form Anda.'))
        return super().form_invalid(form)


class PanelDeleteView(StaffRequiredMixin, DeleteView):
    """Base delete view for admin panel."""
    template_name = 'panel/confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = getattr(self, 'page_title', _('Hapus Data'))
        context['back_url'] = getattr(self, 'back_url', None)
        return context

    def form_valid(self, form):
        messages.success(self.request, _('Data berhasil dihapus.'))
        return super().form_valid(form)
