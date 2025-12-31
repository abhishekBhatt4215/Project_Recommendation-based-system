
from django.db import models
from django.contrib.auth.models import User

class Guide(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    languages = models.CharField(max_length=200, blank=True)
    rating = models.FloatField(default=0)
    city = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100, blank=True)

class Traveler(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    featured = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profiles/', blank=True, null=True)

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
      
class Trip(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='trips')
    recommendations = models.ManyToManyField(Recommendation)
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)	  
    

# Create your models here.
