from django.test import TestCase
from deals.models import Game, Review
import datetime

class ModelStrTest(TestCase):
    def test_game_str(self):
        game = Game(
            title="Test Game",
            discount_rate=20,
            original_price=5000,
            discounted_price=4000,
            review_pct=95,
            review_count=1000,
            release_date=datetime.date.today(),
            tags="Action,Adventure",
            link="http://example.com"
        )
        expected = "Test Game: 4000 (-20%%)"
        self.assertEqual(str(game), expected)

    def test_review_str(self):
        game = Game(
            title="Review Game",
            discount_rate=30,
            original_price=10000,
            discounted_price=7000,
            review_pct=80,
            review_count=800,
            release_date=datetime.date.today(),
            tags="RPG",
            link="http://example.com/review"
        )
        review = Review(
            game=game,
            rating="Very Positive",
            content="Great game!"
        )
        expected = f"{str(game)}: Very Positive"
        self.assertEqual(str(review), expected)
