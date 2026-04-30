from datetime import date

from django.db import transaction
from rest_framework import serializers

from library.models import Book, Borrowing, Payment
from library.stripe_service import stripe_checkout_session
from library.tasks import notify_new_borrowing


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BorrowingSerializer(serializers.ModelSerializer):
    session_url = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_date", "book", "session_url")

    def get_session_url(self, obj):
        payment = obj.payments.last()
        if payment:
            return payment.session_url
        return None

    def validate_expected_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(
                "Expected date must be in future"
            )
        return value

    def create(self, validated_data):
        book = validated_data.pop("book")
        request = self.context["request"]

        with transaction.atomic():
            if book.inventory < 1:
                raise serializers.ValidationError("No books available")

            book.inventory -= 1
            book.save()

            borrowing = Borrowing.objects.create(
                book=book,
                user=request.user,
                **validated_data
            )

            notify_new_borrowing.delay(borrowing.id)

            session = stripe_checkout_session(borrowing)
            Payment.objects.create(
                session_id=session.id,
                session_url=session.url,
                borrowing=borrowing,
                money_to_pay=((
                                      borrowing.expected_date
                                      - borrowing.borrow_date
                              ).days) * book.daily_fee,
                type=Payment.TypeChoices.PAYMENT
            )
            return borrowing


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_date",
            "actual_return_date",
            "book",
        )


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("Book has already been returned")
        return attrs

    def update(self, instance, validated_data):
        with transaction.atomic():
            if instance.actual_return_date:
                raise serializers.ValidationError("Already returned")
            instance.actual_return_date = date.today()
            instance.save()

            instance.book.inventory += 1
            instance.book.save()

        return instance


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )
        read_only_fields = ("id", "session_url", "session_id")
