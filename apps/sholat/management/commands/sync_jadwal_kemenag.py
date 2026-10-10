from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.sholat import kemenag
from apps.sholat.utils import get_settings


class Command(BaseCommand):
    help = 'Ambil jadwal sholat resmi Kemenag untuk bulan ini dan bulan depan.'

    def add_arguments(self, parser):
        parser.add_argument('--bulan', type=int, default=2, help='Jumlah bulan mulai bulan ini (bawaan 2).')

    def handle(self, *args, **opts):
        settings = get_settings()
        if not settings.kota_kemenag_id:
            self.stderr.write('Kode kab/kota Kemenag belum diatur.')
            return
        today = timezone.localdate()
        year, month = today.year, today.month
        for _ in range(max(1, opts['bulan'])):
            n = kemenag.fetch_month(settings.kota_kemenag_id, year, month, force=True)
            self.stdout.write(f'{year}-{month:02d}: {n} hari' if n else f'{year}-{month:02d}: GAGAL')
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
