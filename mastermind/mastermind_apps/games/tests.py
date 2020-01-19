from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED

from mastermind_apps.games.models import Game, Code


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
