from django.urls import path
from . import views

urlpatterns = [
    path('trip-draft/<uidb64>', views.trip_draft, name='trips.draft'),
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('my-trips/', views.trips_list, name='trips'),
    path('trips/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
]