from django.contrib import admin
from django.urls import path
from .views import *
from deals.views import index_view, run_crawler_view

urlpatterns = [
    path('', index_view, name='index'),
    path('game/', GameList.as_view(), name='game-list'),
    path('run-crawler/', run_crawler_view, name='run-crawler'),
    path('review/', ReviewList.as_view(), name='review-list'),
]
