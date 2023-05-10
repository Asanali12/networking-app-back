from django.urls import path

from posts.views import PostViewSet

urlpatterns = [
    path('create/', PostViewSet.as_view({"post": "create"}), name='create_post'),
    path('like/', PostViewSet.as_view({"post": "like"}), name='like_post'),
    path('unlike/', PostViewSet.as_view({"post": "unlike"}), name='unlike_post'),
    path('userPosts/', PostViewSet.as_view({"get": "user_posts"}), name='get_user_posts'),
    path('feed/', PostViewSet.as_view({"get": "feed"}), name='get_user_feed'),
]
