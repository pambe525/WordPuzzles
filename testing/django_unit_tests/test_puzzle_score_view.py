from unittest.case import skip

from django.contrib.auth import logout
from django.test import TestCase
from django.utils.timezone import now

from puzzles.models import WordPuzzle, SolverSession
from testing.data_setup_utils import create_user, create_published_puzzle, create_session


class PuzzleScoreViewTests(TestCase):
    def setUp(self):
        self.user1 = create_user()
        self.user2 = create_user(username="user2", email="abc@xyz.com")
        self.user3 = create_user(username="user3", email="xyz@xyz.com")
        self.client.force_login(self.user1)
        self.puzzle = create_published_puzzle(editor=self.user1, clues_pts=[1, 2, 2, 1, 3, 1, 4])

    def test_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/puzzle_score/" + str(self.puzzle.id) + "/")

    def test_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/puzzle_score/50/")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertTemplateUsed(response, "puzzle_error.html")

    def test_shows_error_if_puzzle_is_not_published(self):
        unpublished_puzzle = WordPuzzle.objects.create(editor=self.user1)
        response = self.client.get("/puzzle_score/" + str(unpublished_puzzle.id) + "/")
        self.assertContains(response, "This puzzle is not published.")

    def test_response_contains_no_scores_if_puzzle_has_no_sessions(self):
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertEqual(response.context['object'], self.puzzle)
        self.assertIsNone(response.context['sessions'])

    def test_response_contains_session_score_data_in_desc_order_of_scores(self):
        session1 = create_session(self.puzzle, self.user3, 3, 0, 8)
        session2 = create_session(self.puzzle, self.user2, 7, 2, 21)
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertTemplateUsed(response, "puzzle_score.html")
        self.assertEqual(response.context['sessions'][0], session2)
        self.assertEqual(response.context['sessions'][1], session1)


