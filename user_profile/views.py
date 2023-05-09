import base64

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.models import User


def user_to_user_data(user: User):
    data = {
        'id': user.id,
        'fullname': user.fullname,
        'email': user.email,
        'age': user.age,
        'city': user.city,
        'university': user.university,
    }
    if user.logo is not None:
        data['logo'] = base64.b64encode(user.logo.read())

    return data


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
            print("LOGO UPDATED")
            user.logo = logo
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
