from django.contrib import admin
from .models import Guide, Traveler, Recommendation, Trip

admin.site.register(Guide)
admin.site.register(Traveler)
admin.site.register(Trip)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
	list_display = ('city', 'name', 'state', 'type', 'popularity', 'ratings')
	search_fields = ('city', 'name', 'state', 'type')

