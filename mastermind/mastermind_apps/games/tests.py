from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

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

    def setUp(self):
        # Create default game
        self.game = Game.objects.create()
        self.game.generate_random_code()

        self.guess_data = {'pegs': [
            {'color': 'red', 'position': 0},
            {'color': 'green', 'position': 1},
            {'color': 'yellow', 'position': 2},
            {'color': 'green', 'position': 3}
        ]}

    def _create_game(self, data=None):
        url = reverse('games-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        return response

    def test_can_create_a_new_game(self):
        # Test can create a game and the returned data contains the uuid
        data = {'max_guesses': 12}
        response = self._create_game(data)
        game_exists = Game.objects.filter(pk=response.data['uuid'])
        self.assertIsNotNone(game_exists)
        self.assertEqual(response.data['max_guesses'], 12)

        # Test a game code with four random pegs has been created for the new
        # game
        code_exists = Code.objects.filter(
            game_id=response.data['uuid'], is_guess=False)
        self.assertIsNotNone(game_exists)
        self.assertEqual(code_exists[0].pegs.count(), 4)

    def test_can_create_code_guess_and_pegs(self):
        url = reverse('games-guesses', kwargs={'pk': self.game.pk})

        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # Test guess code and pegs are created
        guess_code_exists = Code.objects.filter(game=self.game, is_guess=True)
        self.assertIsNotNone(guess_code_exists)
        self.assertTrue('pegs' in response.data)
        pegs_data = sorted(response.data['pegs'],
                           key=lambda peg: peg['position'])
        self.assertEqual(pegs_data, self.guess_data['pegs'])

        # Test guess returns feedback
        self.assertTrue('feedback' in response.data)
        feedback_data = response.data['feedback']
        self.assertTrue('whites' in feedback_data and
                        'blacks' in feedback_data)

    def test_can_validate_code_guess_and_pegs(self):
        url = reverse('games-guesses', kwargs={'pk': self.game.pk})

        # Test validates correct number of pegs
        response = self.client.post(url, {'pegs': []}, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # Test validates pegs color and position
        self.guess_data['pegs'][0]['color'] = 'purple'
        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.guess_data['pegs'][0]['color'] = 'red'

        self.guess_data['pegs'][0]['position'] = 4
        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.guess_data['pegs'][0]['position'] = 3

        # Test validates game is not finished
        self.game.finished = True
        self.game.save()
        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
