from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="profiles-home"),
    path("new", views.new_profile, name="profiles-new"),
    path("users", views.manage_users, name="profiles-users"),
    path("<uuid:profile_uuid>", views.profile, name="profiles-profile"),
    path("<uuid:profile_uuid>/edit", views.edit_profile, name="profiles-profile-edit"),
    path("<uuid:profile_uuid>/manage", views.manage_profile, name="profiles-profile-manage"),
]
