from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from deals.models import Game, Review

class GameAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api-game-list')

    def test_game_list_empty(self):
        # 데이터 없을 때 빈 리스트 반환 
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])

    def test_game_list_with_one(self):
        g = Game.objects.create(
            title="TestGame",
            discount_rate=10,
            original_price=1000,
            discounted_price=900,
            review_pct=80,
            review_count=2,
            release_date="2025-04-01",
            tags="action,indie",
            link="http://example.com"
        )
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # 리스트 길이
        self.assertEqual(len(resp.data), 1)
        # 첫 번째 아이템 필드
        item = resp.data[0]
        self.assertEqual(item['id'], g.id)
        self.assertEqual(item['title'], "TestGame")
        self.assertEqual(item['discount_rate'], 10)
        self.assertEqual(item['original_price'], 1000)
        self.assertEqual(item['discounted_price'], 900)
        # reviews 는 아직 없으니 빈 배열
        self.assertEqual(item['reviews'], [])

