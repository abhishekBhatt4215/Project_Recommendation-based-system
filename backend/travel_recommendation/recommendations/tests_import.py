import os
import tempfile
import csv
from django.core.management import call_command
from django.test import TestCase
from recommendations.models import Recommendation


class ImportRecommendationsTest(TestCase):
    def test_import_creates_recommendations_and_handles_invalid_numbers(self):
        # Create a temporary CSV file
        fd, path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        try:
            with open(path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'city', 'ratings', 'ideal_duration', 'best_time_to_visit', 'city_desc',
                    'destinationid', 'name', 'state', 'type', 'popularity', 'place',
                    'ratings_place', 'distance', 'place_desc'
                ])
                writer.writerow(['TestCity', '4.5', '3', 'spring', 'A nice city', 'dest-1', 'Place A', 'TS', 'urban', '0.8', 'Place', '4.0', '10', 'Nice place'])
                # invalid numeric values should be handled safely and set to None
                writer.writerow(['OtherCity', 'not_a_number', '', '', '', '', '', '', '', 'not_a_number', '', 'NaN', '', ''])

            # Ensure table is empty
            Recommendation.objects.all().delete()

            # Run the import command with truncate
            call_command('import_recommendations', path, '--truncate')

            # After import we expect 2 records
            qs = Recommendation.objects.all()
            self.assertEqual(qs.count(), 2)

            rec1 = Recommendation.objects.get(city='TestCity')
            self.assertEqual(rec1.ratings, 4.5)
            self.assertEqual(rec1.ideal_duration, 3.0)
            self.assertEqual(rec1.popularity, 0.8)
            self.assertEqual(rec1.ratings_place, 4.0)

            rec2 = Recommendation.objects.get(city='OtherCity')
            # invalid numeric values should result in None
            self.assertIsNone(rec2.ratings)
            self.assertIsNone(rec2.popularity)

        finally:
            os.remove(path)
