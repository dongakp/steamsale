from django.shortcuts import redirect, render, get_object_or_404
from utils.steam_crawler import crawler,NoSearchResult
from .models import Game, Visualization
from django.http import HttpResponse
from django.http import JsonResponse
from utils.steam_visualize import get_visualization_data, save_wordcloud
from django.conf import settings
import subprocess
import os
from django.utils import timezone



def index_view(request):
    return render(request, "index.html")

def run_crawler_view(request):
    if request.method == 'POST':
        Game.objects.all().delete()
        category = request.POST.get('category')
        count = request.POST.get('count')

        if count is None or str(count).strip() == "":
            return render(request, 'dashboard.html', {
                'message': "⚠️ 게임 수를 입력해주세요.",
                'games': Game.objects.all()  # 필드에 따라 추가
            })
        # count 입력 없을 시 기본값 10
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
                'games': Game.objects.all(),  # 필요 시 추가
            })

        try:
            crawler(category, count)
            subprocess.call(["python", os.path.join(settings.BASE_DIR, "utils", "steam_visualize.py")])

            # ✅ 크롤링 성공 시 워드클라우드 자동 생성
            data = get_visualization_data()
            save_wordcloud(data["wordcloud_data"])

        except NoSearchResult:
            return render(request, 'dashboard.html', {
                'message': f"'{category}'에 대한 검색 결과가 없습니다."
            })

        return redirect('game-list') 
    return HttpResponse("비정상적인 접근입니다.")

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

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    reviews = game.reviews.all()
    return render(request, 'deals/game_detail.html', {'game': game, 'rev    iews':reviews})

def game_statistics(request):
    vis = Visualization.objects.all()
    return HttpResponse("여기는 시각화 페이지 입니다") # ... 적절한 template을 만들어 연결해야 함

#def dashboard_view(request):
#   return render(request, "dashboard.html")  # 기존: index 복사본.html


def visualization_json_view(request): # 시각화
    data = get_visualization_data()
    return JsonResponse(data, safe=False, json_dumps_params={"ensure_ascii": False, "indent": 2})

def charts_view(request):
    games = Game.objects.all().order_by('-discount_rate')[:50]
    return render(request, "charts.html", {"games": games})

def dashboard_view(request):
    games = Game.objects.all()
    return render(request, "dashboard.html", {"games": games,  "timestamp": timezone.now().timestamp()})
