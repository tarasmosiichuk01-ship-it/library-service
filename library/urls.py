from django.urls import path, include
from rest_framework import routers

from library.views import BookViewSet, BorrowingView, BorrowingDetailView, BorrowingReturnView

app_name = "library"

router = routers.DefaultRouter()
router.register("books", BookViewSet)
#router.register("borrowings", BorrowingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("borrowings/", BorrowingView.as_view(), name="borrowings"),
    path("borrowings/<int:pk>/", BorrowingDetailView.as_view(), name="borrowings-detail"),
    path("borrowings/<int:pk>/return/", BorrowingReturnView.as_view(), name="borrowing-return"),
]

