from rest_framework.serializers import ModelSerializer, SerializerMethodField

from mastermind_apps.games.models import Game, Code


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


class CodeSerializer(ModelSerializer):
    feedback = SerializerMethodField()

    class Meta:
        model = Code
        read_only_fields = ('game', 'is_guess', 'created_at')
        exclude = ('id',)

    def get_feedback(self, code):
        return code.get_feedback()
