from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer
from rest_framework import viewsets, fields
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

    @extend_schema(
        request=inline_serializer("PostCreateRequest", {
            'body': fields.CharField(),
            'image': fields.ImageField()
        }),
        responses={
            200: inline_serializer("PostInfo", {
                'id': fields.IntegerField(),
                'body': fields.CharField(),
                'image_url': fields.CharField(),
                'likes': fields.IntegerField(),
                'is_liked': fields.BooleanField()
            }, many=True),
        },
    )
    def create(self, request):
        user = request.user
        body = request.data.get('body', None)
        image = request.FILES.get('image', None)
        if body is None and image is None:
            raise ValidationError("Post is empty")

        post = Posts.objects.create(body=body, author=user)
        if image is not None:
            path = f'images/user_{user.id}/post_{post.id}.PNG'
            post.image_url = upload_image_to_aws_storage(BUCKET_NAME, image.read(), path)
            post.save()

        return Response(post_to_post_data(post, user), status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("post_id", int)
        ],
        responses={
            200: OpenApiResponse(description="Post is liked"),
        },
    )
    def like(self, request):
        user = request.user
        post_id = request.GET.get('post_id', None)
        if post_id is None:
            raise ValidationError("post_id field does not exist")
        if not Posts.objects.filter(id=post_id).exists():
            raise ValidationError("post_id does not exist")

        post = Posts.objects.get(id=post_id)

        if post.likes.filter(id=user.id).exists():
            raise ValidationError("Post already liked")

        post.likes.add(user)
        return Response("Post is liked", status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("post_id", int)
        ],
        responses={
            200: OpenApiResponse(description="Post is unliked"),
        },
    )
    def unlike(self, request):
        user = request.user
        post_id = request.GET.get('post_id', None)
        if post_id is None:
            raise ValidationError("post_id field does not exist")
        if not Posts.objects.filter(id=post_id).exists():
            raise ValidationError("post_id does not exist")

        post = Posts.objects.get(id=post_id)

        if not post.likes.filter(id=user.id).exists():
            raise ValidationError("User cannot unlike post")

        post.likes.remove(user)
        return Response("Post is unliked", status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("user_id", int)
        ],
        responses={
            200: inline_serializer("PostInfo", {
                'id': fields.IntegerField(),
                'body': fields.CharField(),
                'image_url': fields.CharField(),
                'likes': fields.IntegerField(),
                'is_liked': fields.BooleanField()
            }, many=True),
        },
    )
    def user_posts(self, request):
        user = request.user
        user_id = request.GET.get('user_id', None)
        user2 = user
        if user_id is not None:
            if not User.objects.filter(id=user_id).exists():
                raise ValidationError("user_id does not exist")
            user2 = User.objects.get(id=user_id)

        data = []
        posts = Posts.objects.filter(author=user2)
        for post in posts:
            data.append(post_to_post_data(post, user))

        return Response(data, status=200)

    @extend_schema(
        responses={
            200: inline_serializer("PostInfo", {
                'id': fields.IntegerField(),
                'body': fields.CharField(),
                'image_url': fields.CharField(),
                'likes': fields.IntegerField(),
                'is_liked': fields.BooleanField()
            }, many=True),
        },
    )
    def feed(self, request):
        user = request.user
        data = []
        friends = user.friends.all()
        for friend in friends:
            posts = Posts.objects.filter(id=friend.id)
            for post in posts:
                data.append(post_to_post_data(post, user))

        return Response(data, status=200)
