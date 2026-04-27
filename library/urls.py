from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

