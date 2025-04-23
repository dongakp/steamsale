from deals.models import Game, Review, Stats
from .serializers import *
from rest_framework import generics

# 🎮 게임 리스트 API (GET, POST)
class GameListAPI(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

# 📝 리뷰 리스트 API (GET, POST)
class ReviewListAPI(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

# 📊 통계 API (GET, POST)
class StatsListAPI(generics.ListCreateAPIView):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer
