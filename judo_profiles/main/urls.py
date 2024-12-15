from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("<int:profile_id>", views.edit_profile)
]
