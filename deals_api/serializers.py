from rest_framework import serializers
from deals.models import *

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['game','rating','content']
        
class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stats
        fields = ['discount_rate','discount_rate_density']
        
class GameSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True,read_only=True)
    class Meta:
        model = Game
        fields = ["id","title", "discount_rate", "original_price", "discounted_price", "review_pct", "review_count", "release_date", "tags", "link", "reviews"]