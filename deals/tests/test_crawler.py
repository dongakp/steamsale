from django.test import TestCase
import pandas as pd
from utils.steam_crawler import crawler, NoSearchResult
from unittest.mock import patch


class CrawelerTests(TestCase):
    def setUp(self):
        # 공통 Dummy HTML
        # 검색 결과 더미 HTML
        self.search_html = '''
        <a class="search_result_row" href="http://fake">
            <div class="title">Dummy Game</div>
            <div class="discount_final_price">₩10,000</div>
            <div class="discount_original_price">₩20,000</div>
            <div class="discount_pct">-50%</div>
            <div class="search_review_summary"
                data-tooltip-html="90% of 100 user reviews"></div>
        </a>
        '''
        # 상세 페이지 더미 HTML
        self.detail_html = """
        <div class="release_date"><span class="date">Apr 1, 2025</span></div>
        <div class="glance_tags popular_tags">
            <a class="app_tag">Action</a>
            <a class="app_tag">Adventure</a>
        </div>
        """
    class DummyResponse:
        def __init__(self, text, status_code=200):
            self.text = text
            self.status_code = status_code
        def raise_for_status(self):
            if self.status_code != 200:
                raise Exception(f"HTTP {self.status_code}")

    # test_crawler_success : 정상 케이스
    @patch('utils.steam_crawler.requests.get')
    def test_crawler_success(self, mock_get):
        def fake_get(url, headers=None):
            return self.DummyResponse(self.search_html if "search/?" in url else self.detail_html)
        mock_get.side_effect = fake_get
        
        df = crawler(category="action", count=1)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        # 컬럼명 체크
        expected_cols = [
            "title","discount_rate","original_price","discounted_price",
            "review_pct","review_count","release_date","tags","link"
        ]
        self.assertListEqual(list(df.columns), expected_cols)

        row = df.iloc[0]
        self.assertEqual(row.title, "Dummy Game")
        self.assertEqual(row.discount_rate, 50)
        self.assertEqual(row.original_price, 20000)
        self.assertEqual(row.discounted_price, 10000)
        self.assertEqual(row.review_pct, 90)
        self.assertEqual(row.review_count, 100)
        self.assertIn("Action", row.tags)

    # category 없음
    def test_crawler_invalid_category(self):
        with self.assertRaises(NoSearchResult):
            crawler(category="invalid", count=1)

    # count가 0일 때
    def test_crawler_zero_count(self):
        with self.assertRaises(NoSearchResult):
            crawler(category="action", count=0)

    # count가 매우 클 때 (성능은 측정하지 않지만 에러 발생 여부만 테스트)
    @patch('utils.steam_crawler.requests.get')
    def test_crawler_large_count(self, mock_get):
        def fake_get(url, headers=None):
            return self.DummyResponse(self.search_html if "search/?" in url else self.detail_html)
        mock_get.side_effect = fake_get

        df = crawler(category="action", count=100)
        self.assertIsInstance(df, pd.DataFrame)