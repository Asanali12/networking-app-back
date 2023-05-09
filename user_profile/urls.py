from django.urls import path

from user_profile.views import ProfileViewSet

urlpatterns = [
    path('edit/', ProfileViewSet.as_view({"post": "edit"}), name='edit_profile')
]