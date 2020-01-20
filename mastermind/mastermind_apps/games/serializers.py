from rest_framework.serializers import ModelSerializer, SerializerMethodField,\
    ValidationError, IntegerField, BooleanField

from mastermind_apps.games.models import Game, Code, Peg
from mastermind_apps.games.response_messages import INVALID_NUMBER_OF_PEGS,\
    GAME_IS_FINISHED


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

        # Add one guess to the game due to the new code guess
        game.n_guesses += 1

        # Check if guess matches game code
        feedback = code.get_feedback()
        if feedback.get('blacks') == 4:
            game.decoded = True

        game.save()

        return code


class GameSerializer(ModelSerializer):
    points = IntegerField(read_only=True)
    finished = BooleanField(read_only=True)
    guesses = SerializerMethodField()
    code = SerializerMethodField()

    class Meta:
        model = Game
        read_only_fields = ('decoded', 'created_at')
        fields = '__all__'

    def create(self, validated_data):
        new_game = super(GameSerializer, self).create(validated_data)

        # Create the code to guess by the codebreaker
        new_game.generate_random_code()

        return new_game

    def get_guesses(self, game):
        return CodeSerializer(
            game.codes.filter(is_guess=True), many=True).data

    def get_code(self, game):
        # We only show the game code if it has finished
        if not game.finished:
            return None

        game_code = game.codes.get(is_guess=False)
        return CodeSerializer(game_code).data
