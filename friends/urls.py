from django.urls import path

from friends.views import FriendsViewSet
from user_profile.views import ProfileViewSet

urlpatterns = [
    path('list/', FriendsViewSet.as_view({"get": "list"}), name='get_friend_list'),
]