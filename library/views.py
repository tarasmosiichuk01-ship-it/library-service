import stripe
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


from library.models import Book, Borrowing, Payment
from library.serializers import (
    BookSerializer,
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)
from library.tasks import notify_successful_payment


class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type=str,
                description="Filter by book title",
                required=False,
            ),
            OpenApiParameter(
                "author",
                type=str,
                description="Filter by book author",
                required=False,
            ),
            OpenApiParameter(
                "cover",
                type=str,
                description="Filter by book cover",
                required=False,
                enum=[choice[0] for choice in Book.CoverChoices.choices]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of books"""
        return super().list(request, *args, **kwargs)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Borrowing.objects.filter(user=user).select_related("book")

        user_id = self.request.query_params.get("user_id", None)
        is_active = self.request.query_params.get("is_active", None)

        if user_id:
            queryset = queryset.filter(user_id=user_id)

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset.order_by("-borrow_date")

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.user != request.user:
            return Response({"detail": "Forbidden"}, status=403)

        serializer = BorrowingReturnSerializer(
            borrowing,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "borrow_date",
                type=OpenApiTypes.DATE,
                description="Filter by borrowed date in format YYYY-MM-DD",
                required=False,
            ),
            OpenApiParameter(
                "expected_date",
                type=OpenApiTypes.DATE,
                description="Filter by expected date in format YYYY-MM-DD",
                required=False,
            ),
            OpenApiParameter(
                "actual_return_date",
                type=OpenApiTypes.DATE,
                description="Filter by actual "
                            "return date in format YYYY-MM-DD",
                required=False,
            ),
            OpenApiParameter(
                "book",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by book id ex. ?book=2,3",
                required=False,
                explode=False,
            ),
            OpenApiParameter(
                "user",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by user id ex. ?user=2,3",
                required=False,
                explode=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of borrowings"""
        return super().list(request, *args, **kwargs)


class PaymentSuccess(APIView):

    def get(self, request):
        session_id = request.GET.get("session_id")
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment_id = session.id
            payment = Payment.objects.get(session_id=payment_id)
            payment.status = Payment.StatusChoices.PAID
            payment.save()
            notify_successful_payment.delay(payment.id)

            return Response(
                {"message": "Payment successful!"},
                status=status.HTTP_200_OK
            )
        except stripe.error.InvalidRequestError:
            return Response(
                {"error": "Invalid session ID."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentCancel(APIView):

    def get(self, request):
        return Response(
            {"message": "Payment was cancelled."},
            status=status.HTTP_200_OK
        )
