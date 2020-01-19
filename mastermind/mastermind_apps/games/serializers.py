from rest_framework.serializers import ModelSerializer, SerializerMethodField,\
    ValidationError

from mastermind_apps.games.models import Game, Code, Peg
from mastermind_apps.games.response_messages import INVALID_NUMBER_OF_PEGS,\
    GAME_IS_FINISHED


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


class PegSerializer(ModelSerializer):
    class Meta:
        model = Peg
        exclude = ('id', 'code', 'created_at')


class CodeSerializer(ModelSerializer):
    feedback = SerializerMethodField()
    pegs = PegSerializer(many=True)

    class Meta:
        model = Code
        read_only_fields = ('game', 'is_guess', 'created_at')
        exclude = ('id',)

    def get_feedback(self, code):
        return code.get_feedback()

    def validate(self, attrs):
        game = self.context.get('game')
        if game.finished:
            raise ValidationError(GAME_IS_FINISHED)

        pegs_data = attrs.get('pegs')
        if len(pegs_data) != 4:
            raise ValidationError(INVALID_NUMBER_OF_PEGS)

        return attrs

    def create(self, validated_data):
        game = self.context.get('game')

        # Obtain the pegs data and create the code
        pegs_data = validated_data.pop('pegs')
        code = Code.objects.create(**validated_data)

        # Create the code pegs
        for peg_data in pegs_data:
            Peg.objects.create(code=code, **peg_data)

        # Add one point to the game due to the new code guess
        game.points += 1

        # Check if guess matches game code
        feedback = code.get_feedback()
        if feedback.get('blacks') == 4:
            game.decoded = True
            game.finished = True

        # Check if this was the last guess attempt
        guess_attempts = Code.objects.filter(game=game, is_guess=True).count()
        if guess_attempts == game.max_guesses:
            game.finished = True
            if not game.decoded:
                game.points += 1

        game.save()

        return code
