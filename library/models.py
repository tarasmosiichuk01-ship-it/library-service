from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

class Book(models.Model):

    class CoverChoices(models.TextChoices):
        HARD = "hard", "Hard"
        SOFT = "soft", "Soft"

    title = models.CharField(max_length=63, unique=True)
    author = models.CharField(max_length=63, blank=True, null=True)
    cover = models.CharField(max_length=63, choices=CoverChoices.choices, default=CoverChoices.SOFT)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )

    def __str__(self):
        return self.title


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings")


class Payment(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"


    class TypeChoices(models.TextChoices):
        PAYMENT = "payment", "Payment"
        FINE ="fine", "Fine"

    status = models.CharField(max_length=63, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    type = models.CharField(max_length=63, choices=TypeChoices.choices)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name="payments")
    session_url = models.URLField(max_length=255, blank=True, null=True)
    session_id = models.CharField(max_length=255, blank=True, null=True)
    money_to_pay = models.DecimalField(max_digits=6, decimal_places=2, default=0)

