from uuid import uuid4

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from mastermind_apps.games.choices import MAX_CODE_GUESSES, PEG_COLORS


class Game(models.Model):
    """
    This is the game model. The pk is a uuid used by the codebreaker to
    continue playing a given game.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid4,
                            editable=False)
    max_guesses = models.IntegerField(choices=MAX_CODE_GUESSES, default=10)
    finished = models.BooleanField(default=False)
    decoded = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} - finished: {self.finished} - ' \
               f'decoded: {self.decoded} - points: {self.points}'


class Code(models.Model):
    """
    The codes of a given game contain the guesses and the actual game code to
    discover.
    """

    game = models.ForeignKey(
        Game, related_name='codes', on_delete=models.CASCADE)
    is_guess = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} - game: {self.game.pk} - is_guess: {self.is_guess}'


class Peg(models.Model):
    """
    There are always four pegs for a given code (blanks not allowed) and there
    can be pegs with repeated colors.
    """
    code = models.ForeignKey(
        Code, related_name='pegs', on_delete=models.CASCADE)
    color = models.CharField(choices=PEG_COLORS, max_length=6)
    position = models.IntegerField(
        validators=[MinValueValidator(0),
                    MaxValueValidator(3)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} - code: {self.code.pk} ' \
               f'- ({self.color}, {self.position})'
