from django.urls import path
from . import views

urlpatterns = [
    path('', views.tournaments, name="tournament"),
    path('create_tournament/', views.create_tournament, name='create_tournament'),
]
