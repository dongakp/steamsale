from django.test import TestCase, Client
from django.urls import reverse
from utils.steam_crawler import NoSearchResult
from unittest.mock import patch

class ViewTest(TestCase):
    def setUp(self):
        # 테스트용 클라이언트 초기화
        # --> self.client로 URL 요청(GET/POST)을 할 수 있음
        self.client = Client()

    # 1. index GET 요청
    def test_index_get(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'index.html')

    # 2. run-crawler GET (비정상 접근)
    # 크롤러 실행 뷰는 POST만 허용
    # GET '/run-crawler/' --> "비정상적인 접근" 메시지 포함
    def test_run_crawler_get_forbidden(self):
        resp = self.client.get(reverse('run-crawler'))
        self.assertContains(resp, "비정상적인 접근")

    # 3. run-crawler POST 성공 (리다이렉트 확인)
    # POST로 크롤러 실행 시 302 리다이렉트 확인
    @patch('deals.views.crawler')
    def test_run_crawler_post_success(self, monkeypatch):
        # crawler 함수를 항상 성공 케이스로 교체
        monkeypatch.setattr(
            'deals.steam_crawler',
            lambda category, count : None
        )
        # POST 요청
        resp = self.client.post(
            reverse('run-crawler'),
            {'category':'x', 'count':'1'}
        )
        # 302 리다이렉트 확인
        self.assertEqual(resp.status_code, 302)
        # 리다이렉트 위치가 dashboard인지 확인
        self.assertEqual(resp.url, reverse('dashboard'))

    # 4. run-crawler POST 실패 - NoSearchResult 발생 시 index.html 렌더링
    # 검색 결과 없을 때, NoSearchResult 예외 처리 확인
    @patch('deals.views.crawler', side_effect=NoSearchResult)
    def test_run_crawler_post_no_results(self, monkeypatch):
        # crawler 함수를 예외 발생 케이스로 교체
        def fake_crawler(category, count): 
            raise NoSearchResult()
        
        monkeypatch.setattr(
            'deals.steam_crawler',
            fake_crawler
        )
        resp = self.client.post(
            reverse('run-crawler'),
            {'category': 'x', 'count': "1"}
        )
        # POST -> 예외 발생시에도 status 200 
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'index.html')
        self.assertContains(resp, '검색 결과가 없습니다')

    # 5. run-crawler POST 실패 - count에 문자가 들어올 경우
    def test_run_crawler_post_invalid_count(self):
        resp = self.client.post(
            reverse('run-crawler'),
            {'category': 'x', 'count': 'abc'}  # 숫자가 아님
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dashboard.html')
        self.assertContains(resp, "⚠️ 게임 수는 숫자로 입력해주세요.")


    # 6. run-crawler POST 실패 - count가 음수일 경우
    def test_run_crawler_post_negative_count(self):
        resp = self.client.post(
            reverse('run-crawler'),
            {'category': 'x', 'count': '-5'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dashboard.html')
        self.assertContains(resp, "게임 수는 1 이상의 숫자여야 합니다")

    # 7. 빈 문자열인 경우
    def test_run_crawler_post_count_missing(self):
        resp = self.client.post(reverse('run-crawler'), {"category": "x", "count": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'dashboard.html')
        self.assertContains(resp, "⚠️ 게임 수를 입력해주세요.")