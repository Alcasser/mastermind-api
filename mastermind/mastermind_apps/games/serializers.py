from rest_framework.serializers import ModelSerializer

from mastermind_apps.games.models import Game


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        read_only_fields = ('finised', 'decoded', 'points', 'created_at')
        fields = '__all__'
