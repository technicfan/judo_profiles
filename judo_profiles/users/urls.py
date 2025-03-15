from django.urls import path

from . import views

urlpatterns = [
    path("", views.manage_users, name="users-manage"),
    path("new", views.new_user, name="users-new"),
    path("login", views.login_user, name="users-login"),
    path("logout", views.logout_user, name="users-logout"),
    path("update", views.change_pass, name="users-update"),
    path("register", views.register, name="users-register")
]
