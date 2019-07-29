from django.urls import path
from treasureHunt import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('room/<int:pk>/', views.RoomDetailsView.as_view()),
]


urlpatterns = format_suffix_patterns(urlpatterns)
