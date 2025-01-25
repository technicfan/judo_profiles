from django.urls import path

from . import views

urlpatterns = [
    path("login", views.auth),
    path("change_pass", views.change_pass)
]

