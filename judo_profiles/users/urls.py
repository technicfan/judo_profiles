from django.urls import path

from . import views

urlpatterns = [
    path("login", views.login_user),
    path("logout", views.logout_user),
    path("update", views.change_pass),
    path("register", views.register)
]
