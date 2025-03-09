from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("search_profiles", views.search_profiles),
    path("new", views.new_profile),
    path("<uuid:profile_uuid>", views.profile),
    path("<uuid:profile_uuid>/edit", views.edit_profile),
    path("<uuid:profile_uuid>/manage", views.manage_profile),
]
