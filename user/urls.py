from django.urls import path

from user.views import MyObtainTokenPairView, LogoutAPIView, MyTokenRefreshView, RegistrationAPIView

urlpatterns = [
    path('login/', MyObtainTokenPairView.as_view(), name='user_login'),
    path('logout/', LogoutAPIView.as_view(), name='user_logout'),
    path('login/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegistrationAPIView.as_view(), name='user_register'),
]