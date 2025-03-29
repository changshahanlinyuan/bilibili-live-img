from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, "live/index.html", {})


def live(request, live_id):
    return HttpResponse("Hello, world.")

