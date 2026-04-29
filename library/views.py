import stripe
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView


from library.models import Book, Borrowing, Payment
from library.serializers import BookSerializer, BorrowingSerializer, BorrowingDetailSerializer, BorrowingReturnSerializer
from library.tasks import notify_successful_payment

class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    serializer_class = BookSerializer


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


class PaymentSuccess(APIView):

    def get(self,request):
        session_id = request.GET.get("session_id")
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            payment_id = session.id
            payment = Payment.objects.get(session_id=payment_id)
            payment.status = Payment.StatusChoices.PAID
            payment.save()
            notify_successful_payment.delay(payment.id)

            return Response({"message": "Payment successful!"}, status=status.HTTP_200_OK)
        except stripe.error.InvalidRequestError:
            return Response({"error": "Invalid session ID."}, status=status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)


class PaymentCancel(APIView):

    def get(self, request):
        return Response(
            {"message": "Payment was cancelled."},
            status=status.HTTP_200_OK
        )

