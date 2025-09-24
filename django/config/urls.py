from django.urls import path
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Django Sample App</h1><p>Running in container</p>")

urlpatterns = [
    path('', index),
]
