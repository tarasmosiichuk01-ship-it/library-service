from django.urls import path

from user.views import RegisterUserView

app_name = "user"

urlpatterns = [
    path("users/", RegisterUserView.as_view(), name="register"),
]