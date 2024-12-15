from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("<int:profile_id>", views.profile),
    path("<int:profile_id>/edit", views.edit_profile)
]
