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
        self.puzzle = create_published_puzzle(editor=self.user, clues_pts=[1, 2, 2, 1, 3])

    def test_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/puzzle_score/" + str(self.puzzle.id) + "/")

    def test_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/puzzle_score/50/")
        self.verify_error_msg_in_response(response, 50, "This puzzle does not exist.")
        self.assertTemplateUsed(response, "puzzle_error.html")

    def test_shows_error_if_puzzle_is_not_published(self):
        unpublished_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/puzzle_score/" + str(unpublished_puzzle.id) + "/")
        self.verify_error_msg_in_response(response, unpublished_puzzle.id, "This puzzle is not published.")

    def test_response_contains_empty_scores_list_if_puzzle_has_no_sessions(self):
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertIsNone(response.context['scores'])

    def test_get_response_contains_session_score_data_in_desc_order_of_scores(self):
        session1 = create_session(solver=self.user, puzzle=self.puzzle, solved_clues="1,2,4",
                                  revealed_clues="5", elapsed_secs=280)
        session2 = create_session(solver=self.other_user, puzzle=self.puzzle, solved_clues="3,5", elapsed_secs=150)
        session3 = create_session(solver=self.user, puzzle=self.puzzle, solved_clues="1,2,4,5",
                                  revealed_clues="3", elapsed_secs=400)
        sessions = [session3, session2, session1]  # In desc order of scores
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertTemplateUsed(response, "puzzle_score.html")
        session_scores = response.context['scores']
        elapsed_time = ["0:06:40s", "0:02:30s", "0:04:40s"]
        perc_solved = ["80%", "40%", "60%"]
        perc_revealed = ["20%", "0%", "20%"]
        num_solved = [4, 2, 3]
        num_revealed = [1, 0, 1]
        is_complete = [True, False, False]
        for index, session_score in enumerate(session_scores):
            session = sessions[index]
            self.assertEqual(session_score['user'], str(session.solver))
            self.assertEqual(session_score['score'], session.score)
            self.assertEqual(session_score['perc_solved'], perc_solved[index])
            self.assertEqual(session_score['perc_revealed'], perc_revealed[index])
            self.assertEqual(session_score['num_solved'], num_solved[index])
            self.assertEqual(session_score['num_revealed'], num_revealed[index])
            self.assertEqual(session_score['is_complete'], is_complete[index])
            self.assertEqual(session_score['elapsed_time'], elapsed_time[index])
            self.assertEqual(session_score['modified_at'], session.modified_at)

    def test_get_response_contains_puzzle_object(self):
        response = self.client.get("/puzzle_score/" + str(self.puzzle.id) + "/")
        self.assertEqual(self.puzzle, response.context['object'])


    # ==================================================================================================================
    # HELPER METHODS
    def verify_error_msg_in_response(self, response, puzzle_id, msg):
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle_id))
        self.assertContains(response, msg)
        self.assertContains(response, "OK")
