from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('deals_api.urls')),
    path('deals/', include('deals_api.urls')),
    path('', include('deals_api.urls')),
]
