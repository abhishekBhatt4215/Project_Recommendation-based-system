import csv
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from recommendations.models import Recommendation


def _safe_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class Command(BaseCommand):
    help = 'Import recommendations from a CSV file using batched bulk_create for performance.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to the CSV file to import')
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of objects to create per bulk_create call (default: 1000)'
        )
        parser.add_argument(
            '--truncate',
            action='store_true',
            help='Truncate the Recommendation table before importing'
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        batch_size = options['batch_size']
        truncate = options['truncate']

        start = time.time()
        created = 0
        objs = []

        if truncate:
            self.stdout.write('Truncating existing Recommendation records...')
            Recommendation.objects.all().delete()

        with open(csv_path, encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for i, row in enumerate(reader, start=1):
                try:
                    obj = Recommendation(
                        city=row.get('city', '') or None,
                        ratings=_safe_float(row.get('ratings')),
                        ideal_duration=_safe_float(row.get('ideal_duration')),
                        best_time_to_visit=row.get('best_time_to_visit') or None,
                        city_desc=row.get('city_desc') or None,
                        destinationid=row.get('destinationid') or None,
                        name=row.get('name') or None,
                        state=row.get('state') or None,
                        type=row.get('type') or None,
                        popularity=_safe_float(row.get('popularity')),
                        place=row.get('place') or None,
                        ratings_place=_safe_float(row.get('ratings_place')),
                        distance=_safe_float(row.get('distance')),
                        place_desc=row.get('place_desc') or None,
                    )
                    objs.append(obj)

                    if len(objs) >= batch_size:
                        with transaction.atomic():
                            Recommendation.objects.bulk_create(objs, batch_size=batch_size)
                        created += len(objs)
                        self.stdout.write(f'Imported {created} rows...')
                        objs = []

                except Exception as e:
                    self.stderr.write(f'Error processing row {i}: {e}')
                    continue

        # Insert any remaining objects
        if objs:
            with transaction.atomic():
                Recommendation.objects.bulk_create(objs, batch_size=batch_size)
            created += len(objs)

        elapsed = time.time() - start
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {created} recommendations in {elapsed:.1f}s'))
