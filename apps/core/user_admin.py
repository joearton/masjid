"""Kelola pengguna panel & perannya (khusus superadmin)."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import SuperuserRequiredMixin
from apps.core.roles import OPERATOR_DISPLAY, ROLE_CHOICES, ROLE_OPERATOR, role_of


class PanelUserForm(forms.ModelForm):
    role = forms.ChoiceField(label=_('Peran'), choices=ROLE_CHOICES, widget=forms.RadioSelect)
    password1 = forms.CharField(label=_('Kata sandi'), widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), required=False)
    password2 = forms.CharField(label=_('Ulangi kata sandi'), widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'is_active']
        labels = {'first_name': _('Nama lengkap'), 'is_active': _('Akun aktif')}

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.editor = editor
        creating = not self.instance.pk
        self.fields['email'].required = False
        if creating:
            self.fields['password1'].required = self.fields['password2'].required = True
            self.fields['role'].initial = ROLE_OPERATOR
        else:
            self.fields['role'].initial = role_of(self.instance)
            self.fields['password1'].help_text = _('Kosongkan bila tidak ingin mengganti kata sandi.')
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(Column('username', css_class='col-md-6'), Column('first_name', css_class='col-md-6')),
            Row(Column('email', css_class='col-md-6'), Column('is_active', css_class='col-md-6 d-flex align-items-center')),
            'role',
            Row(Column('password1', css_class='col-md-6'), Column('password2', css_class='col-md-6')),
            Submit('submit', _('Simpan'), css_class='btn btn-primary'),
        )

    def clean(self):
        data = super().clean()
        p1, p2 = data.get('password1'), data.get('password2')
        if p1 or p2:
            if p1 != p2:
                self.add_error('password2', _('Kata sandi tidak sama.'))
            else:
                try:
                    validate_password(p1, self.instance)
                except forms.ValidationError as e:
                    self.add_error('password1', e)
        if self.instance.pk and self.instance == self.editor and not data.get('is_active', True):
            self.add_error('is_active', _('Anda tidak dapat menonaktifkan akun sendiri.'))
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True  # semua peran panel memerlukan akses staf
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        user.save()
        group, _created = Group.objects.get_or_create(name=OPERATOR_DISPLAY)
        if not user.is_superuser and self.cleaned_data['role'] == ROLE_OPERATOR:
            user.groups.add(group)
        else:
            user.groups.remove(group)
        return user


class PanelUserList(SuperuserRequiredMixin, ListView):
    template_name = 'panel/core/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.filter(is_staff=True).prefetch_related('groups').order_by('-is_superuser', 'username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Pengguna & Peran')
        for u in context['users']:
            u.role = role_of(u)
        return context


class _UserFormMixin(SuperuserRequiredMixin):
    model = User
    form_class = PanelUserForm
    template_name = 'panel/form.html'
    success_url = reverse_lazy('panel:user_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['editor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(page_title=self.page_title, form_title=self.form_title, back_url=self.success_url)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Pengguna %s disimpan.') % self.object.username)
        return response


class PanelUserCreate(_UserFormMixin, CreateView):
    page_title = _('Tambah Pengguna')
    form_title = _('Pilih peran "Operator Display" untuk petugas yang hanya mengatur layar masjid.')


class PanelUserUpdate(_UserFormMixin, UpdateView):
    page_title = _('Ubah Pengguna')
    form_title = _('Peran menentukan menu panel yang dapat dibuka.')

    def get_queryset(self):
        return User.objects.filter(is_staff=True, is_superuser=False)  # superadmin dikelola lewat Django admin
