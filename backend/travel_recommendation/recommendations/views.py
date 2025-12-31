from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Traveler, Recommendation, Trip
from .serializers import RecommendationSerializer 
from rest_framework.views import APIView , Response
from .serializers import TravelerSerializer


class RecommendationList(generics.ListAPIView):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['city', 'state', 'type']  
    search_fields = ['city', 'name', 'state', 'type', 'place']  

class RecommendationDetail(generics.RetrieveAPIView):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer


class TravelerDetail(APIView):
    def get(self, request):
        traveler = Traveler.objects.get(user=request.user)

        # ✅ WRITE IT HERE
        serializer = TravelerSerializer(
            traveler,
            context={'request': request}
        )

        return Response(serializer.data)
