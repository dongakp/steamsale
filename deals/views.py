from django.shortcuts import redirect, render, get_object_or_404
from .crawler import run_crawler
from .models import Game

def index_view(request):
    return render(request, "index.html")

def run_crawler_view(request):
    run_crawler()
    return redirect('game-list')

def game_list(request):
    games = Game.objects.all()
    return render(request, 'deals/game_list.html', {'games': games})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    reviews = game.reviews.all()
    return render(request, 'deals/game_detail.html', {'game': game, 'reviews':reviews})
