from django.test import SimpleTestCase
from unittest.mock import patch
import pandas as pd
from utils.steam_crawler import crawler, NoSearchResult


class SteamCrawlerTest(SimpleTestCase):
    @patch('requests.get')
    def test_crawler_success(self, mock_get):
        # DummyResponse 정의
        class DummyResponse:
            def __init__(self, text, status_code=200):
                self.text = text
                self.status_code = 200
            def raise_for_status(self):
                pass

        # 1)검색 결과용 더미 HTML
        search_html = '''
        <a class="search_result_row" href="http://fake">
            <div class="title">Dummy Game</div>
            <div class="discount_final_price">₩10,000</div>
            <div class="discount_original_price">₩20,000</div>
            <div class="discount_pct">-50%</div>
            <div class="search_review_summary"
                data-tooltip-html="90% of 100 user reviews"></div>
        </a>
        '''
        # 2) 상세 페이지용 더미 HTML
        detail_html = '''
        <div class="release_date"><span class="date">Apr 1, 2025</span></div>
        <div class="glance_tags popular_tags">
            <a class="app_tag">Action</a>
            <a class="app_tag">Adventure</a>
        </div>
        '''
        
        # requests.get 호출 순서에 따라 응답 분기
        mock_get.side_effect = [
            DummyResponse("", 200),     # robots.txt
            DummyResponse(search_html), # 검색 페이지
            DummyResponse(detail_html), # 상세 페이지 
        ]

        df = crawler(category="foo", count=1)
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)

        self.assertListEqual(
            list(df.columns),
            ["title","discount_rate","original_price","discounted_price",
            "review_pct","review_count","release_date","tags","link"]
        )
        row = df.iloc[0]
        self.assertEqual(row.title, "Dummy Game")
        self.assertEqual(row.discount_rate, 50)
        self.assertEqual(row.original_price, 20000)
        self.assertEqual(row.discounted_price, 10000)
        self.assertEqual(row.review_pct, 90)
        self.assertEqual(row.review_count, 100)
        self.assertIn("Action", row.tags)

    @patch('requests.get')
    def test_crawler_no_results(self, mock_get):
        # 빈 검색 결과를 돌려주는 DummyResponse
        class DummyResponse:
            def __init__(self):
                self.text = "<div></div>"
                self.status_code = 200
            def raise_for_status(self):
                pass

        mock_get.return_value = DummyResponse()
        with self.assertRaises(NoSearchResult):
            crawler(category="nothing", count=5)

    def test_clean_functions(self):
        # 헬퍼 함수 검증
        from utils.steam_crawler import clean_discount, clean_price, clean_date
        from datetime import date

        # clean_discount
        self.assertEqual(clean_discount("-20%"), 20)
        self.assertEqual(clean_discount("0%"), 0)

        # clean_price
        self.assertEqual(clean_price("₩1,234"), 1234)
        self.assertEqual(clean_price("N/A"), 0)

        # clean_date
        self.assertEqual(clean_date("2025-04-01"), date(2025,4,1))
        self.assertIsNone(clean_date("not a date"))    

# class DummyResponse:
#     def __init__(self, text, status_code=200):
#         self.text = text
#         self.status_code = status_code
#     def raise_for_status(self):
#         if self.status_code != 200:
#             raise Exception(f"HTTP {self.status_code}")
        
# @pytest.fixture(autouse=True)
# def mock_requests(monkeypatch):
#     # 검색 결과 더미 HTML
#     search_html = '''
#     <a class="search_result_row" href="http://fake">
#         <div class="title">Dummy Game</div>
#         <div class="discount_final_price">₩10,000</div>
#         <div class="discount_original_price">₩20,000</div>
#         <div class="discount_pct">-50%</div>
#         <div class="search_review_summary"
#             data-tooltip-html="90% of 100 user reviews"></div>
#     </a>
#     '''

#     # 상세 페이지 더미 HTML
#     detail_html = """
#     <div class="release_date"><span class="date">Apr 1, 2025</span></div>
#     <div class="glance_tags popular_tags">
#         <a class="app_tag">Action</a>
#         <a class="app_tag">Adventure</a>
#     </div>
#     """

#     import utils.steam_crawler as sc

#     def fake_get(url, headers=None):
#         # URL에 "search/?" 포함 시 --> search_html 반환
#         if "search/?" in url:
#             return DummyResponse(search_html)
#         else:
#             return DummyResponse(detail_html)
        
#     # steam_crawler 모듈 내부의 requests.get을 fake_get으로 교체
#     monkeypatch.setattr(sc.requsts, "get", fake_get)

# # test_crawler_success : 정상 케이스
# def test_crawler_success(self, mock_get):
#     df = crawler(category="anything", count=1)
#     assert isinstance(df, pd.DataFrame)
#     assert len(df) == 1
#     # 컬럼명 체크
#     assert list(df.columns) == [
#         "title","discount_rate","original_price","discounted_price",
#         "review_pct","review_count","release_date","tags","link"
#     ]
#     row = df.iloc[0]
#     assert row.title == "Dummy Game"
#     assert row.discount_rate == 50
#     assert row.original_price == 20000
#     assert row.discounted_price == 10000
#     assert row.review_pct == 90
#     assert row.review_count == 100
#     assert "Action" in row.tags

# # test_crawler_no_results : search_result_row 없을 때 NoResearchResult 예외 발생
# def test_crawler_no_results(monkeypatch):
#     import utils.steam_crawler as sc
#     # crawler 함수를 “무조건 NoSearchResult 예외” 버전으로 교체
#     monkeypatch.setattr(
#         sc, "crawler",
#         lambda category, count: (_ for _ in ()).throw(NoSearchResult())
#     )
#     with pytest.raises(NoSearchResult):
#         crawler(category="___none___", count=1)
