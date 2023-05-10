from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from posts.models import Posts
from socialApp.settings import BUCKET_NAME
from user.models import User
from user_profile.helpers import upload_image_to_aws_storage


def post_to_post_data(post: Posts, user: User = None):
    data = {
        'id': post.id,
        'body': post.body,
        'image_url': post.image_url,
        'likes': len(post.likes.all()),
        'is_liked': 0
    }
    if user is not None and post.likes.filter(id=user.id).exists():
        data['is_liked'] = 1
    return data


class PostViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        user = request.user
        body = request.data.get('body', None)
        image = request.FILES.get('image', None)
        if body is None and image is None:
            raise ValidationError("Post is empty")

        post = Posts.objects.create(body=body, author=user)
        path = f'images/user_{user.id}/post_{post.id}.PNG'
        post.image_url = upload_image_to_aws_storage(BUCKET_NAME, image.read(), path)
        post.save()

        return Response(post_to_post_data(post, user), status=200)
