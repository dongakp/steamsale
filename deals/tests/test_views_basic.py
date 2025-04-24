# deals/tests/test_views_basic.py

from django.test import TestCase, Client
from django.urls import reverse
from deals.models import Game
import datetime

class ViewBasicTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_game_list_view(self):
        response = self.client.get(reverse("game-list"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_charts_view(self):
        response = self.client.get(reverse("charts"))
        self.assertEqual(response.status_code, 200)

    def test_visualization_json_view(self):
        response = self.client.get(reverse("visualization-json"))
        self.assertEqual(response.status_code, 200)

    def test_game_statistics_view(self):
        response = self.client.get(reverse("game-statistics"))
        self.assertEqual(response.status_code, 200)

    def test_game_detail_view(self):
        # game_detail은 pk가 필요해서 Game 객체 먼저 생성
        game = Game.objects.create(
            title="테스트 게임",
            discount_rate=10,
            original_price=10000,
            discounted_price=9000,
            review_pct=90,
            review_count=100,
            release_date=datetime.date.today(),
            tags="Action,Adventure",
            link="https://example.com"
        )
        response = self.client.get(reverse("game-detail", args=[game.id]))
        self.assertEqual(response.status_code, 200)
