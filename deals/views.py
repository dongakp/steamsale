from django.shortcuts import redirect, render, get_object_or_404
from .crawler import run_crawler, NoSearchResult
from .models import Game
from django.http import HttpResponse

def index_view(request):
    return render(request, "index.html")

def run_crawler_view(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        count = int(request.POST.get('count'))

        try:
            run_crawler(category, count)
        except NoSearchResult:
            return render(request, 'index.html', {'message' : f"'{category}'에 대한 검색 결과가 없습니다."})

        return redirect('game-list')
    return HttpResponse("비정상적인 접근입니다.")

def game_list(request):
    games = Game.objects.all()
    return render(request, 'deals/game_list.html', {'games': games})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    reviews = game.reviews.all()
    return render(request, 'deals/game_detail.html', {'game': game, 'reviews':reviews})

    
