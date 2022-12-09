from django.urls import path
from . import views

urlpatterns = [
    path('flights', views.flights_page),
    path('flights/<str:flightNum>', views.flight_info),
    path('manage/health', views.manage)
]
