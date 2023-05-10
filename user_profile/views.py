import base64

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from socialApp.settings import s3_client, BUCKET_NAME
from user.models import User
from user_profile.helpers import upload_image_to_aws_storage


def user_to_user_data(user: User):
    data = {
        'id': user.id,
        'fullname': user.fullname,
        'email': user.email,
        'age': user.age,
        'city': user.city,
        'university': user.university,
        'logo_url': user.logo_url
    }
    return {k: v for k, v in data.items() if v}


class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def edit(self, request):
        user = request.user
        logo = request.FILES.get('logo', None)
        fullname = request.data.get('fullname', None)
        age = request.data.get('age', None)
        city = request.data.get('city', None)
        university = request.data.get('university', None)
        if logo is not None:
            extension = logo.name.split('.')[-1]
            path = f'images/user_{user.id}/logo.{extension}'
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

    def info(self, request):
        user = request.user
        return Response(user_to_user_data(user), status=200)
