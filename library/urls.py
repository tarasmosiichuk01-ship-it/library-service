from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet, BorrowingViewSet

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet)
router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

