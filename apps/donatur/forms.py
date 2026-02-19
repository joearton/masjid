from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Fieldset, HTML
from .models import Donatur

class DonaturForm(forms.ModelForm):
    class Meta:
        model = Donatur
        fields = '__all__'
        widgets = {
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'keterangan': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                _('Informasi Dasar'),
                Row(
                    Column('nama', css_class='col-md-6'),
                    Column('tipe', css_class='col-md-3'),
                    Column('status', css_class='col-md-3'),
                ),
                'alamat',
                'telepon',
            ),
            Fieldset(
                _('Komitmen Donasi (Khusus Donatur Tetap)'),
                HTML('<div class="alert alert-info text-small mb-3">Isi bagian ini jika merupakan Donatur Tetap.</div>'),
                Row(
                    Column('komitmen_rutin', css_class='col-md-6'),
                    Column('tipe_rutin', css_class='col-md-6'),
                ),
            ),
            'keterangan',
            Submit('submit', _('Simpan Data Donatur'), css_class='btn btn-primary')
        )

class PublicDonaturForm(forms.ModelForm):
    class Meta:
        model = Donatur
        fields = ['nama', 'alamat', 'telepon', 'tipe', 'komitmen_rutin', 'tipe_rutin', 'keterangan']
        widgets = {
            'alamat': forms.Textarea(attrs={'rows': 2, 'placeholder': _('Alamat lengkap Anda')}),
            'keterangan': forms.Textarea(attrs={'rows': 2, 'placeholder': _('Catatan tambahan (opsional)')}),
            'komitmen_rutin': forms.NumberInput(attrs={'step': '1000', 'placeholder': '0'}),
        }
        help_texts = {
            'komitmen_rutin': _('Diisi jika Anda berniat menjadi donatur tetap.'),
        }
        labels = {
            'komitmen_rutin': _('Rencana Donasi Rutin (Rp)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'donatur:public_register'
        self.helper.layout = Layout(
            'nama',
            Row(
                Column('telepon', css_class='col-md-6'),
                Column('tipe', css_class='col-md-6'),
            ),
            'alamat',
            HTML('<div class="collapse" id="collapseRutin">'),
            Fieldset(
                _('Rencana Donasi Rutin (Opsional)'),
                Row(
                    Column('komitmen_rutin', css_class='col-md-7'),
                    Column('tipe_rutin', css_class='col-md-5'),
                ),
            ),
            HTML('</div>'),
            'keterangan',
            Submit('submit', _('Daftar Jadi Donatur'), css_class='btn btn-success w-100')
        )
        
        self.fields['tipe'].widget.attrs.update({
            'onchange': "if(this.value === 'tetap') { document.getElementById('collapseRutin').classList.add('show'); } else { document.getElementById('collapseRutin').classList.remove('show'); }"
        })
