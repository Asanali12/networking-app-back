from django.http import JsonResponse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.serializers import RegistrationSerializer, MyTokenObtainPairSerializer, UserSerializer


class RegistrationAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

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

    def post(self, request, *args, **kwargs):
        return super().post(request, args, kwargs)


class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        for token in OutstandingToken.objects.filter(user=user).exclude(
                id__in=BlacklistedToken.objects.filter(token__user=user).values_list('token_id', flat=True)):
            BlacklistedToken.objects.create(token=token)
        return Response("Successfully logout", status=200)