from rest_framework import serializers
from .models import Recommendation , Traveler , Trip , Guide

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'

class TravelerSerializer(serializers.ModelSerializer):
    profile_recommendations = RecommendationSerializer()

    class Meta:
        model = Traveler
        fields = ('id', 'user', 'bio', 'featured', 'profile_pic')

    def get_profile_pic(self,obj):
         if obj.profile_pic:
            request = self.context.get('request', None)
            if request is not None:
                return request.build_absolute_uri(obj.profile_pic.url)
            return obj.profile_pic.url
         return None 

