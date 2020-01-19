from rest_framework import viewsets, mixins

from mastermind_apps.games.models import Game
from mastermind_apps.games.serializers import GameSerializer


class GameViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
