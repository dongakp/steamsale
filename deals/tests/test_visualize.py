import os
from django.test import TestCase
from utils import steam_visualize
from deals.models import Game
import datetime

class SteamVisualizeTests(TestCase):
    def setUp(self):
        # 최소한의 Game 객체 하나 생성
        Game.objects.create(
            title="Test Game",
            discount_rate=50,
            original_price=20000,
            discounted_price=10000,
            review_pct=90,
            review_count=120,
            release_date=datetime.date(2024, 5, 1),
            tags="Action,Adventure",
            link="http://example.com"
        )

    def test_get_visualization_data(self):
        data = steam_visualize.get_visualization_data()

        # 반환된 각 키 확인
        self.assertIn("discount_distribution", data)
        self.assertIn("review_vs_discount", data)
        self.assertIn("release_discount_scatter", data)
        self.assertIn("monthly_release_spline", data)
        self.assertIn("wordcloud_data", data)

        self.assertIsInstance(data["wordcloud_data"], dict)

    def test_save_wordcloud_creates_file(self):
        tag_data = {"Action": 10, "Adventure": 5}
        output_path = os.path.join("static", "images", "word_cloud.png")

        # 기존 파일 삭제
        if os.path.exists(output_path):
            os.remove(output_path)

        steam_visualize.save_wordcloud(tag_data)

        # 실제 파일 생성 여부 확인
        self.assertTrue(os.path.exists(output_path))

        # 정리
        os.remove(output_path)