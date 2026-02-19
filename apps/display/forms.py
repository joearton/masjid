from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset
from .models import DisplaySettings, DisplaySlide

class DisplaySettingsForm(forms.ModelForm):
    class Meta:
        model = DisplaySettings
        fields = '__all__'
        widgets = {
            'running_text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('nama', css_class='col-md-8'),
                Column('is_default', css_class='col-md-4 d-flex align-items-center mb-3'),
            ),
            Row(
                Column('tema', css_class='col-md-6'),
                Column('layout', css_class='col-md-6'),
            ),
            Fieldset(
                _('Konten & Tampilan'),
                'running_text',
                'video_url',
            ),
            Fieldset(
                _('Suara Notifikasi Sholat'),
                Row(
                    Column('sholat_notification', css_class='col-md-6'),
                    Column('custom_notification', css_class='col-md-6'),
                ),
            ),
            'aktif',
            Submit('submit', _('Simpan Pengaturan'), css_class='btn btn-primary')
        )


class DisplaySlideForm(forms.ModelForm):
    class Meta:
        model = DisplaySlide
        fields = '__all__'
        widgets = {
            'konten_teks': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Row(
                Column('judul', css_class='col-md-8'),
                Column('urutan', css_class='col-md-2'),
                Column('aktif', css_class='col-md-2 d-flex align-items-center mb-3'),
            ),
            Row(
                Column('tipe', css_class='col-md-6'),
                Column('durasi', css_class='col-md-6'),
            ),
            Fieldset(
                _('Konten'),
                'konten_teks',
                'gambar',
            ),
            Submit('submit', _('Simpan Slide'), css_class='btn btn-primary')
        )
