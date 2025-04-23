from django.test import TestCase, Client
from django.urls import reverse
from utils.steam_crawler import NoSearchResult
from unittest.mock import patch

class ViewTest(TestCase):
    def setUp(self):
        # 1. 테스트용 클라이언트 초기화
        # --> self.client로 URL 요청(GET/POST)을 할 수 있음
        self.client = Client()

    # 2. test_index_get
    def test_index_get(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'index.html')

    # 3. test_run_crawler_get_forbidden
    # 크롤러 실행 뷰는 POST만 허용
    # GET '/run-crawler/' --> "비정상적인 접근" 메시지 포함
    def test_run_crawler_get_forbidden(self):
        resp = self.client.get(reverse('run-crawler'))
        self.assertContains(resp, "비정상적인 접근")

    # 4. test_run_crawler_post_success
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
        # 리다이렉트 위치가 game-list인지 확인
        self.assertEqual(resp.url, reverse('game-list'))

    # 5. test_run_crawler_post_no_results
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