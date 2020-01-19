from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from mastermind_apps.games.models import Game
from mastermind_apps.games.serializers import GameSerializer, CodeSerializer


class GameViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    @action(detail=True, methods=['post'])
    def guesses(self, request, *args, **kwargs):
        game = self.get_object()

        serializer = CodeSerializer(
            data=request.data, context={'game': game})
        if serializer.is_valid():
            serializer.save(game=game)
            return Response(serializer.data, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
