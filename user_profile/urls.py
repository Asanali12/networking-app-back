from django.urls import path

from user_profile.views import ProfileViewSet

urlpatterns = [
    path('edit/', ProfileViewSet.as_view({"post": "edit"}), name='edit_profile'),
    path('info/', ProfileViewSet.as_view({"get": "info"}), name='profile_info'),
]