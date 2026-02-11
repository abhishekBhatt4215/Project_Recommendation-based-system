from rest_framework import generics, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Traveler, Recommendation, Trip, Guide, AIInteraction
from .serializers import (
    RecommendationSerializer,
    GuideSerializer,
    TravelerSerializer,
    TripSerializer,
    RegisterSerializer,
    AIInteractionSerializer,
    TravelerProfileSerializer,
)
from rest_framework.views import APIView , Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, SAFE_METHODS
from django.core.exceptions import PermissionDenied
from django.conf import settings
import requests


# -----------------
# Auth / Registration
# -----------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer


# AI proxy endpoint (protected)

class AIPlanProxyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = request.data
        ai_url = getattr(settings, 'AI_SERVICE_URL', 'http://localhost:8001')
        
        # Extract user prompt from payload (assume it's under 'prompt' or 'query' key)
        # Adjust key based on actual AI service request format
        user_prompt = payload.get('prompt') or payload.get('query') or str(payload)
        
        try:
            resp = requests.post(f"{ai_url}/trip", json=payload, timeout=60)
            print("=== AI RESPONSE STATUS ===", resp.status_code)
            print("=== AI RESPONSE TEXT ===", resp.text)
        except requests.RequestException as e:
            print("=== AI CONNECTION ERROR ===", str(e))
            return Response({'detail': str(e)}, status=502)
        except Exception as e:
            print("=== UNKNOWN ERROR ===", str(e))
            return Response({'detail': str(e)}, status=502)


        try:
            data = resp.json()
        except ValueError:
            return Response({'detail': 'Invalid response from AI service'}, status=status.HTTP_502_BAD_GATEWAY)

        # Save AI interaction to database
        ai_response_text = str(data)  # Convert response to string for storage
        AIInteraction.objects.create(
            user=request.user,
            prompt=user_prompt,
            ai_response=ai_response_text
        )

        return Response(data, status=resp.status_code)



class RecommendationList(generics.ListCreateAPIView):
    """List recommendations and allow creating new ones (POST requires admin)."""
    queryset = Recommendation.objects.all().order_by('id')
    serializer_class = RecommendationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'state', 'type']
    search_fields = ['city', 'name', 'state', 'type', 'place']
    ordering_fields = ['ratings', 'popularity', 'city']

    def get_permissions(self):
        # Allow anyone to read, but restrict write operations to admin users
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAdminUser()]


class RecommendationDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a recommendation. Unsafe methods require admin."""
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAdminUser()]


class GuideList(generics.ListCreateAPIView):
    queryset = Guide.objects.all().order_by('id')
    serializer_class = GuideSerializer


class GuideDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer


class TravelerList(generics.ListAPIView):
    """List traveler profile. POST (create) is disabled for clients; traveler profiles are auto-created on user signup."""
    serializer_class = TravelerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Traveler.objects.all().order_by('id')
        return Traveler.objects.filter(user=user)


class TravelerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Traveler.objects.all()
    serializer_class = TravelerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the traveler's profile for the requesting user (or allow staff to access by pk)
        if self.request.user.is_staff:
            return super().get_object()
        # ensure the user has a traveler profile (signals should create it on user creation)
        return Traveler.objects.get(user=self.request.user)


class TripList(generics.ListCreateAPIView):
    queryset = Trip.objects.all().order_by('id')
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Enforce authentication explicitly to avoid accidental anonymous creation
        if not request.user or not request.user.is_authenticated:
            return Response({'detail': 'Authentication credentials were not provided.'}, status=401)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        # ensure traveler belongs to requesting user (if traveler provided)
        traveler = serializer.validated_data.get('traveler')
        if traveler and traveler.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied('Cannot create trip for another user')
        serializer.save()


class TripDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer



# AI History endpoint 

class AIInteractionHistoryView(generics.ListAPIView):
    """Retrieve authenticated user's AI interaction history (read-only)."""
    serializer_class = AIInteractionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Return all records for simplicity
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Newest first

    def get_queryset(self):
        # Only return interactions for the authenticated user, ordered by newest first
        return AIInteraction.objects.filter(user=self.request.user).order_by('-created_at')



# Dashboard endpoint

class DashboardOverviewView(APIView):
    """Return aggregated user-specific dashboard data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        
        try:
            traveler = Traveler.objects.get(user=user)
            total_trips = traveler.trips.count()
        except Traveler.DoesNotExist:
            total_trips = 0
        
        # Count AI interactions
        ai_interactions_count = AIInteraction.objects.filter(user=user).count()
        
        # Build response
        data = {
            'username': user.username,
            'total_trips': total_trips,
            'ai_interactions': ai_interactions_count,
            'member_since': user.date_joined
        }
        
        return Response(data, status=status.HTTP_200_OK)


# -----------------
# Profile endpoint (user's own profile)
# -----------------
class ProfileMeView(APIView):
    """Get or update the authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the authenticated user's profile data."""
        user = request.user
        try:
            traveler = Traveler.objects.get(user=user)
        except Traveler.DoesNotExist:
            return Response({'detail': 'Traveler profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TravelerProfileSerializer(traveler, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Update the authenticated user's profile (partial updates allowed)."""
        user = request.user
        try:
            traveler = Traveler.objects.get(user=user)
        except Traveler.DoesNotExist:
            return Response({'detail': 'Traveler profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Allow partial updates (PATCH-like behavior with PUT)
        serializer = TravelerProfileSerializer(
            traveler,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)