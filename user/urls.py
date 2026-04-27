from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import RegisterUserView, UserProfileView

app_name = "user"

urlpatterns = [
    path("users/", RegisterUserView.as_view(), name="register"),
    path("users/token/", TokenObtainPairView.as_view(), name="get-token"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="refresh-token"),
    path("users/me/", UserProfileView.as_view(), name="user-profile"),
]