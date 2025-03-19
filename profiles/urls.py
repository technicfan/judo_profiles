from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="profiles-home"),
    path("about", views.about, name="profiles-about"),
    path("profiles/", views.start, name="profiles-profiles"),
    path("profiles/new", views.new_profile, name="profiles-new"),
    path("profiles/<str:username>", views.profile, name="profiles-profile"),
    path("profiles/<str:username>/edit", views.edit_profile, name="profiles-profile-edit"),
    path("profiles/<str:username>/manage", views.manage_profile, name="profiles-profile-manage"),
]
