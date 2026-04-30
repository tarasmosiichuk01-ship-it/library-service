from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from library.models import Book, Borrowing, Payment
from library.tasks import (
    notify_new_borrowing,
    notify_overdue_borrowings,
    notify_successful_payment
)


class TestTasks(TestCase):
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
            inventory=9,
            daily_fee=8.00,
        )
        self.borrowing = Borrowing.objects.create(
            expected_date="2026-05-16",
            book=self.book,
            user=self.user,
        )
        self.payment = Payment.objects.create(
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
            borrowing=self.borrowing,
            session_url="https://stripe.com/test",
            session_id="test_session_id",
            money_to_pay=Decimal("11.00"),
        )

    @patch("library.tasks.send_telegram_notification")
    def test_notify_new_borrowing(self, mock_notify):
        message = (
            f"New borrowing: title: {self.borrowing.book.title}, "
            f"borrow date: {self.borrowing.borrow_date}, "
            f"expected date: {self.borrowing.expected_date}"
        )
        notify_new_borrowing(self.borrowing.id)
        mock_notify.assert_called_once()
        mock_notify.assert_called_with(message)

    @patch(
        "library.tasks.send_telegram_notification"
    )
    def test_notify_overdue_borrowings_with_overduer(self, mock_notify):
        borrowings = Borrowing.objects.create(
            expected_date=date.today() - timedelta(days=1),
            actual_return_date=None,
            book=self.book,
            user=self.user,
        )
        message = "\n".join([
            "Found 1 overdue borrowings:",
            f"Book: {self.book.title}, "
            f"Expected date: {borrowings.expected_date}, "
            f"Days overdue: {(date.today() - borrowings.expected_date).days}, "
            f"User: {self.user.email}"
        ])
        notify_overdue_borrowings()
        mock_notify.assert_called_once()
        mock_notify.assert_called_once_with(message)

    @patch("library.tasks.send_telegram_notification")
    def test_notify_overdue_borrowings_without_overdue(self, mock_notify):
        message = "No overdue borrowings today!"
        notify_overdue_borrowings()
        mock_notify.assert_called_once()
        mock_notify.assert_called_once_with(message)

    @patch("library.tasks.send_telegram_notification")
    def test_notify_successful_payment(self, mock_notify):
        message = (
            f"Your payment was successful! "
            f"User: {self.payment.borrowing.user.email}, "
            f"book: {self.payment.borrowing.book.title}, "
            f"payment amount: {self.payment.money_to_pay} $, "
            f"type: {self.payment.type}, "
            f"date: {date.today()}"
        )
        notify_successful_payment(self.payment.id)
        mock_notify.assert_called_once()
        mock_notify.assert_called_once_with(message)
