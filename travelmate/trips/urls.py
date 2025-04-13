from django.urls import path
from . import views

urlpatterns = [
    path('trip-draft/<uidb64>', views.trip_draft, name='trips.draft')
]