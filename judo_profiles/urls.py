"""
URL configuration for judo_profiles project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

from .views import profiles, users

urlpatterns = [
    path("", profiles.home, name="profiles-home"),
    path("about", profiles.about, name="profiles-about"),
    # profile related
    path("profiles", profiles.start, name="profiles-profiles"),
    path("profiles/new", profiles.new_profile, name="profiles-new"),
    path("profile/<str:username>", profiles.profile, name="profiles-profile"),
    path(
        "profile/<str:username>/edit",
        profiles.edit_profile,
        name="profiles-profile-edit",
    ),
    path(
        "profile/<str:username>/manage",
        profiles.manage_profile,
        name="profiles-profile-manage",
    ),
    # user related
    path("users", users.users, name="users-manage"),
    path("users/new-trainer", users.new_trainer, name="users-new-trainer"),
    path("users/new-staff", users.new_staff, name="users-new-staff"),
    path("login", users.login_user, name="users-login"),
    path("logout", users.logout_user, name="users-logout"),
    path("users/manage", users.change_pass, name="users-update"),
    path("register", users.register, name="users-register"),
    path("user/<str:username>", users.manage_user, name="users-user"),
    # translation
    path("i18n/", include("django.conf.urls.i18n")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]
