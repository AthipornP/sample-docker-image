from django.urls import path
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Django Sample App</h1><p>Hello from Django.</p><p><a href='http://localhost:3000' target='_top' style='display:inline-block;padding:10px 16px;background:#1976d2;color:#fff;border-radius:6px;text-decoration:none;font-weight:600;'>Back to Portal</a></p>")

urlpatterns = [
    path('', index),
]
