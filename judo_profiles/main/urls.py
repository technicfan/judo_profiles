from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("profile/new", views.new_profile),
    path("profile/<uuid:profile_uuid>", views.profile),
    path("profile/<uuid:profile_uuid>/edit", views.edit_profile),
    path("profile/<uuid:profile_uuid>/manage", views.manage)
]
