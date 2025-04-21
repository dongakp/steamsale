from rest_framework import serializers
from deals.models import *

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['game','rating','content']
        
class GameSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True,read_only=True)
    class Meta:
        model = Game
        fields = ['id','title','original_price','discount_price','discount_percent','steam_link','reviews']