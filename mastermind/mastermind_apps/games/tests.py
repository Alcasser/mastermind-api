from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED

from mastermind_apps.games.models import Game, Code


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


class GamesViewsApiTests(APITestCase):

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
