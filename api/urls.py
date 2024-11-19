from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the homepage")

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin URL
    # path('', home),  # Root URL
    # path('',include('boostedchatScrapper.urls')),
    path('instagram/',include('api.instagram.urls')),
    path('prompt/',include('api.prompt.urls')),
    path('',include('api.analyst.urls')),
]
