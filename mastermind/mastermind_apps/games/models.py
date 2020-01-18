from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from mastermind_apps.games.choices import MAX_CODE_GUESSES, PEG_COLORS


class Game(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid4,
                            editable=False)
    max_guesses = models.IntegerField(choices=MAX_CODE_GUESSES, default=10)
    finished = models.BooleanField(default=False)
    decoded = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class Code(models.Model):
    game = models.ForeignKey(
        Game, related_name='codes', on_delete=models.CASCADE)
    is_guess = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Peg(models.Model):
    code = models.ForeignKey(
        Code, related_name='pegs', on_delete=models.CASCADE)
    color = models.CharField(choices=PEG_COLORS, max_length=6)
    position = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(3)])
    created_at = models.DateTimeField(auto_now_add=True)
