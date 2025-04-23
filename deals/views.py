import json
import pprint
import subprocess
import os

from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from utils.steam_crawler import crawler,NoSearchResult
from .models import Game, Stats
from django.http import HttpResponse


def index_view(request):
    return render(request, "index.html")

def run_crawler_view(request):
    if request.method == 'POST':
        Game.objects.all().delete()
        category = request.POST.get('category')
        count = (request.POST.get('count'))
        
        if count is None or str(count).strip() == "":
            return render(request, 'index.html', {
                'message': "⚠️ 게임 수를 입력해주세요."
            })
        try:
            count = int(count)
        except ValueError:
            return render(request, 'index.html', {
                'message': "⚠️ 게임 수는 숫자로 입력해주세요."
            })

            
        try:
            crawler(category, count)
            subprocess.call(["python", os.path.join(settings.BASE_DIR, "utils", "steam_visualize.py")])
        except NoSearchResult:
            return render(request, 'index.html', {'message' : f"'{category}'에 대한 검색 결과가 없습니다."})
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
    return render(request, 'deals/game_detail.html', {'game': game, 'reviews':reviews})

def index_alt_view(request):  # 양민식
    def get_data(data_type):
        obj = Stats.objects.filter(data__type=data_type).first()
        return obj.data if obj else {}

    context = {
        "discount_data": json.dumps(get_data("discount_kde")),
        "tag_data": json.dumps(get_data("tag")),
        "value_data": json.dumps(get_data("value")),
        "price_data": json.dumps(get_data("price")),
        "bubble_data": json.dumps(get_data("bubble")),
    }

    return render(request, 'index 복사본.html', context)