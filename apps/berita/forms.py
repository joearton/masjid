"""Berita forms."""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Berita, KategoriBerita


class BeritaForm(forms.ModelForm):
    class Meta:
        model = Berita
        fields = ['judul', 'kategori', 'isi', 'gambar', 'is_published', 'is_pengumuman']
        widgets = {
            'isi': forms.Textarea(attrs={'rows': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))


class KategoriBeritaForm(forms.ModelForm):
    class Meta:
        model = KategoriBerita
        fields = ['nama']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))
