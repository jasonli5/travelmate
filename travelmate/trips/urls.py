from django.urls import path
from . import views
from .views import export_trip_pdf



urlpatterns = [
    path('trip-draft/', views.trip_draft, name='trips.draft'),
    path('travel_recs/',views.travel_recs, name='travel_recs'),
    path('add_travel_recs/',views.add_travel_recs, name='add_travel_recs'),
    path('travel_recs/',views.travel_recs, name='travel_recs'),
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('my-trips/', views.trips_list, name='trips'),
    path('shared-trips/', views.shared_trips_list, name='shared_trips'),
    path('trips/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
    path('<int:trip_id>/edit/', views.edit_trip, name='edit_trip'),
    path('generate-weather/<int:trip_id>/', views.generate_weather_view, name='generate_weather'),
    path('trips/invite/<int:trip_id>/', views.invite_collaborator, name='invite_collaborator'),
    path('trip/<int:trip_id>/pdf/', export_trip_pdf, name='export_trip_pdf'),
    path('trips/<int:trip_id>/remove-collaborator/<int:user_id>/', views.remove_collaborator, name='remove_collaborator'),
]

