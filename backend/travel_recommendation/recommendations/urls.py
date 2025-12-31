from django.urls import path
from .views import RecommendationList, RecommendationDetail
# from .views import TravelerListView   

urlpatterns = [
    # path("travelers/", TravelerListView.as_view()),
    path('recommendations/', RecommendationList.as_view(), name='recommendation-list'),
    path('recommendations/<int:pk>/', RecommendationDetail.as_view(), name='recommendation-detail'),
]   