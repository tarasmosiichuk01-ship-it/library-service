import stripe
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from library.models import Book, Borrowing, Payment

SUCCESS_URL = reverse("library:success")
CANCEL_URL = reverse("library:cancel")

class TestPaymentApi(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testemail.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Hard",
            inventory=10,
            daily_fee=9.00,
        )
        self.borrowing = Borrowing.objects.create(
            expected_date="2026-05-15",
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://stripe.com/test",
            session_id="test_session_id",
            money_to_pay=10.00,
        )

    @patch("library.views.notify_successful_payment.delay")
    @patch("library.views.stripe.checkout.Session.retrieve")
    def test_payment_success_with_valid_session_id(self, mock_stripe, mock_notify):
        mock_stripe.return_value.id = "test_session_id"
        res = self.client.get(SUCCESS_URL, {"session_id": self.payment.session_id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, Payment.StatusChoices.PAID)

    @patch("library.views.stripe.checkout.Session.retrieve")
    def test_payment_success_with_invalid_session_id(self, mock_stripe):
        mock_stripe.side_effect = stripe.error.InvalidRequestError("Invalid", "session_id")
        res = self.client.get(SUCCESS_URL, {"session_id": self.payment.session_id})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_cancel(self):
        res = self.client.get(CANCEL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["message"], "Payment was cancelled.")
