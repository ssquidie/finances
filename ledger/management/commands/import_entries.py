import csv
import datetime
from decimal import Decimal, InvalidOperation
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from ledger.models import Entry

SKIP_DESCRIPTIONS = set(['total', 'amount remaining'])


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
    args = '<csv_path> <username> <year>'
    help = 'Import spending entries from a CSV export of a spreadsheet tab (Date/Description/Price in columns C, D, E). Pass --negate if this sheet records expenses as negative numbers.'
    option_list = BaseCommand.option_list + (
        make_option('--negate', action='store_true', dest='negate', default=False,
                    help='Flip the sign of every cost value on import.'),
    )

    def handle(self, *args, **options):
        if len(args) != 3:
            raise CommandError('Usage: python manage.py import_entries <csv_path> <username> <year> [--negate]')
        csv_path, username, year_str = args
        negate = options.get('negate', False)

        try:
            year = int(year_str)
        except ValueError:
            raise CommandError('Year must be a number, e.g. 2025 or 2026.')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError('No user "%s" found. Log into the site once first so your account gets created.' % username)

        created = 0
        skipped = 0
        last_date = None
        with open(csv_path, 'rb') as f:
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

        self.stdout.write('Imported %d entries, skipped %d rows.' % (created, skipped))
