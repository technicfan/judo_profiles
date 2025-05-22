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
    path("", profiles.index, name="index"),
    path("about", profiles.about, name="about"),
    # profiles
    path("profiles", profiles.start, name="profiles"),
    path("profiles/new", profiles.new_profile, name="new-profile"),
    path("profiles/<str:username>", profiles.profile, name="profile"),
    path(
        "profiles/<str:username>/edit",
        profiles.edit_profile,
        name="edit-profile",
    ),
    path(
        "profiles/<str:username>/manage",
        profiles.manage_profile,
        name="manage-profile",
    ),
    # users
    path("users", users.users, name="users"),
    path("users/new-trainer", users.new_trainer, name="new-trainer"),
    path("users/new-staff", users.new_staff, name="new-staff"),
    path("users/<str:username>", users.manage_user, name="manage-user"),
    # auth/account
    path("login", users.login_user, name="login"),
    path("logout", users.logout_user, name="logout"),
    path("register", users.register, name="register"),
    path("account/manage", users.change_pass, name="account"),
    # admin stuff
    path("server/techniques", profiles.techniques, name="techniques"),
    # translation
    path("i18n/", include("django.conf.urls.i18n")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
]
