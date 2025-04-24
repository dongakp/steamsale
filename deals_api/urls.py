# deals_api/urls.py 

from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('game/', GameListAPI.as_view(), name='api-game-list'),
    path('review/', ReviewListAPI.as_view(), name='api-review-list'),
]
