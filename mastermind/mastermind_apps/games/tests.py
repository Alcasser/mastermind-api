from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED

from mastermind_apps.games.models import Game, Code, Peg


class GameTestCase(TestCase):

    def setUp(self):
        self.game = Game.objects.create()

    def game_can_create_code_to_guess(self):
        code = self.game.generate_random_code()

        # One code with four pegs are created
        code_exists = Code.objects.filter(game=self.game, is_guess=False)
        self.assertTrue(code_exists)
        self.assertEqual(code.pk, code_exists[0].pk)
        self.assertEqual(code.pegs.count(), 4)

        # No more codes are created
        code = self.game.generate_random_code()
        self.assertIsNone(code)
        self.assertEqual(Code.objects.count(), 1)


class CodeTestCase(TestCase):

    def setUp(self):
        self.game = Game.objects.create()
        self.game_colors = ['red', 'blue', 'green', 'red']
        self.game_code = self._create_code_with_colors(
            self.game_colors, is_guess=False)

    def _create_code_with_colors(self, colors, is_guess):
        code = Code.objects.create(game=self.game, is_guess=is_guess)
        for position in range(Code.NUMBER_OF_PEGS):
            Peg.objects.create(
                code=code, position=position, color=colors[position])

        return code

    def test_can_get_correct_code_feedback(self):
        guess_colors = ['red', 'green', 'red', 'yellow']
        guess_code = self._create_code_with_colors(guess_colors, is_guess=True)

        # Test feedback is correct
        self.assertEqual(guess_code.get_feedback(), {'blacks': 1, 'whites': 2})
        self.assertIsNone(self.game_code.get_feedback())

    def test_can_get_peg_colors_list(self):
        self.assertEqual(self.game_code.get_peg_colors(), self.game_colors)


class GamesViewsApiTestCase(APITestCase):

    def _create_game(self, data=None):
        url = reverse('games-list')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        return response

    def test_can_create_a_new_game(self):
        # Test can create a game with specific number of guesses
        data = {'max_guesses': 12}
        response = self._create_game(data)
        self.assertEqual(Game.objects.count(), 1)
        self.assertEqual(response.data['max_guesses'], 12)

        # Test can create default game and the returned data contains the uuid
        response = self._create_game()
        game_exists = Game.objects.filter(pk=response.data['uuid'])
        self.assertIsNotNone(game_exists)
        self.assertEqual(Game.objects.count(), 2)
        self.assertEqual(response.data['max_guesses'], 10)

    def test_code_with_random_pegs_are_created(self):
        self._create_game()

        # Test a game code with four random pegs has been created for the new
        # game
        code = Code.objects.first()
        self.assertEqual(Code.objects.count(), 1)
        self.assertEqual(code.pegs.count(), 4)

    def test_can_create_code_guess(self):
        # Create default game
        game = Game.objects.create()
        game_code = game.generate_random_code()

        url = reverse('games-guesses', kwargs={'pk': game.pk})

        # Test guess returns correct feedback
        guess_data = {'pegs': [
            {'color': 'red', 'position': 0},
            {'color': 'green', 'position': 1},
            {'color': 'yellow', 'position': 2},
            {'color': 'green', 'position': 3}
        ]}
        response = self.client.post(url, guess_data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertTrue('feedback' in response.data)
        feedback_data = response.data['feedback']
        self.assertTrue('whites' in feedback_data and
                        'blacks' in feedback_data)
