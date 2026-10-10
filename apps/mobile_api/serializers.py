"""Bentuk respons untuk skema OpenAPI (dokumentasi). Data dibangun di views.py."""
from rest_framework import serializers as s


class Choice(s.Serializer):
    value = s.CharField()
    label = s.CharField()


class Jam(s.Serializer):
    imsak = s.CharField(help_text='HH:MM')
    subuh = s.CharField()
    terbit = s.CharField()
    dzuhur = s.CharField()
    ashar = s.CharField()
    maghrib = s.CharField()
    isya = s.CharField()


class Waktu(s.Serializer):
    imsak = s.DateTimeField()
    subuh = s.DateTimeField()
    terbit = s.DateTimeField()
    dzuhur = s.DateTimeField()
    ashar = s.DateTimeField()
    maghrib = s.DateTimeField()
    isya = s.DateTimeField()


class JadwalHari(s.Serializer):
    tanggal = s.DateField()
    hijriah = s.CharField()
    sumber = s.ChoiceField(choices=['kemenag', 'hisab'])
    waktu = Waktu()
    jam = Jam()


class Berikutnya(s.Serializer):
    key = s.ChoiceField(choices=['subuh', 'dzuhur', 'ashar', 'maghrib', 'isya'])
    nama = s.CharField()
    waktu = s.DateTimeField()
    besok = s.BooleanField()
    detik_lagi = s.IntegerField()


class Lokasi(s.Serializer):
    jenis = s.ChoiceField(choices=['masjid', 'kota', 'koordinat'])
    nama = s.CharField(allow_null=True, help_text='Nama kab/kota (masjid/kota); null untuk koordinat')
    kota_id = s.CharField(allow_null=True)
    latitude = s.FloatField(allow_null=True)
    longitude = s.FloatField(allow_null=True)
    timezone = s.CharField(help_text='Zona waktu jam pada respons ini')


class Sholat(JadwalHari):
    lokasi = Lokasi()
    berikutnya = Berikutnya()


class SholatBulan(s.Serializer):
    bulan = s.CharField(help_text='YYYY-MM')
    sumber = s.ChoiceField(choices=['kemenag', 'hisab'])
    lokasi = Lokasi()
    results = JadwalHari(many=True)


class Kota(s.Serializer):
    id = s.CharField()
    nama = s.CharField()
    daerah = s.CharField(allow_null=True, help_text='Provinsi; terisi setelah jadwal kota itu pernah diambil')


class KotaList(s.Serializer):
    results = Kota(many=True)


class Jumat(s.Serializer):
    id = s.IntegerField()
    tanggal = s.DateField()
    hijriah = s.CharField()
    khatib = s.CharField()
    imam = s.CharField()
    tema = s.CharField()


class JumatList(s.Serializer):
    results = Jumat(many=True)


class Kegiatan(s.Serializer):
    id = s.IntegerField()
    judul = s.CharField()
    tanggal = s.DateField()
    hijriah = s.CharField()
    waktu_mulai = s.CharField(help_text='HH:MM')
    waktu_selesai = s.CharField(allow_null=True)
    tempat = s.CharField()
    narasumber = s.CharField()
    status = Choice(help_text='upcoming | ongoing | done | cancelled')
    gambar_url = s.URLField(allow_null=True)
    web_url = s.URLField()
    ringkasan = s.CharField()


class KegiatanDetail(Kegiatan):
    ringkasan = None
    deskripsi = s.CharField()
    deskripsi_html = s.CharField()


class KategoriRef(s.Serializer):
    slug = s.CharField()
    nama = s.CharField()


class Berita(s.Serializer):
    id = s.IntegerField()
    slug = s.CharField()
    judul = s.CharField()
    kategori = KategoriRef(allow_null=True)
    is_pengumuman = s.BooleanField()
    gambar_url = s.URLField(allow_null=True)
    tanggal = s.DateTimeField()
    hijriah = s.CharField()
    web_url = s.URLField()
    ringkasan = s.CharField()


class BeritaDetail(Berita):
    ringkasan = None
    isi = s.CharField()
    isi_html = s.CharField()
    diperbarui = s.DateTimeField()


class Kategori(KategoriRef):
    count = s.IntegerField()


class KategoriList(s.Serializer):
    results = Kategori(many=True)


class PerKategori(s.Serializer):
    kategori = s.CharField()
    jenis = s.ChoiceField(choices=['pemasukan', 'pengeluaran'])
    total = s.IntegerField()


class JenisKas(s.Serializer):
    value = s.ChoiceField(choices=['pemasukan', 'pengeluaran'])
    label = s.CharField(help_text='Pemasukan | Pengeluaran')


class Transaksi(s.Serializer):
    id = s.IntegerField()
    tanggal = s.DateField()
    keterangan = s.CharField()
    kategori = s.CharField()
    jenis = JenisKas()
    jumlah = s.IntegerField()


class Keuangan(s.Serializer):
    bulan = s.CharField()
    saldo_awal = s.IntegerField()
    pemasukan = s.IntegerField()
    pengeluaran = s.IntegerField()
    saldo_akhir = s.IntegerField()
    per_kategori = PerKategori(many=True)
    transaksi = Transaksi(many=True, help_text='Maks. 200 transaksi bulan itu, terbaru dulu')
    web_url = s.URLField()


class JadwalSholatInfo(s.Serializer):
    sumber = Choice()
    lokasi = s.CharField(allow_null=True)
    latitude = s.FloatField()
    longitude = s.FloatField()
    timezone = s.CharField()


class Meta(s.Serializer):
    name = s.CharField()
    tagline = s.CharField()
    alamat = s.CharField()
    foto_url = s.URLField(allow_null=True)
    logo_url = s.URLField(allow_null=True)
    warna = s.DictField(child=s.CharField(), help_text='{primary, accent} hex')
    today = s.DateField()
    hijriah = s.CharField()
    jadwal_sholat = JadwalSholatInfo()
    features = s.DictField(child=s.BooleanField(), help_text='{keuangan, donasi}')
    links = s.DictField(child=s.URLField(), help_text='{web, jadwal_sholat, cetak_jadwal, display}')


class ProfilData(s.Serializer):
    nama = s.CharField()
    tagline = s.CharField()
    alamat = s.CharField()
    telepon = s.CharField()
    email = s.CharField()
    website = s.CharField()
    foto_url = s.URLField(allow_null=True)
    sejarah = s.CharField()
    visi = s.CharField()
    misi = s.CharField()


class Pengurus(s.Serializer):
    id = s.IntegerField()
    nama = s.CharField()
    jabatan = Choice()
    periode = s.CharField(allow_null=True)
    foto_url = s.URLField(allow_null=True)


class Fasilitas(s.Serializer):
    id = s.IntegerField()
    nama = s.CharField()
    deskripsi = s.CharField()
    icon = s.CharField(help_text='Kelas Bootstrap Icons, mis. bi-water')


class Donasi(s.Serializer):
    teks = s.CharField()
    rekening_html = s.CharField()
    qris_url = s.URLField(allow_null=True)
    daftar_donatur_url = s.URLField()


class Sosmed(s.Serializer):
    nama = s.CharField()
    url = s.URLField()


class Profil(s.Serializer):
    profil = ProfilData(allow_null=True)
    pengurus = Pengurus(many=True)
    fasilitas = Fasilitas(many=True)
    donasi = Donasi(allow_null=True, help_text='null bila pengurus menyembunyikan donasi')
    sosial_media = Sosmed(many=True)
