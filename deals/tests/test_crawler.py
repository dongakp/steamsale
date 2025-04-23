import pandas as pd
import pytest
from utils.steam_crawler import crawler, NoSearchResult


class DummyResponse:
    def __init__(self, text, status_code=200):
        self.text = text
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP {self.status_code}")
        
@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):
    # 검색 결과 더미 HTML
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

    # 상세 페이지 더미 HTML
    detail_html = """
    <div class="release_date"><span class="date">Apr 1, 2025</span></div>
    <div class="glance_tags popular_tags">
        <a class="app_tag">Action</a>
        <a class="app_tag">Adventure</a>
    </div>
    """

    import utils.steam_crawler as sc

    def fake_get(url, headers=None):
        # URL에 "search/?" 포함 시 --> search_html 반환
        if "search/?" in url:
            return DummyResponse(search_html)
        else:
            return DummyResponse(detail_html)
        
    # steam_crawler 모듈 내부의 requests.get을 fake_get으로 교체
    monkeypatch.setattr(sc.requsts, "get", fake_get)

# test_crawler_success : 정상 케이스
def test_crawler_success():
    df = crawler(category="anything", count=1)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    # 컬럼명 체크
    assert list(df.columns) == [
        "title","discount_rate","original_price","discounted_price",
        "review_pct","review_count","release_date","tags","link"
    ]
    row = df.iloc[0]
    assert row.title == "Dummy Game"
    assert row.discount_rate == 50
    assert row.original_price == 20000
    assert row.discounted_price == 10000
    assert row.review_pct == 90
    assert row.review_count == 100
    assert "Action" in row.tags

# test_crawler_no_results : search_result_row 없을 때 NoResearchResult 예외 발생
def test_crawler_no_results(monkeypatch):
    import utils.steam_crawler as sc
    # crawler 함수를 “무조건 NoSearchResult 예외” 버전으로 교체
    monkeypatch.setattr(
        sc, "crawler",
        lambda category, count: (_ for _ in ()).throw(NoSearchResult())
    )
    with pytest.raises(NoSearchResult):
        crawler(category="___none___", count=1)
