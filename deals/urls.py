from django.urls import path
from . import views
from .views import run_crawler_view, index_view

urlpatterns = [
    path('', index_view, name='index'),
    path('games/', views.game_list, name='game-list'),
    path('run-crawler/', run_crawler_view, name='run-crawler'),
    path('games/<int:pk>/', views.game_detail, name='game-detail'),
    path('games/statistics/', views.game_statistics, name='game-statistics'),
]
