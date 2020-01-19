from rest_framework.serializers import ModelSerializer

from mastermind_apps.games.models import Game


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        read_only_fields = ('finised', 'decoded', 'points', 'created_at')
        fields = '__all__'

    def create(self, validated_data):
        new_game = super(GameSerializer, self).create(validated_data)

        # Create the code to guess by the codebreaker
        new_game.generate_random_code()

        return new_game
