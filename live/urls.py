from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    #path("<int:m5u8id>/", views.live, name="live"),
]