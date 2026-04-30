from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

from library.models import Book
from library.serializers import BookSerializer

BOOK_URL = reverse("library:book-list")


class UnauthenticatedTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BOOK_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@testemail.com",
            password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_book_list(self):
        Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Soft",
            inventory=5,
            daily_fee=2.50,
        )
        res = self.client.get(BOOK_URL)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.data, serializer.data)
