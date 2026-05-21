from django.urls import path
from . import views

urlpatterns = [
    path('', views.billboard_view, name='billboard'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('event/create/', views.create_event_view, name='create_event'),
    path('location/create/', views.create_location_view, name='create_location'),
]
