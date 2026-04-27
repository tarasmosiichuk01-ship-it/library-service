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
    inventory = models.PositiveIntegerField(null=True)
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00)],
    )


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
