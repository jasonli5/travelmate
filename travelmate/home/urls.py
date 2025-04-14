from django.urls import path
from . import views
from trips.views import plan_trip

urlpatterns = [
    path('', plan_trip, name='home.index'),
    path('about', views.about, name="home.about")
]