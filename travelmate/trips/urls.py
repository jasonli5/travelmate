from django.urls import path
from . import views



urlpatterns = [
    path('trip-draft/', views.trip_draft, name='trips.draft'),
    path('travel_recs/',views.travel_recs, name='travel_recs'),
    path('add_travel_recs/',views.add_travel_recs, name='add_travel_recs'),
    path('edit_trip/<uidb64>/<int:trip_id>', views.edit_trip, name='edit.trip'),
    path('travel_recs/',views.travel_recs, name='travel_recs'),
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('my-trips/', views.trips_list, name='trips'),
    path('trips/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
    path('<int:trip_id>/edit/', views.edit_trip, name='edit_trip'),
    path('generate-weather/<int:trip_id>/', views.generate_weather_view, name='generate_weather'),
]