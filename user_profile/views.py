from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
        return Response(status=200)
