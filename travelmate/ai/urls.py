from django.urls import path
from . import views

urlpatterns = [
    path("suggest-activities", views.suggest_activities, name="suggest-activities"),
]
