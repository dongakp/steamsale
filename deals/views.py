from django.shortcuts import redirect, render
from .crawler import run_crawler
from django.http import HttpResponse

def index_view(request):
    return render(request, "index.html")

def run_crawler_view(request):
    if request.method == 'POST':
        category = request.POST.get('category')
        count = int(request.POST.get('count'))
        run_crawler(category, count)
        return redirect('/api/game/')
    return HttpResponse("비정상적인 접근입니다.")
