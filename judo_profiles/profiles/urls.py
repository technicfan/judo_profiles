from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="profiles-home"),
    path("new", views.new_profile, name="profiles-new"),
    path("<int:profile_id>", views.profile, name="profiles-profile"),
    path("<int:profile_id>/edit", views.edit_profile, name="profiles-profile-edit"),
    path("<int:profile_id>/manage", views.manage_profile, name="profiles-profile-manage"),
]
