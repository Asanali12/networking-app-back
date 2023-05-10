import base64

from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse, OpenApiParameter
from rest_framework import viewsets, fields
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from socialApp.settings import s3_client, BUCKET_NAME
from user.models import User
from user_profile.helpers import upload_image_to_aws_storage


def user_to_user_data(user: User, self: User = None):
    data = {
        'id': user.id,
        'fullname': user.fullname,
        'email': user.email,
        'age': user.age,
        'city': user.city,
        'university': user.university,
        'logo_url': user.logo_url
    }
    if self is not None:
        data['is_friend'] = 1 if self.friends.filter(id=user.id).exists() else 0
    return {k: v for k, v in data.items() if v is not None}


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=inline_serializer("EditProfileRequest",
                                  {"fullname": fields.CharField(),
                                   "age": fields.IntegerField(),
                                   "city": fields.CharField(),
                                   "university": fields.CharField(),
                                   "logo": fields.ImageField()}),
        responses={
            200: inline_serializer("ProfileInfo",
                                   {"id": fields.IntegerField(),
                                    "email": fields.CharField(),
                                    "fullname": fields.CharField(),
                                    "age": fields.IntegerField(),
                                    "city": fields.CharField(),
                                    "university": fields.CharField(),
                                    "logo_url": fields.CharField(),
                                    "is_friend": fields.IntegerField()}),
        },
    )
    def edit(self, request):
        print(request.content_type)
        print(request.data)
        user = request.user
        logo = request.FILES.get('logo', None)
        print(request.FILES)
        fullname = request.data.get('fullname', None)
        age = request.data.get('age', None)
        city = request.data.get('city', None)
        university = request.data.get('university', None)
        if logo is not None:
            path = f'images/user_{user.id}/logo.PNG'
            user.logo_url = upload_image_to_aws_storage(BUCKET_NAME, logo.read(), path)
        if fullname is not None:
            user.fullname = fullname
        if age is not None:
            user.age = age
        if city is not None:
            user.city = city
        if university is not None:
            user.university = university
        user.save()
        return Response(user_to_user_data(user), status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("user_id", int)
        ],
        responses={
            200: inline_serializer("ProfileInfo",
                                   {"id": fields.IntegerField(),
                                    "email": fields.CharField(),
                                    "fullname": fields.CharField(),
                                    "age": fields.IntegerField(),
                                    "city": fields.CharField(),
                                    "university": fields.CharField(),
                                    "logo_url": fields.CharField(),
                                    "is_friend": fields.IntegerField()}),
        },
    )
    def info(self, request):
        user = request.user
        user_id = request.GET.get('user_id', None)
        user2 = user
        if user_id is not None:
            if not User.objects.filter(id=user_id).exists():
                raise ValidationError("user_id does not exist")
            user2 = User.objects.get(id=user_id)
        return Response(user_to_user_data(user2, user), status=200)