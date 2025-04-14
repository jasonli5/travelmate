from django.urls import path
from . import views

urlpatterns = [
    path('', views.trip_list, name='trip_list'),
    path('<int:pk>/', views.trip_detail, name='trip_detail'),
    path('new/', views.trip_create, name='trip_create'),
    path('<int:pk>/edit/', views.trip_update, name='trip_update'),
    path('trip-draft/<uidb64>', views.trip_draft, name='trips.draft'),
    path('plan-trip/', views.plan_trip, name='plan_trip'),
    path('my-trips/', views.trips_list, name='trips'),
]

