from django.urls import path
from . import views

urlpatterns = [
    path('', views.plan_trip, name='home.index'),
    path('about/', views.about, name="home.about"),
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('my-trips/', views.trips_list, name='trips'),
    path('trips/delete/<int:trip_id>/', views.delete_trip, name='delete_trip'),
]