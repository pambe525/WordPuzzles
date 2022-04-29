from django.contrib.auth import logout
from django.test import TestCase

from django.contrib.auth.models import User

from puzzles.models import WordPuzzle, PuzzleSession
from testing.data_setup_utils import create_user, create_published_puzzle, create_session


class PuzzleScoreViewTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.other_user = create_user(username="other_user")
        self.client.force_login(self.user)
        self.puzzle = create_published_puzzle(editor=self.user, clues_pts=[1,2,2,1,3])

    def test_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/puzzle_score/"+str(self.puzzle.id)+"/")

    def test_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/puzzle_score/50/")
        self.verify_error_msg_in_response(response, 50, "This puzzle does not exist.")
        self.assertTemplateUsed(response, "puzzle_error.html")

    def test_shows_error_if_puzzle_is_not_published(self):
        unpublished_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/puzzle_score/" + str(unpublished_puzzle.id) + "/")
        self.verify_error_msg_in_response(response, unpublished_puzzle.id, "This puzzle is not published.")

    def test_shows_error_if_puzzle_has_no_sessions(self):
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.verify_error_msg_in_response(response, self.puzzle.id, "This puzzle has no solve sessions.")

    def test_response_contains_session_score_data_in_desc_order_of_scores(self):
        session1 = create_session(solver=self.user, puzzle=self.puzzle, solved_clues="1,2,4",
                                   revealed_clues="5", elapsed_secs=280),
        session2 = create_session(solver=self.other_user, puzzle=self.puzzle, solved_clues="3,5", elapsed_secs=150)
        sessions = [session2, session1]    # In desc order of scores
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertTemplateUsed(response, "puzzle_score.html")
        scores = response.context['scores']
        for index, score in enumerate(scores):
            self.assertEqual(score['user'], str(sessions[index].solver))
            self.assertEqual(score['score'], sessions[index].get_solved_points())
            self.assertEqual(score['perc_solved'], sessions[index].get_revealed_points())
            self.assertEqual(score['perc_revealed'], sessions[index].puzzle.total_points)
            self.assertEqual(score['elapsed_secs'], sessions[index].elapsed_seconds)
            self.assertEqual(score['modified_at'], sessions[index].modified_at)

    #==================================================================================================================
    # HELPER METHODS
    def verify_error_msg_in_response(self, response, puzzle_id, msg):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #"+str(puzzle_id))
        self.assertContains(response, msg)
        self.assertContains(response, "OK")