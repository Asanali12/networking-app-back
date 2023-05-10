from django.urls import path

from posts.views import PostViewSet

urlpatterns = [
    path('create/', PostViewSet.as_view({"post": "create"}), name='create_post'),
]