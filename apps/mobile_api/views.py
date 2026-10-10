"""API publik baca-saja Masjid UMKO untuk aplikasi MyUMKO (/api/mobile/v1/)."""
import calendar
import datetime as dt
from decimal import Decimal

from django.conf import settings
from django.db.models import Q, Sum
from django.template.defaultfilters import linebreaks
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response

from apps.berita.models import Berita, KategoriBerita
from apps.core.models import SiteSetting
from apps.core.templatetags.hijri_tags import hijri_full
from apps.kegiatan.models import Kegiatan
from apps.keuangan.models import TransaksiKeuangan
from apps.profil.models import Fasilitas, Pengurus, ProfilMasjid
from apps.sholat.models import JadwalJumat
from apps.sholat import kemenag
from apps.sholat.utils import (KEYS, JadwalTidakTersedia, LokasiKoordinat, LokasiKota, get_month_schedule,
                               get_prayer_times, get_settings, zona_indonesia)

from . import serializers as sz
from .common import ApiError, MobileAPIView, MobileListView, invalid_param, not_found, today

NAMA_WAKTU = {'imsak': 'Imsak', 'subuh': 'Subuh', 'terbit': 'Terbit', 'dzuhur': 'Dzuhur',
              'ashar': 'Ashar', 'maghrib': 'Maghrib', 'isya': 'Isya'}
WAJIB = ('subuh', 'dzuhur', 'ashar', 'maghrib', 'isya')


# ------------------------------------------------------------------ pembantu
def public_base():
    return getattr(settings, 'MASJID_PUBLIC_URL', 'https://masjid.umko.ac.id').rstrip('/')


def absolute(path):
    if not path:
        return None
    return path if path.startswith('http') else public_base() + path


def file_url(field):
    try:
        return absolute(field.url) if field else None
    except ValueError:
        return None


def choice(value, label):
    return {'value': value, 'label': str(label)}


def parse_date(request, name):
    raw = request.query_params.get(name)
    if not raw:
        return None
    try:
        return dt.date.fromisoformat(raw)
    except ValueError:
        raise invalid_param(name, 'Format tanggal harus YYYY-MM-DD.')


def parse_month(request, name='month'):
    raw = request.query_params.get(name)
    if not raw:
        d = today()
        return d.year, d.month
    try:
        year, month = (int(x) for x in raw.split('-'))
        if not (1900 <= year <= 2100 and 1 <= month <= 12):
            raise ValueError
    except ValueError:
        raise invalid_param(name, 'Format bulan harus YYYY-MM.')
    return year, month


def is_true(request, name):
    return request.query_params.get(name, '').lower() in ('1', 'true', 'yes', 'ya')


def rupiah(value):
    value = Decimal(value or 0)
    return int(value) if value == value.to_integral_value() else float(value)


def schedule_day(pt):
    return {
        'tanggal': pt.tanggal.isoformat(),
        'hijriah': hijri_full(pt.tanggal),
        'sumber': pt.source,
        'waktu': {key: getattr(pt, key).isoformat() for key in KEYS},
        'jam': {key: getattr(pt, key).strftime('%H:%M') for key in KEYS},
    }


def next_prayer(lokasi, now):
    """Waktu sholat wajib berikutnya di lokasi itu; setelah Isya → Subuh besok."""
    pt = get_prayer_times(now.date(), lokasi)
    for key in WAJIB:
        moment = getattr(pt, key)
        if moment > now:
            return key, moment, False
    tomorrow = get_prayer_times(now.date() + dt.timedelta(days=1), lokasi)
    return 'subuh', tomorrow.subuh, True


LOKASI_PARAMS = [
    OpenApiParameter('kota', str, description='Kode kab/kota Kemenag dari /sholat/kota/ → jadwal resmi kota itu'),
    OpenApiParameter('lat', float, description='Lintang (GPS) → hisab kriteria Kemenag; wajib bersama lon'),
    OpenApiParameter('lon', float, description='Bujur (GPS)'),
    OpenApiParameter('tz', str, description='Zona waktu IANA perangkat (Asia/Jakarta|Asia/Makassar|Asia/Jayapura); '
                                            'disarankan bersama lat/lon, wajib di luar Indonesia'),
]


def parse_lokasi(request):
    """(objek lokasi, info lokasi). Tanpa parameter = lokasi masjid (Kotabumi)."""
    params = request.query_params
    kota, lat, lon, tz = (params.get(k, '').strip() for k in ('kota', 'lat', 'lon', 'tz'))
    if kota and (lat or lon):
        raise invalid_param('kota', 'Pilih salah satu: kota atau lat/lon.')
    if tz:
        from zoneinfo import ZoneInfo
        try:
            ZoneInfo(tz)
        except Exception:
            raise invalid_param('tz', 'Zona waktu tidak dikenal. Contoh: Asia/Jakarta.')
    if kota:
        city = kemenag.find_city(kota) if kota.isdigit() else None
        if not city:
            raise not_found('Kab/kota tidak ditemukan. Cari kodenya di /sholat/kota/.')
        if not city.daerah:  # provinsi (→ zona waktu) baru diketahui dari jadwal kota itu
            d = today()
            kemenag.fetch_month(city.id, d.year, d.month)
            city.refresh_from_db()
        lokasi = LokasiKota(city)
        return lokasi, {'jenis': 'kota', 'nama': city.nama, 'kota_id': city.id,
                        'latitude': None, 'longitude': None, 'timezone': None}
    if lat or lon:
        try:
            latitude, longitude = float(lat), float(lon)
        except ValueError:
            raise invalid_param('lat' if not lat else 'lon', 'lat dan lon wajib berupa angka desimal.')
        if not (-60 <= latitude <= 60 and -180 <= longitude <= 180):
            raise invalid_param('lat', 'Koordinat di luar jangkauan (lintang -60..60).')
        zone = tz or zona_indonesia(latitude, longitude)
        if not zone:
            raise invalid_param('tz', 'Wajib diisi untuk lokasi di luar Indonesia.')
        lokasi = LokasiKoordinat(round(latitude, 4), round(longitude, 4), zone)
        return lokasi, {'jenis': 'koordinat', 'nama': None, 'kota_id': None,
                        'latitude': lokasi.latitude, 'longitude': lokasi.longitude, 'timezone': zone}
    masjid = get_settings()
    return masjid, {'jenis': 'masjid', 'nama': masjid.kota_kemenag_nama or None,
                    'kota_id': masjid.kota_kemenag_id or None,
                    'latitude': masjid.latitude, 'longitude': masjid.longitude, 'timezone': masjid.timezone}


def unavailable():
    return ApiError('Jadwal resmi untuk kota ini sedang tidak dapat diambil. Coba lagi nanti atau gunakan lokasi GPS.',
                    code='jadwal_tidak_tersedia', status_code=503)


# ------------------------------------------------------------------ layanan
class MetaView(MobileAPIView):
    @extend_schema(tags=['Layanan'], summary='Informasi layanan masjid', responses=sz.Meta, operation_id='meta',
                   description='Panggil saat fitur Masjid dibuka: nama, alamat, tautan, dan sumber jadwal sholat.')
    def get(self, request):
        profil = ProfilMasjid.objects.first()
        site = SiteSetting.load()
        sholat = get_settings()
        return Response({
            'name': profil.nama if profil else getattr(settings, 'SITE_NAME', 'Masjid'),
            'tagline': (profil.tagline if profil else '') or getattr(settings, 'SITE_TAGLINE', ''),
            'alamat': profil.alamat if profil else '',
            'foto_url': file_url(profil.foto) if profil else None,
            'logo_url': file_url(site.logo),
            'warna': {'primary': site.warna_primary, 'accent': site.warna_accent},
            'today': today().isoformat(),
            'hijriah': hijri_full(today()),
            'jadwal_sholat': {
                'sumber': choice(sholat.sumber, sholat.get_sumber_display()),
                'lokasi': sholat.kota_kemenag_nama or None,
                'latitude': sholat.latitude,
                'longitude': sholat.longitude,
                'timezone': sholat.timezone,
            },
            'features': {
                'keuangan': site.tampilkan_keuangan,
                'donasi': site.tampilkan_donasi,
            },
            'links': {
                'web': public_base() + '/',
                'jadwal_sholat': public_base() + '/sholat/',
                'cetak_jadwal': public_base() + '/sholat/cetak/',
                'display': public_base() + '/display/',
            },
        })


# ------------------------------------------------------------------ sholat
class SholatView(MobileAPIView):
    @extend_schema(
        tags=['Jadwal sholat'], summary='Jadwal sholat satu hari + waktu berikutnya', responses=sz.Sholat, operation_id='sholat',
        parameters=[OpenApiParameter('date', str, description='YYYY-MM-DD, bawaan hari ini di zona lokasi')] + LOKASI_PARAMS)
    def get(self, request):
        lokasi, info = parse_lokasi(request)
        try:
            from zoneinfo import ZoneInfo
            now = timezone.now().astimezone(ZoneInfo(lokasi.timezone))
            target = parse_date(request, 'date') or now.date()
            pt = get_prayer_times(target, lokasi)
            key, moment, besok = next_prayer(lokasi, now)
        except JadwalTidakTersedia:
            raise unavailable()
        info['timezone'] = lokasi.timezone
        data = schedule_day(pt)
        data['lokasi'] = info
        data['berikutnya'] = {
            'key': key, 'nama': NAMA_WAKTU[key], 'waktu': moment.isoformat(),
            'besok': besok, 'detik_lagi': int((moment - now).total_seconds()),
        }
        response = Response(data)
        response['Cache-Control'] = 'public, max-age=60'
        return response


class SholatBulanView(MobileAPIView):
    @extend_schema(tags=['Jadwal sholat'], summary='Jadwal sholat satu bulan', responses=sz.SholatBulan, operation_id='sholat_bulan',
                   parameters=[OpenApiParameter('month', str, description='YYYY-MM, bawaan bulan ini')] + LOKASI_PARAMS)
    def get(self, request):
        lokasi, info = parse_lokasi(request)
        year, month = parse_month(request)
        try:
            days = get_month_schedule(year, month, lokasi)
        except JadwalTidakTersedia:
            raise unavailable()
        info['timezone'] = lokasi.timezone
        return Response({
            'bulan': f'{year}-{month:02d}',
            'sumber': 'kemenag' if days and all(d.source == 'kemenag' for d in days) else 'hisab',
            'lokasi': info,
            'results': [schedule_day(d) for d in days],
        })


class KotaView(MobileAPIView):
    @extend_schema(tags=['Jadwal sholat'], summary='Cari kab/kota jadwal Kemenag', responses=sz.KotaList,
                   operation_id='sholat_kota',
                   parameters=[OpenApiParameter('search', str, description='Mis. "bandar lampung"; kosong = semua (±518)')])
    def get(self, request):
        cities = kemenag.search_cities(request.query_params.get('search', '').strip())
        response = Response({'results': [{'id': c.id, 'nama': c.nama, 'daerah': c.daerah or None} for c in cities]})
        response['Cache-Control'] = 'public, max-age=86400'
        return response


class JumatView(MobileAPIView):
    @extend_schema(tags=['Jadwal sholat'], summary='Jadwal khatib & imam Jumat', responses=sz.JumatList, operation_id='jumat',
                   parameters=[OpenApiParameter('past', bool, description='true = riwayat (terbaru dulu)')])
    def get(self, request):
        qs = JadwalJumat.objects.all()
        if is_true(request, 'past'):
            qs = qs.filter(tanggal__lt=today()).order_by('-tanggal')[:20]
        else:
            qs = qs.filter(tanggal__gte=today()).order_by('tanggal')[:10]
        return Response({'results': [
            {'id': j.id, 'tanggal': j.tanggal.isoformat(), 'hijriah': hijri_full(j.tanggal),
             'khatib': j.khatib, 'imam': j.imam, 'tema': j.tema} for j in qs]})


# ------------------------------------------------------------------ kegiatan
def kegiatan_item(k, detail=False):
    d = today()
    status = k.status
    if status != 'cancelled' and k.tanggal != d:
        status = 'done' if k.tanggal < d else 'upcoming'
    item = {
        'id': k.id, 'judul': k.judul, 'tanggal': k.tanggal.isoformat(), 'hijriah': hijri_full(k.tanggal),
        'waktu_mulai': k.waktu_mulai.strftime('%H:%M'),
        'waktu_selesai': k.waktu_selesai.strftime('%H:%M') if k.waktu_selesai else None,
        'tempat': k.tempat, 'narasumber': k.narasumber,
        'status': choice(status, dict(Kegiatan.STATUS_CHOICES).get(status, status)),
        'gambar_url': file_url(k.gambar),
        'web_url': absolute(k.get_absolute_url()),
    }
    if detail:
        item['deskripsi'] = k.deskripsi
        item['deskripsi_html'] = linebreaks(k.deskripsi)
    else:
        item['ringkasan'] = (k.deskripsi[:160] + '…') if len(k.deskripsi) > 160 else k.deskripsi
    return item


class KegiatanListView(MobileListView):
    serializer_class = sz.Kegiatan
    @extend_schema(tags=['Kegiatan'], summary='Daftar kegiatan masjid', operation_id='kegiatan_list',
                   parameters=[OpenApiParameter('upcoming', bool, description='true = hari ini & mendatang (urut terdekat)'),
                               OpenApiParameter('search', str)])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Kegiatan.objects.all()
        if is_true(self.request, 'upcoming'):
            qs = qs.filter(tanggal__gte=today()).exclude(status='cancelled').order_by('tanggal', 'waktu_mulai')
        else:
            qs = qs.order_by('-tanggal', '-waktu_mulai')
        q = self.request.query_params.get('search', '').strip()
        if q:
            qs = qs.filter(Q(judul__icontains=q) | Q(deskripsi__icontains=q) | Q(narasumber__icontains=q))
        return qs

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        return self.get_paginated_response([kegiatan_item(k) for k in page])


class KegiatanDetailView(MobileAPIView):
    @extend_schema(tags=['Kegiatan'], summary='Detail kegiatan', responses=sz.KegiatanDetail, operation_id='kegiatan_detail')
    def get(self, request, pk):
        k = Kegiatan.objects.filter(pk=pk).first()
        if not k:
            raise not_found('Kegiatan tidak ditemukan.')
        return Response(kegiatan_item(k, detail=True))


# ------------------------------------------------------------------ berita
def berita_item(b, detail=False):
    item = {
        'id': b.id, 'slug': b.slug, 'judul': b.judul,
        'kategori': {'slug': b.kategori.slug, 'nama': b.kategori.nama} if b.kategori else None,
        'is_pengumuman': b.is_pengumuman,
        'gambar_url': file_url(b.gambar),
        'tanggal': timezone.localtime(b.created_at).isoformat(),
        'hijriah': hijri_full(b.created_at),
        'web_url': absolute(b.get_absolute_url()),
    }
    if detail:
        item['isi'] = b.isi
        item['isi_html'] = linebreaks(b.isi)
        item['diperbarui'] = timezone.localtime(b.updated_at).isoformat()
    else:
        item['ringkasan'] = (b.isi[:160] + '…') if len(b.isi) > 160 else b.isi
    return item


class BeritaListView(MobileListView):
    serializer_class = sz.Berita
    @extend_schema(tags=['Berita'], summary='Berita & pengumuman masjid', operation_id='berita_list',
                   parameters=[OpenApiParameter('kategori', str, description='slug dari /berita/kategori/'),
                               OpenApiParameter('pengumuman', bool, description='true = hanya pengumuman'),
                               OpenApiParameter('search', str)])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        qs = Berita.objects.filter(is_published=True).select_related('kategori').order_by('-created_at')
        kategori = self.request.query_params.get('kategori')
        if kategori:
            qs = qs.filter(kategori__slug=kategori)
        if is_true(self.request, 'pengumuman'):
            qs = qs.filter(is_pengumuman=True)
        q = self.request.query_params.get('search', '').strip()
        if q:
            qs = qs.filter(Q(judul__icontains=q) | Q(isi__icontains=q))
        return qs

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        return self.get_paginated_response([berita_item(b) for b in page])


class BeritaDetailView(MobileAPIView):
    @extend_schema(tags=['Berita'], summary='Detail berita', responses=sz.BeritaDetail, operation_id='berita_detail')
    def get(self, request, slug):
        b = Berita.objects.filter(is_published=True, slug=slug).select_related('kategori').first()
        if not b:
            raise not_found('Berita tidak ditemukan.')
        return Response(berita_item(b, detail=True))


class BeritaKategoriView(MobileAPIView):
    @extend_schema(tags=['Berita'], summary='Kategori berita yang berisi', responses=sz.KategoriList, operation_id='berita_kategori')
    def get(self, request):
        rows = []
        for k in KategoriBerita.objects.all():
            count = k.berita_set.filter(is_published=True).count()
            if count:
                rows.append({'slug': k.slug, 'nama': k.nama, 'count': count})
        return Response({'results': rows})


# ------------------------------------------------------------------ keuangan
class KeuanganView(MobileAPIView):
    @extend_schema(tags=['Keuangan'], summary='Laporan kas bulanan (sama dengan halaman web)', responses=sz.Keuangan, operation_id='keuangan',
                   parameters=[OpenApiParameter('month', str, description='YYYY-MM, bawaan bulan ini')])
    def get(self, request):
        if not SiteSetting.load().tampilkan_keuangan:
            raise not_found('Laporan keuangan tidak ditampilkan untuk publik.')
        year, month = parse_month(request)
        start = dt.date(year, month, 1)
        end = dt.date(year, month, calendar.monthrange(year, month)[1])
        all_tx = TransaksiKeuangan.objects.select_related('kategori')

        def total(qs, jenis):
            return qs.filter(kategori__jenis=jenis).aggregate(t=Sum('jumlah'))['t'] or 0

        before = all_tx.filter(tanggal__lt=start)
        saldo_awal = total(before, 'pemasukan') - total(before, 'pengeluaran')
        month_tx = all_tx.filter(tanggal__range=(start, end)).order_by('-tanggal', '-created_at')
        masuk, keluar = total(month_tx, 'pemasukan'), total(month_tx, 'pengeluaran')
        per_kategori = (month_tx.values('kategori__nama', 'kategori__jenis')
                        .annotate(total=Sum('jumlah')).order_by('kategori__jenis', '-total'))
        return Response({
            'bulan': f'{year}-{month:02d}',
            'saldo_awal': rupiah(saldo_awal),
            'pemasukan': rupiah(masuk),
            'pengeluaran': rupiah(keluar),
            'saldo_akhir': rupiah(saldo_awal + masuk - keluar),
            'per_kategori': [{'kategori': r['kategori__nama'], 'jenis': r['kategori__jenis'],
                              'total': rupiah(r['total'])} for r in per_kategori],
            'transaksi': [{'id': t.id, 'tanggal': t.tanggal.isoformat(), 'keterangan': t.keterangan,
                           'kategori': t.kategori.nama,
                           'jenis': choice(t.kategori.jenis, t.kategori.get_jenis_display()),
                           'jumlah': rupiah(t.jumlah)} for t in month_tx[:200]],
            'web_url': public_base() + f'/keuangan/?bulan={month}&tahun={year}',
        })


# ------------------------------------------------------------------ profil
class ProfilView(MobileAPIView):
    @extend_schema(tags=['Layanan'], summary='Profil masjid, pengurus aktif, fasilitas, dan info donasi', responses=sz.Profil, operation_id='profil')
    def get(self, request):
        profil = ProfilMasjid.objects.first()
        site = SiteSetting.load()
        pengurus = Pengurus.objects.filter(aktif=True).filter(
            Q(periode__isnull=True) | Q(periode__aktif=True)).select_related('periode')
        return Response({
            'profil': None if not profil else {
                'nama': profil.nama, 'tagline': profil.tagline, 'alamat': profil.alamat,
                'telepon': profil.telepon, 'email': profil.email, 'website': profil.website,
                'foto_url': file_url(profil.foto),
                'sejarah': profil.sejarah, 'visi': profil.visi, 'misi': profil.misi,
            },
            'pengurus': [{'id': p.id, 'nama': p.nama, 'jabatan': choice(p.jabatan, p.get_jabatan_display()),
                          'periode': p.periode.nama if p.periode else None, 'foto_url': file_url(p.foto)}
                         for p in pengurus],
            'fasilitas': [{'id': f.id, 'nama': f.nama, 'deskripsi': f.deskripsi, 'icon': f.icon}
                          for f in Fasilitas.objects.filter(aktif=True)],
            'donasi': None if not site.tampilkan_donasi else {
                'teks': site.donasi_teks, 'rekening_html': site.rekening_info,
                'qris_url': file_url(site.qris_image),
                'daftar_donatur_url': public_base() + '/#donatur-section',
            },
            'sosial_media': [{'nama': s['name'], 'url': s['url']} for s in site.social_links],
        })
