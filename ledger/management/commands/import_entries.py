import csv
import datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from ledger.models import Entry

SKIP_DESCRIPTIONS = {'total', 'amount remaining'}


def parse_date(value, default_year=None):
    value = value.strip()
    if not value:
        return None
    for fmt in ('%m/%d/%Y', '%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    if default_year:
        try:
            md = datetime.datetime.strptime(value, '%m/%d')
            return datetime.date(default_year, md.month, md.day)
        except ValueError:
            pass
    return None


class Command(BaseCommand):
    help = 'Import spending entries from a CSV export of a spreadsheet tab (Date/Description/Price in columns C, D, E)'

    def add_arguments(self, parser):
        parser.add_argument('csv_path')
        parser.add_argument('username')
        parser.add_argument('year', type=int)
        parser.add_argument('--negate', action='store_true', help='Flip the sign of every cost value on import.')

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        username = options['username']
        year = options['year']
        negate = options['negate']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'No user "{username}" found. Log into the site once first so your account gets created.')

        created = 0
        skipped = 0
        last_date = None
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header row
            for row in reader:
                if len(row) < 5:
                    skipped += 1
                    continue
                date_str, desc, cost_str = row[2], row[3], row[4]
                desc_clean = desc.strip()
                if not desc_clean or desc_clean.lower() in SKIP_DESCRIPTIONS:
                    skipped += 1
                    continue
                parsed = parse_date(date_str, default_year=year)
                if parsed is not None:
                    last_date = parsed
                entry_date = parsed or last_date
                if entry_date is None:
                    skipped += 1
                    continue
                try:
                    cost = Decimal(cost_str.strip())
                    if negate:
                        cost = -cost
                except (InvalidOperation, AttributeError):
                    skipped += 1
                    continue
                Entry.objects.create(user=user, date=entry_date, description=desc_clean, cost=cost)
                created += 1

        self.stdout.write(f'Imported {created} entries, skipped {skipped} rows.')
