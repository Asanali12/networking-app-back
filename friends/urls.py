from django.urls import path

from friends.views import FriendsViewSet
from user_profile.views import ProfileViewSet

urlpatterns = [
    path('list/', FriendsViewSet.as_view({"get": "list"}), name='get_friend_list'),
    path('sendRequest/', FriendsViewSet.as_view({"post": "send_request"}), name='send_friend_request'),
    path('delete/', FriendsViewSet.as_view({"post": "delete"}), name='delete_from_friend'),
    path('incomeRequest/', FriendsViewSet.as_view({"get": "income_request"}), name='user_income_request'),
    path('approveRequest/', FriendsViewSet.as_view({"post": "approve_request"}), name='approve_user_request'),
    path('declineRequest/', FriendsViewSet.as_view({"post": "decline_request"}), name='decline_user_request'),
]