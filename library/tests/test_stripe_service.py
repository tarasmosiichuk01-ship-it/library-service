from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.test import TestCase

from library.models import Book, Borrowing
from library.stripe_service import stripe_checkout_session


class TestStripeService(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testemail.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    @patch("library.stripe_service.stripe.checkout.Session.create")
    def test_stripe_checkout_session(self, mock_create):
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Hard",
            inventory=9,
            daily_fee=10.00,
        )
        borrowing = Borrowing.objects.create(
            expected_date=date.today() + timedelta(days=3),
            book=book,
            user=self.user,
        )
        mock_create.return_value.id = "test_session_id"
        mock_create.return_value.url = "https://stripe.com/test"

        stripe_checkout_session(borrowing)

        days = (borrowing.expected_date - borrowing.borrow_date).days
        expected_amount = int(days * book.daily_fee * 100)
        call_kwargs = mock_create.call_args[1]
        unit_amount = call_kwargs["line_items"][0]["price_data"]["unit_amount"]
        self.assertEqual(unit_amount, expected_amount)

    @patch("library.stripe_service.stripe.checkout.Session.create")
    def test_stripe_returns_session_object(self, mock_create):
        mock_create.return_value.id = "test_session_id"
        mock_create.return_value.url = "https://stripe.com/test"

        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Hard",
            inventory=9,
            daily_fee=10.00,
        )
        borrowing = Borrowing.objects.create(
            expected_date=date.today() + timedelta(days=3),
            book=book,
            user=self.user,
        )

        session = stripe_checkout_session(borrowing)

        self.assertEqual(session.id, "test_session_id")
        self.assertEqual(session.url, "https://stripe.com/test")

