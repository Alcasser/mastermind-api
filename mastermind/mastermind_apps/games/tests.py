from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST,\
    HTTP_200_OK

from mastermind_apps.games.models import Game, Code, Peg


class GameTestCase(TestCase):

    def setUp(self):
        self.game = Game.objects.create()
        self.game_code = self.game.generate_random_code()

    def test_game_can_create_code_to_guess(self):
        # One code with four pegs are created
        code_exists = Code.objects.filter(game=self.game, is_guess=False)
        self.assertTrue(code_exists)
        self.assertEqual(self.game_code.pk, code_exists[0].pk)
        self.assertEqual(self.game_code.pegs.count(), 4)

        # No more codes are created
        code = self.game.generate_random_code()
        self.assertIsNone(code)
        self.assertEqual(Code.objects.count(), 1)

    def test_game_points_property(self):
        # Test points increment with guesses
        self.game.n_guesses += 1
        self.game.save()
        self.assertEqual(self.game.points, 1)

        # Test one extra point is given if max_guesses is reached without the
        # game being decoded
        self.game.n_guesses = self.game.max_guesses
        self.game.save()
        self.assertEqual(self.game.points, self.game.max_guesses + 1)

    def test_game_finished_property(self):
        # Test game is finished when decoded
        self.game.decoded = True
        self.game.save()
        self.assertTrue(self.game.finished)

        # Test game is finished when max_guesses is reached
        self.game.decoded = False
        self.game.n_guesses = self.game.max_guesses
        self.game.save()
        self.assertTrue(self.game.finished)


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
        # Test feedback is correct
        guess_colors = ['red', 'green', 'red', 'yellow']
        guess_code = self._create_code_with_colors(guess_colors, is_guess=True)
        self.assertEqual(guess_code.get_feedback(), {'blacks': 1, 'whites': 2})

        guess_code = self._create_code_with_colors(
            self.game_colors, is_guess=True)
        self.assertEqual(guess_code.get_feedback(), {'blacks': 4, 'whites': 0})

        # Test feedback is none for game code
        self.assertIsNone(self.game_code.get_feedback())

    def test_can_get_peg_colors_list(self):
        self.assertEqual(self.game_code.get_peg_colors(), self.game_colors)


class GamesViewsApiTestCase(APITestCase):

    def setUp(self):
        # Create default game
        self.game = Game.objects.create()
        self.game_code = self.game.generate_random_code()

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

    def _set_game_code_colors(self):
        # Set game code colors or guess could match
        for peg in self.game_code.pegs.all():
            peg.color = 'red'
            peg.save()

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
        self.game.decoded = True
        self.game.save()
        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_can_increment_guess_on_each_code_guess(self):
        url = reverse('games-guesses', kwargs={'pk': self.game.pk})

        self.assertEqual(self.game.n_guesses, 0)
        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.game.refresh_from_db()
        self.assertEqual(self.game.n_guesses, 1)

    def test_can_set_decoded_when_guess_matches(self):
        url = reverse('games-guesses', kwargs={'pk': self.game.pk})

        # Set game code colors to match guess code
        for peg in self.game_code.pegs.order_by('position'):
            peg.color = self.guess_data['pegs'][peg.position]['color']
            peg.save()

        response = self.client.post(url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.game.refresh_from_db()
        self.assertTrue(self.game.decoded)

    def test_can_get_game_historic_code_guesses_and_game_code(self):
        guesses_url = reverse('games-guesses', kwargs={'pk': self.game.pk})
        game_url = reverse('games-detail', kwargs={'pk': self.game.pk})
        self._create_game()

        response = self.client.post(
            guesses_url, self.guess_data, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # Test serializer returns the code guesses but not the game code
        response = self.client.get(game_url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue('guesses' in response.data)
        self.assertEqual(len(response.data['guesses']), 1)
        self.assertIsNone(response.data['code'])

        # Test returns the game code if finished
        self.game.decoded = True
        self.game.save()
        response = self.client.get(game_url)
        self.assertTrue('guesses' in response.data)
        self.assertIsNotNone(response.data['code'])
