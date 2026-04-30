from unittest.mock import patch
from datetime import date, timedelta
from rest_framework import status
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from library.models import Book, Borrowing

BORROWING_URL = reverse("library:borrowing-list")


def sample_book(**params):
    defaults = {
        "title": "Test Book",
        "author": "Test Author",
        "cover": "Soft",
        "inventory": 4,
        "daily_fee": 4.50,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(user, **params):
    defaults = {
        "expected_date": "2026-05-02",
        "book": sample_book(),
        "user": user,
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class BorrowingAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testemail.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    @patch("library.serializers.stripe_checkout_session")
    @patch("library.serializers.notify_new_borrowing.delay")
    def test_create_borrowing(self, mock_notify, mock_stripe):
        mock_stripe.return_value.id = "test_session_id"
        mock_stripe.return_value.url = "https://stripe.com/test"
        book = sample_book()
        data = {
            "expected_date": "2026-05-10",
            "book": book.id,
        }
        res = self.client.post(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    @patch("library.serializers.stripe_checkout_session")
    @patch(
        "library.serializers.notify_new_borrowing.delay"
    )
    def test_create_borrowing_decreases_inventory(
            self,
            mock_notify,
            mock_stripe
    ):
        mock_stripe.return_value.id = "test_session_id"
        mock_stripe.return_value.url = "https://stripe.com/test"
        book = sample_book()
        data = {
            "expected_date": "2026-05-02",
            "book": book.id,
        }
        initial_inventory = book.inventory
        res = self.client.post(BORROWING_URL, data)
        book.refresh_from_db()
        self.assertEqual(book.inventory, initial_inventory - 1)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_borrowing_no_inventory(self):
        book = sample_book(inventory=0)
        data = {
            "expected_date": "2026-05-08",
            "book": book.id,
        }
        res = self.client.post(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_borrowing_past_expected_date(self):
        book = sample_book()
        data = {
            "expected_date": date.today() - timedelta(days=1),
            "book": book.id,
        }
        res = self.client.post(BORROWING_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_borrowing_increases_inventory(self):
        borrowing = sample_borrowing(user=self.user)
        book = borrowing.book
        initial_inventory = book.inventory
        url = reverse("library:borrowing-return-book", args=[borrowing.id])
        res = self.client.post(url)
        book.refresh_from_db()
        self.assertEqual(book.inventory, initial_inventory + 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
