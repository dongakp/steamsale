from django.shortcuts import redirect, render, get_object_or_404
from utils.steam_crawler import crawler, NoSearchResult
from .models import Game, Visualization, Stats
from django.http import HttpResponse, JsonResponse
from utils.steam_visualize import get_visualization_data, save_wordcloud
from django.conf import settings
import subprocess
import os

# ✅ 인덱스 뷰
def index_view(request):
    return render(request, "index.html")

# ✅ 크롤링 실행 뷰
def run_crawler_view(request):
    if request.method == 'POST':
        Game.objects.all().delete()
        category = request.POST.get('category')
        count = request.POST.get('count')

        if count is None or str(count).strip() == "":
            return render(request, 'dashboard.html', {
                'message': "⚠️ 게임 수를 입력해주세요.",
                'games': Game.objects.all()
            })
        try:
            count = int(count)
            if count <= 0:
                return render(request, 'dashboard.html', {
                    'message': "⚠️ 게임 수는 1 이상의 숫자여야 합니다.",
                    'games': Game.objects.all()
                })
        except ValueError:
            return render(request, 'dashboard.html', {
                'message': "⚠️ 게임 수는 숫자로 입력해주세요.",
                'games': Game.objects.all()
            })

        try:
            crawler(category, count)
            subprocess.call(["python", os.path.join(settings.BASE_DIR, "utils", "steam_visualize.py")])
            data = get_visualization_data()
            save_wordcloud(data["wordcloud_data"])
        except NoSearchResult:
            return render(request, 'index.html', {
                'message': f"'{category}'에 대한 검색 결과가 없습니다."
            })

        return redirect('dashboard')
    return HttpResponse("비정상적인 접근입니다.")

# ✅ 게임 리스트 뷰
def game_list(request):
    sort = request.GET.get('sort')
    games = Game.objects.all()
    if sort == 'price':
        games = games.order_by('discounted_price')
    elif sort == 'discount':
        games = games.order_by('-discount_rate')
    elif sort == 'review':
        games = games.order_by('-review_count')
    return render(request, 'deals/game_list.html', {'games': games})

# ✅ 게임 상세 뷰
def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    reviews = game.reviews.all()
    return render(request, 'deals/game_detail.html', {'game': game, 'reviews': reviews})

# ✅ 게임 통계용 시각화 placeholder (백엔드 확장 가능)
def game_statistics(request):
    vis = Visualization.objects.all()
    return HttpResponse("여기는 시각화 페이지 입니다")

# ✅ 대시보드 메인 뷰
def dashboard_view(request):
    games = Game.objects.all()
    return render(request, "dashboard.html", {"games": games})

# ✅ 시각화 데이터를 JSON으로 반환 (Chart.js용)
def visualization_json_view(request):
    data = get_visualization_data()
    return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})

# ✅ 차트 뷰
def charts_view(request):
    games = Game.objects.all().order_by('-discount_rate')[:50]
    return render(request, "charts.html", {"games": games})
