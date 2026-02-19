"""Profil forms."""
from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import ProfilMasjid, Pengurus, Fasilitas, PeriodePengurus


class ProfilMasjidForm(forms.ModelForm):
    class Meta:
        model = ProfilMasjid
        fields = '__all__'
        widgets = {
            'sejarah': forms.Textarea(attrs={'rows': 5}),
            'visi': forms.Textarea(attrs={'rows': 3}),
            'misi': forms.Textarea(attrs={'rows': 5}),
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'maps_embed': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Fieldset(
                _('Data Umum'),
                'nama',
                'tagline',
                Row(
                    Column('telepon', css_class='col-md-4'),
                    Column('email', css_class='col-md-4'),
                    Column('website', css_class='col-md-4'),
                ),
                'alamat',
                'foto',
                'maps_embed',
            ),
            Fieldset(
                _('Tentang Masjid'),
                'sejarah',
                'visi',
                'misi',
            ),
            Submit('submit', _('Simpan Perubahan'), css_class='btn btn-primary')
        )


class PeriodePengurusForm(forms.ModelForm):
    class Meta:
        model = PeriodePengurus
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))


class PengurusForm(forms.ModelForm):
    class Meta:
        model = Pengurus
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))


class FasilitasForm(forms.ModelForm):
    class Meta:
        model = Fasilitas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Simpan'), css_class='btn btn-primary'))
