import json
from datetime import date, datetime, time, timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.display.models import DisplaySettings, DisplaySlide
from apps.kegiatan.models import Kegiatan
from apps.sholat.models import JadwalJumat


def fake_schedule(d, settings=None):
    from apps.sholat.utils import PrayerSchedule
    tz = timezone.get_current_timezone()
    jam = {'imsak': '04:17', 'subuh': '04:27', 'terbit': '05:39', 'dzuhur': '11:51',
           'ashar': '14:54', 'maghrib': '17:56', 'isya': '19:05'}
    return PrayerSchedule(d, {k: datetime.combine(d, time.fromisoformat(v), tz) for k, v in jam.items()}, 'kemenag')


@mock.patch('apps.display.views.get_prayer_times', side_effect=fake_schedule)
class MonitorTests(TestCase):
    def setUp(self):
        self.display = DisplaySettings.objects.create(nama='TV Utama', is_default=True, iqamah_maghrib=5)

    def test_monitor_renders_config_and_server_clock(self, _):
        r = self.client.get(reverse('display:index') + '?embed=1')
        self.assertEqual(r.status_code, 200)
        raw = r.content.decode().split('id="monitor-config" type="application/json">')[1].split('</script>')[0]
        cfg = json.loads(raw)
        self.assertEqual(cfg['iqamah']['Maghrib'], 5)
        self.assertEqual(cfg['peringatan'], 10)
        self.assertContains(r, 'var serverOffset = ')
        self.assertContains(r, 'Asia/Jakarta')
        self.assertNotContains(r, 'id="item-Imsak"')

    def test_imsak_optional_and_jumat_slide(self, _):
        self.display.tampilkan_imsak = True
        self.display.save()
        DisplaySlide.objects.create(display=self.display, judul='Petugas', tipe='jumat')
        DisplaySlide.objects.create(display=self.display, judul='Jadwal', tipe='sholat')
        JadwalJumat.objects.create(tanggal=timezone.localdate() + timedelta(days=3), khatib='Ust. Fulan', imam='Ust. Ahmad')
        r = self.client.get(reverse('display:index') + '?embed=1')
        self.assertContains(r, 'id="item-Imsak"')
        self.assertContains(r, 'Ust. Fulan')
        self.assertContains(r, 'data-prayer="Isya"')

    def test_kegiatan_slide_shows_start_time(self, _):
        DisplaySlide.objects.create(display=self.display, judul='Kegiatan', tipe='kegiatan')
        Kegiatan.objects.create(judul='Kajian Ahad', deskripsi='-', tanggal=timezone.localdate(),
                                waktu_mulai=time(16, 30), tempat='Aula')
        r = self.client.get(reverse('display:index') + '?embed=1')
        self.assertContains(r, '16:30')

    def test_jumat_config_only_on_friday(self, _):
        with mock.patch('apps.display.views.timezone.localdate', return_value=date(2026, 10, 9)):
            r = self.client.get(reverse('display:index') + '?embed=1')
        self.assertTrue(r.context['is_jumat'])
        self.assertEqual(r.context['monitor_config']['jumat'], 40)
        with mock.patch('apps.display.views.timezone.localdate', return_value=date(2026, 10, 10)):
            r = self.client.get(reverse('display:index') + '?embed=1')
        self.assertEqual(r.context['monitor_config']['jumat'], 0)

    def test_shell_keeps_fullscreen_frame(self, _):
        r = self.client.get(reverse('display:index'))
        self.assertTemplateUsed(r, 'display/shell.html')
        self.assertContains(r, 'src="/display/?embed=1"')
        self.assertContains(r, 'allow="fullscreen; autoplay; screen-wake-lock"')
        r = self.client.get(reverse('display:detail', args=[self.display.pk]))
        self.assertContains(r, f'src="/display/{self.display.pk}/?embed=1"')
        self.assertEqual(self.client.get(reverse('display:detail', args=[9999])).status_code, 404)

    def test_no_placeholder_mosque_name(self, _):
        from apps.profil.models import ProfilMasjid
        ProfilMasjid.objects.all().delete()
        DisplaySettings.objects.all().delete()
        for url in (reverse('display:index'), reverse('display:index') + '?embed=1'):
            self.assertNotContains(self.client.get(url), 'Ikhlas')
        self.assertNotIn('Ikhlas', DisplaySettings.objects.get().running_text)

    def test_navbar_links_to_monitor(self, _):
        r = self.client.get('/', follow=True)
        self.assertContains(r, reverse('display:index'))

    def test_update_api_staff_only(self, _):
        url = reverse('display:api_update', args=[self.display.pk])
        self.assertEqual(self.client.post(url, {'tema': 'blue'}).status_code, 403)
        staff = get_user_model().objects.create_user('pengurus', password='x', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.client.post(url, {'tema': 'blue'}).status_code, 200)
        self.display.refresh_from_db()
        self.assertEqual(self.display.tema, 'blue')

    def test_version_changes_when_admin_edits(self, _):
        url = reverse('display:versi')
        r = self.client.get(url)
        self.assertEqual(r['Cache-Control'], 'no-store')
        v1 = r.json()['versi']
        self.assertEqual(self.client.get(url).json()['versi'], v1)
        page = self.client.get(reverse('display:index') + '?embed=1')
        self.assertContains(page, v1)
        self.display.tema = 'gold'
        self.display.save()
        v2 = self.client.get(url).json()['versi']
        self.assertNotEqual(v1, v2)
        slide = DisplaySlide.objects.create(display=self.display, judul='Info', tipe='teks')
        v3 = self.client.get(url).json()['versi']
        self.assertNotEqual(v2, v3)
        slide.delete()
        self.assertNotEqual(self.client.get(url).json()['versi'], v3)


@mock.patch('apps.display.views.get_prayer_times', side_effect=fake_schedule)
class EditorAjaxTests(TestCase):
    def setUp(self):
        self.display = DisplaySettings.objects.create(nama='TV Utama', is_default=True)
        self.staff = get_user_model().objects.create_user('pengurus', password='x', is_staff=True)
        self.client.force_login(self.staff)

    def url(self, name, **kw):
        return reverse(f'display:{name}', kwargs=kw)

    def test_editor_page_lists_catalog(self, _):
        from apps.display import catalog
        r = self.client.get(self.url('panel_settings_edit', pk=self.display.pk))
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(len(catalog.THEMES), 20)
        self.assertGreaterEqual(len(catalog.LAYOUTS), 13)
        self.assertGreaterEqual(len(catalog.PRESETS), 15)
        for key in ('ramadan', 'portrait', 'analog', 'ornamen'):
            self.assertContains(r, f'value="{key}"' if key != 'ramadan' else 'data-tema="ramadan"')

    def test_partial_save_validates_and_keeps_other_fields(self, _):
        save = self.url('ajax_display_save', pk=self.display.pk)
        r = self.client.post(save, {'tema': 'ramadan', 'layout': 'countdown', 'tampilkan_imsak': 'true'})
        self.assertEqual(r.status_code, 200, r.content)
        self.display.refresh_from_db()
        self.assertEqual((self.display.tema, self.display.layout, self.display.tampilkan_imsak, self.display.nama),
                         ('ramadan', 'countdown', True, 'TV Utama'))
        r = self.client.post(save, {'tema': 'tidak-ada'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('tema', r.json()['errors'])
        r = self.client.post(save, {'iqamah_maghrib': '-3'})
        self.assertEqual(r.status_code, 400)
        r = self.client.post(save, {'tampilkan_imsak': 'false'})
        self.display.refresh_from_db()
        self.assertFalse(self.display.tampilkan_imsak)

    def test_audio_upload_rejects_non_audio(self, _):
        from django.core.files.uploadedfile import SimpleUploadedFile
        r = self.client.post(self.url('ajax_display_save', pk=self.display.pk),
                             {'custom_notification': SimpleUploadedFile('x.exe', b'MZ')})
        self.assertEqual(r.status_code, 400)

    def test_slide_crud_reorder_duplicate(self, _):
        create = self.url('ajax_slide_create', display_pk=self.display.pk)
        for judul in ('A', 'B', 'C'):
            r = self.client.post(create, {'judul': judul, 'tipe': 'teks', 'durasi': 10, 'konten_teks': judul, 'aktif': 'true'})
            self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(r.json()['count'], 3)
        a, b, c = self.display.slides.order_by('urutan')
        self.assertEqual([a.urutan, b.urutan, c.urutan], [0, 1, 2])
        r = self.client.post(self.url('ajax_slide_reorder', display_pk=self.display.pk), {'ids': [c.pk, a.pk, b.pk]})
        self.assertEqual(list(self.display.slides.order_by('urutan').values_list('judul', flat=True)), ['C', 'A', 'B'])
        self.client.post(self.url('ajax_slide_update', pk=a.pk), {'aktif': 'false'})
        a.refresh_from_db()
        self.assertFalse(a.aktif)
        self.assertEqual(a.judul, 'A')
        r = self.client.post(self.url('ajax_slide_update', pk=a.pk), {'durasi': 'abc'})
        self.assertEqual(r.status_code, 400)
        self.client.post(self.url('ajax_slide_duplicate', pk=c.pk))
        self.assertEqual(list(self.display.slides.order_by('urutan').values_list('judul', flat=True)), ['C', 'C (salinan)', 'A', 'B'])
        r = self.client.post(self.url('ajax_slide_delete', pk=b.pk))
        self.assertEqual(r.json()['count'], 3)
        self.assertIn('slide-row', r.json()['html'])

    def test_duplicate_display_copies_slides(self, _):
        DisplaySlide.objects.create(display=self.display, judul='X', tipe='teks')
        r = self.client.post(self.url('ajax_display_duplicate', pk=self.display.pk))
        copy = DisplaySettings.objects.exclude(pk=self.display.pk).get()
        self.assertEqual(r.json()['url'], self.url('panel_settings_edit', pk=copy.pk))
        self.assertFalse(copy.is_default)
        self.assertEqual(copy.slides.count(), 1)

    def test_ajax_requires_staff_and_post(self, _):
        save = self.url('ajax_display_save', pk=self.display.pk)
        self.assertEqual(self.client.get(save).status_code, 405)
        self.client.logout()
        self.assertEqual(self.client.post(save, {'tema': 'blue'}).status_code, 403)
        user = get_user_model().objects.create_user('jamaah', password='x')
        self.client.force_login(user)
        self.assertEqual(self.client.post(save, {'tema': 'blue'}).status_code, 403)

    def test_preview_mode_frameable_with_theme_vars(self, _):
        self.display.tema = 'ramadan'
        self.display.save()
        r = self.client.get(self.url('detail', pk=self.display.pk) + '?preview=1&fase=iqamah')
        self.assertEqual(r['X-Frame-Options'], 'SAMEORIGIN')
        self.assertContains(r, 'is-preview')
        self.assertContains(r, '--primary:#1e3a8a')
        self.assertContains(r, 'var PREVIEW_FASE = "iqamah"')
        r = self.client.get(self.url('detail', pk=self.display.pk) + '?embed=1&fase=iqamah')
        self.assertContains(r, 'var PREVIEW_FASE = ""')

    def test_list_page(self, _):
        r = self.client.get(self.url('panel_settings_list'))
        self.assertContains(r, 'TV Utama')
        self.assertContains(r, '<svg viewBox')
