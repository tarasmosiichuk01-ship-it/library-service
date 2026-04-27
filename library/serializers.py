from datetime import date

from rest_framework import serializers

from library.models import Book, Borrowing


class BookSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "title", "author", "cover", "inventory", "daily_fee")


class BorrowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "borrow_date", "expected_date", "book")

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError({"book": "Inventory cannot be less than 1"})
        return book

    def create(self, validated_data):
        book = validated_data.pop("book")
        book.inventory -= 1
        book.save()
        return Borrowing.objects.create(book=book, **validated_data)


class BookDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)


class BorrowingReturnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    def validate(self, attrs):
        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError("Book has already been returned")
        return attrs

    def update(self, instance, validated_data):
        instance.actual_return_date = date.today()
        instance.save()

        instance.book.inventory += 1
        instance.book.save()

        return instance


