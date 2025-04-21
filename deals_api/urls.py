from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('game/', GameList.as_view(), name='game-list'),
    path('review/', ReviewList.as_view(), name='review-list'),
]
