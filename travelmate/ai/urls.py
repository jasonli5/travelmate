from django.urls import path
from . import views

urlpatterns = [
    path("suggest-activities", views.SuggestActivitiesAPI.as_view(), name="suggest-activities_api"),
    path("additional-info", views.AdditionalInfoAPI.as_view(), name="additional-info_api"),
]
