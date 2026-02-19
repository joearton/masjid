import random
from datetime import datetime, date, timedelta, time
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

from apps.berita.models import Berita, KategoriBerita
from apps.kegiatan.models import Kegiatan
from apps.keuangan.models import KategoriKeuangan, TransaksiKeuangan
from apps.profil.models import ProfilMasjid, PeriodePengurus, Pengurus, Fasilitas
from apps.donatur.models import Donatur
from apps.display.models import DisplaySettings, DisplaySlide
from apps.sholat.models import SholatSettings, JadwalJumat

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating dummy data...')
        
        self.create_users()
        self.create_profil()
        self.create_display_settings()
        self.create_sholat_settings()
        self.create_berita()
        self.create_kegiatan()
        self.create_keuangan()
        self.create_donatur()
        self.create_jadwal_jumat()
        self.create_pengurus_fasilitas()

        self.stdout.write(self.style.SUCCESS('Successfully populated database with dummy data!'))

    def create_users(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write('Created superuser: admin/admin')
        
        if not User.objects.filter(username='staff').exists():
            user = User.objects.create_user('staff', 'staff@example.com', 'staff')
            user.is_staff = True
            user.save()
            self.stdout.write('Created staff user: staff/staff')

    def create_profil(self):
        # Gunakan update_or_create agar data selalu ter-refresh dengan data dummy yang lengkap
        ProfilMasjid.objects.update_or_create(
            id=1, # Asumsi hanya ada 1 profil
            defaults={
                'nama': 'Masjid Al-Ikhlas',
                'tagline': 'Masjid yang Makmur dan Sejahtera',
                'sejarah': 'Masjid ini didirikan pada tahun 2000 oleh warga sekitar untuk memfasilitasi kegiatan ibadah dan sosial. Bermula dari musholla kecil, kini telah berkembang menjadi pusat kegiatan umat.',
                'visi': 'Menjadi pusat ibadah dan pembinaan umat yang rahmatan lil alamin, modern, dan profesional.',
                'misi': '1. Memakmurkan masjid dengan sholat berjamaah dan kegiatan dakwah.\n2. Mengembangkan potensi ekonomi dan sosial umat.\n3. Menyelenggarakan pendidikan Islam yang berkualitas.\n4. Menjaga dan memelihara fasilitas masjid.',
                'alamat': 'Jl. Damai Sejahtera No. 123, Kelurahan Kebujian, Kecamatan Kebaikan, Jakarta Selatan, 12345',
                'telepon': '021-12345678',
                'email': 'sekretariat@masjid-alikhlas.id',
                'website': 'https://masjid-alikhlas.id',
                'maps_embed': '<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d126907.036062778!2d106.788506!3d-6.284486!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x2e69f1ec2422b42d%3A0x2bc3600dd632f7d3!2sMasjid%20Istiqlal!5e0!3m2!1sid!2sid!4v1650000000000!5m2!1sid!2sid" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
            }
        )
        self.stdout.write('Updated/Created Profil Masjid')

    def create_display_settings(self):
        if not DisplaySettings.objects.exists():
            DisplaySettings.objects.create(
                nama='Display Utama',
                tema='default',
                running_text='Selamat Datang di Masjid Al-Ikhlas. Jagalah kebersihan dan ketertiban.',
                aktif=True
            )
            self.stdout.write('Created Display Settings')

        if not DisplaySlide.objects.exists():
            slides = [
                {'judul': 'Jadwal Sholat', 'tipe': 'sholat', 'urutan': 1},
                {'judul': 'Laporan Kas', 'tipe': 'kas', 'urutan': 2},
                {'judul': 'Kajian Rutin', 'tipe': 'kegiatan', 'urutan': 3},
                {'judul': 'Berita Terkini', 'tipe': 'berita', 'urutan': 4},
                {'judul': 'Himbauan', 'tipe': 'teks', 'konten_teks': 'Mohon nonaktifkan HP saat sholat berjamaah.', 'urutan': 5},
            ]
            for s in slides:
                DisplaySlide.objects.create(**s)
            self.stdout.write(f'Created {len(slides)} Display Slides')

    def create_sholat_settings(self):
        if not SholatSettings.objects.exists():
            SholatSettings.objects.create(
                latitude=-6.2088,
                longitude=106.8456,
                timezone='Asia/Jakarta',
                koreksi_subuh=2,
                koreksi_dzuhur=2,
                koreksi_ashar=2,
                koreksi_maghrib=2,
                koreksi_isya=2
            )
            self.stdout.write('Created Sholat Settings')

    def create_berita(self):
        kategori_list = ['Pengumuman', 'Artikel', 'Kegiatan', 'Berita Duka']
        kategori_objs = []
        for kat in kategori_list:
            obj, _ = KategoriBerita.objects.get_or_create(nama=kat)
            kategori_objs.append(obj)
        
        titles = [
            'Penerimaan Hewan Qurban 1446H',
            'Kajian Rutin Bulanan Bersama Ustadz Fulan',
            'Laporan Keuangan Pembangunan Toilet',
            'Gotong Royong Membersihkan Masjid',
            'Innalillahi, Telah Berpulang Bapak H. Ahmad'
        ]
        
        if Berita.objects.count() < 5:
            for i, title in enumerate(titles):
                Berita.objects.create(
                    judul=title,
                    slug=slugify(title),
                    kategori=random.choice(kategori_objs),
                    isi=f'Ini adalah konten dummy untuk berita "{title}". Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
                    is_published=True,
                    is_pengumuman=(i % 2 == 0)
                )
            self.stdout.write(f'Created {len(titles)} Berita')

    def create_kegiatan(self):
        titles = [
            'Kajian Subuh', 'Buka Puasa Bersama', 'Pesantren Kilat', 'Rapat DKM', 'Santunan Anak Yatim'
        ]
        if Kegiatan.objects.count() < 5:
            today = date.today()
            for i, title in enumerate(titles):
                Kegiatan.objects.create(
                    judul=title,
                    deskripsi=f'Kegiatan {title} yang akan dilaksanakan di masjid kita tercinta.',
                    tanggal=today + timedelta(days=i*2),
                    waktu_mulai=time(8+i, 0), # 08:00, 09:00, etc.
                    waktu_selesai=time(10+i, 0),
                    tempat='Ruang Utama Masjid Al-Ikhlas',
                    narasumber='Ustadz Fulan S.Ag' if i % 2 == 0 else 'Panitia',
                    status='upcoming'
                )
            self.stdout.write(f'Created {len(titles)} Kegiatan')

    def create_keuangan(self):
        kat_pemasukan, _ = KategoriKeuangan.objects.get_or_create(nama='Infaq Jumat', jenis='pemasukan')
        kat_pengeluaran, _ = KategoriKeuangan.objects.get_or_create(nama='Listrik & Air', jenis='pengeluaran')
        kat_donasi, _ = KategoriKeuangan.objects.get_or_create(nama='Donasi Pembangunan', jenis='pemasukan')
        kat_gaji, _ = KategoriKeuangan.objects.get_or_create(nama='Gaji Marbot', jenis='pengeluaran')
        
        categories = [kat_pemasukan, kat_pengeluaran, kat_donasi, kat_gaji]
        
        if TransaksiKeuangan.objects.count() < 10:
            today = date.today()
            for i in range(10):
                cat = random.choice(categories)
                amount = random.randint(100, 5000) * 1000
                TransaksiKeuangan.objects.create(
                    tanggal=today - timedelta(days=i),
                    kategori=cat,
                    keterangan=f'Transaksi dummy {cat.nama}',
                    jumlah=amount
                )
            self.stdout.write('Created 10 Transaksi Keuangan')

    def create_donatur(self):
        names = ['H. Budi', 'Ibu Siti', 'Keluarga Bapak Joko', 'Hamba Allah', 'CV. Maju Jaya']
        if Donatur.objects.count() < 5:
            for name in names:
                Donatur.objects.create(
                    nama=name,
                    tipe=random.choice(['tetap', 'tidak_tetap']),
                    status='aktif',
                    alamat='Jl. Contoh No. 1, Jakarta',
                    telepon='08123456789',
                    komitmen_rutin=500000 if random.choice([True, False]) else 0,
                    tipe_rutin='bulanan'
                )
            self.stdout.write(f'Created {len(names)} Donatur')

    def create_jadwal_jumat(self):
        if JadwalJumat.objects.count() < 4:
            today = date.today()
            # Find next friday
            friday = today + timedelta((4 - today.weekday()) % 7)
            
            for i in range(4):
                curr_date = friday + timedelta(weeks=i)
                JadwalJumat.objects.create(
                    tanggal=curr_date,
                    khatib=f'Ustadz Khatib {i+1}',
                    imam=f'Ustadz Imam {i+1}',
                    tema=f'Tema Khutbah Jumat ke-{i+1}: Keutamaan Beribadah'
                )
            self.stdout.write('Created 4 Jadwal Jumat')

    def create_pengurus_fasilitas(self):
        periode, _ = PeriodePengurus.objects.get_or_create(
            nama='Periode 2024-2029',
            defaults={'tahun_mulai': 2024, 'tahun_selesai': 2029, 'aktif': True}
        )
        
        # Reset pengurus untuk periode ini agar tidak duplikat saat dijalankan ulang
        # Pengurus.objects.filter(periode=periode).delete() 
        # (Optional: uncomment jika ingin reset total, tapi kita pakai get_or_create saja di bawah atau cek count)

        roles = [
            ('H. Ahmad Dahlan', 'Ketua DKM', 'ketua'),
            ('H. Budi Santoso', 'Wakil Ketua', 'wakil_ketua'),
            ('Ust. Zakaria', 'Sekretaris', 'sekretaris'),
            ('Bpk. Irfan Hakim', 'Bendahara', 'bendahara'),
            ('Sdr. Rahmat', 'Anggota Bidang Dakwah', 'anggota'),
            ('Sdr. Yudi', 'Anggota Bidang Pembangunan', 'anggota'),
            ('Sdr. Anto', 'Anggota Bidang Kebersihan', 'anggota'),
            ('Sdr. Dedi', 'Anggota Bidang Keamanan', 'anggota'),
        ]
        
        # Tambahkan jika belum ada (cek nama saja simple-nya)
        count_added = 0
        for i, (nama, role_desc, role_key) in enumerate(roles):
            if not Pengurus.objects.filter(nama=nama, periode=periode).exists():
                Pengurus.objects.create(
                    periode=periode,
                    nama=nama,
                    jabatan=role_key,
                    urutan=i+1,
                    aktif=True
                )
                count_added += 1
        
        if count_added > 0:
            self.stdout.write(f'Added {count_added} Pengurus baru')
        else:
            self.stdout.write('Pengurus data already exists')

        fasilitas_data = [
            ('Ruang Utama Ber-AC', 'Ruang sholat utama yang nyaman dengan pendingin ruangan.', 'bi-snow'),
            ('Perpustakaan Islami', 'Koleksi buku-buku agama yang lengkap untuk jamaah.', 'bi-book'),
            ('Aula Serbaguna', 'Dapat digunakan untuk resepsi atau pertemuan warga.', 'bi-building'),
            ('Area Parkir Luas', 'Parkir motor dan mobil yang aman dan luas.', 'bi-p-square'),
            ('Kamar Mandi & Wudhu', 'Fasilitas bersuci yang bersih dan terawat.', 'bi-droplet'),
            ('Akses Disabilitas', 'Ramah untuk pengguna kursi roda.', 'bi-person-wheelchair'),
            ('Taman Masjid', 'Area hijau untuk kenyamanan visual.', 'bi-tree'),
        ]
        
        count_fasilitas = 0
        for nama, deskripsi, icon in fasilitas_data:
            if not Fasilitas.objects.filter(nama=nama).exists():
                Fasilitas.objects.create(
                    nama=nama,
                    deskripsi=deskripsi,
                    icon=icon,
                    aktif=True
                )
                count_fasilitas += 1
                
        if count_fasilitas > 0:
            self.stdout.write(f'Added {count_fasilitas} Fasilitas')
