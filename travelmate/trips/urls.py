from django.urls import path
from . import views


app_name = 'trips'

urlpatterns = [
    path('travel_recs/',views.travel_recs, name='travel_recs'),
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('my-trips/', views.trips_list, name='trips'),
    path('trips/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
]