from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet, BorrowingViewSet, PaymentSuccess, PaymentCancel

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet)
router.register("borrowings", BorrowingViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
    path("payments/success/", PaymentSuccess.as_view(), name="success"),
    path("payments/cancel/", PaymentCancel.as_view(), name="cancel"),
]

