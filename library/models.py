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
