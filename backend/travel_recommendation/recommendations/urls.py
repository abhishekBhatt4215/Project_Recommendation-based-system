from django.urls import path
from .views import (
    RecommendationList,
    RecommendationDetail,
    GuideList,
    GuideDetail,
    TravelerList,
    TravelerDetail,
    TripList,
    TripDetail,
    RegisterView,
    AIPlanProxyView,
    AIInteractionHistoryView,
    DashboardOverviewView,
    ProfileMeView,
)

urlpatterns = [
    path('recommendations/', RecommendationList.as_view(), name='recommendation-list'),
    path('recommendations/<int:pk>/', RecommendationDetail.as_view(), name='recommendation-detail'),

    path('guides/', GuideList.as_view(), name='guide-list'),
    path('guides/<int:pk>/', GuideDetail.as_view(), name='guide-detail'),

    path('travelers/', TravelerList.as_view(), name='traveler-list'),
    path('travelers/<int:pk>/', TravelerDetail.as_view(), name='traveler-detail'),

    path('trips/', TripList.as_view(), name='trip-list'),
    path('trips/<int:pk>/', TripDetail.as_view(), name='trip-detail'),

    # for Auth
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    # AI proxy-(protected)
    path('ai/plan_trip/', AIPlanProxyView.as_view(), name='ai-plan'),
    path('ai/history/', AIInteractionHistoryView.as_view(), name='ai-history'),

    path('dashboard/overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('profile/me/', ProfileMeView.as_view(), name='profile-me'),
]