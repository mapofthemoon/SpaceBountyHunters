from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class WantedCriminal(models.Model):
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    nickname = models.CharField(max_length=100)

    reward = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    latitude = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )

    longitude = models.FloatField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )

    last_known_note = models.TextField(blank=True)

    difficulty = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    armed = models.BooleanField(default=False)
    has_crew = models.BooleanField(default=False)
    escape_master = models.BooleanField(default=False)

    def __str__(self):
        return self.nickname


class HuntLog(models.Model):
    criminal = models.ForeignKey(
        WantedCriminal,
        on_delete=models.CASCADE,
        related_name="hunt_logs"
    )

    success = models.BooleanField(default=False)
    notes = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hunt #{self.id} - {self.criminal.nickname}"
