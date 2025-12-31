
from django.db import models

class Recommendation(models.Model):
	city = models.CharField(max_length=100)
	ratings = models.FloatField(null=True, blank=True)
	ideal_duration = models.FloatField(null=True, blank=True)
	best_time_to_visit = models.CharField(max_length=100, null=True, blank=True)
	city_desc = models.TextField(null=True, blank=True)
	destinationid = models.CharField(max_length=100, null=True, blank=True)
	name = models.CharField(max_length=200, null=True, blank=True)  # Place or destination name
	state = models.CharField(max_length=100, null=True, blank=True)
	type = models.CharField(max_length=100, null=True, blank=True)
	popularity = models.FloatField(null=True, blank=True)
	place = models.CharField(max_length=200, null=True, blank=True)
	ratings_place = models.FloatField(null=True, blank=True)
	distance = models.FloatField(null=True, blank=True)
	place_desc = models.TextField(null=True, blank=True)

	def __str__(self):
		return f"{self.city} - {self.name}"

# Create your models here.
