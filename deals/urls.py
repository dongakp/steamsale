from django.urls import path
from . import views
from .views import run_crawler_view, index_view, dashboard_view, charts_view
from .views import visualization_json_view


urlpatterns = [
    path('', index_view, name='index'),
    path('dashboard', dashboard_view, name='dashboard'),  
    path('games/', views.game_list, name='game-list'),
    path('run-crawler/', run_crawler_view, name='run-crawler'),
    path('games/<int:pk>/', views.game_detail, name='game-detail'),
    path('games/statistics/', views.game_statistics, name='game-statistics'),
    path("visualization-data/", visualization_json_view, name="visualization-json"),
    path('charts/', charts_view, name='charts'),
]
