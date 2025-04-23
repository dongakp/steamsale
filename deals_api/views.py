from deals.models import Game, Review
from .serializers import *
from rest_framework import generics

class GameListAPI(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class ReviewListAPI(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class StatsListAPI(generics.ListCreateAPIView):
    queryset = Stats.objects.all()
    serializer_class = StatsSerializer