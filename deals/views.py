from django.shortcuts import redirect, render
from .crawler import run_crawler

def index_view(request):
    return render(request, "index.html")

def run_crawler_view(request):
    run_crawler()
    return redirect('/api/game/')
