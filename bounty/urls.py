
from django.urls import path
from . import views

urlpatterns = [
    path(
        "api/criminals/",
        views.criminal_list,
        name="criminal_list"
    ),
    path(
        "api/criminals/<int:criminal_id>/",
        views.criminal_detail,
        name="criminal_detail"
    ),
    path(
        "api/hunts/",
        views.hunt_list,
        name="hunt_list"
    ),
    path(
        "api/hunts/<int:hunt_id>/",
        views.hunt_detail,
        name="hunt_detail"
    ),
]
