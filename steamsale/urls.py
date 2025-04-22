from django.contrib import admin
from django.urls import path, include
from deals.views import index_view  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('deals.urls')),
    path('api/', include('deals_api.urls')),
]
