from django.urls import path
from .views import (
    MissionGoalListCreateView,
    MissionGoalDetailView,
    MissionGoalCompleteView,
    MissionGoalCancelView,
)

urlpatterns = [
    path("", MissionGoalListCreateView.as_view(), name="mission-list-create"),
    path("<int:pk>/", MissionGoalDetailView.as_view(), name="mission-detail"),
    path(
        "<int:pk>/complete/", MissionGoalCompleteView.as_view(), name="mission-complete"
    ),
    path("<int:pk>/cancel/", MissionGoalCancelView.as_view(), name="mission-cancel"),
]
