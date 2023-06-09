from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer, OpenApiParameter
from rest_framework import fields
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.models import User
from user.serializers import RegistrationSerializer, MyTokenObtainPairSerializer, UserSerializer
from user_profile.views import user_to_user_data


class RegistrationAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    @extend_schema(
        request=RegistrationSerializer,
        responses={201: TokenObtainPairSerializer},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=400)

        user = serializer.save()
        tokens = MyTokenObtainPairSerializer(request.data).validate(request.data)
        return Response(tokens, status=201)


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = MyTokenObtainPairSerializer

    @extend_schema(
        request=MyTokenObtainPairSerializer,
        responses={201: TokenObtainPairSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, args, kwargs)


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            (200, 'text/plain'): OpenApiResponse(description="Successfully logout")
        },
    )
    def post(self, request):
        user = request.user
        for token in OutstandingToken.objects.filter(user=user).exclude(
                id__in=BlacklistedToken.objects.filter(token__user=user).values_list('token_id', flat=True)):
            BlacklistedToken.objects.create(token=token)
        return Response("Successfully logout", status=200)


@extend_schema(
    parameters=[
        OpenApiParameter("query", str)
    ],
    responses={
    200: inline_serializer("FriendsList",
                           {"id": fields.IntegerField(),
                            "email": fields.CharField(),
                            "fullname": fields.CharField(),
                            "age": fields.IntegerField(),
                            "city": fields.CharField(),
                            "university": fields.CharField(),
                            "logo_url": fields.CharField(),
                            "is_friend": fields.IntegerField()}, many=True),
    },
)
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def search(request):
    user = request.user
    query = request.GET.get('query', None)

    if query is None:
        raise ValidationError("query field does not exist")

    users = User.objects.filter(fullname__startswith=query).exclude(id=user.id)

    data = []
    for user2 in users:
        data.append(user_to_user_data(user2, user))

    return Response(data, status=200)