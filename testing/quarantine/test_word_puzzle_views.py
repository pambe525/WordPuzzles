import json
from unittest.case import skip

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TransactionTestCase

from puzzles.models import WordPuzzle, PuzzleSession
from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle, create_session


@skip
class PreviewPuzzleViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create(username="tester", password="scretkey")
        self.other_user = User.objects.create(username="other_user", password="secretkey2")
        self.client.force_login(self.user)

    def test_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/preview_puzzle/1/")

    def test_shows_error_if_user_is_not_editor_for_draft_puzzle(self):
        puzzle = create_draft_puzzle(self.other_user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/preview_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_draft_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
        puzzle = create_draft_puzzle(editor=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Publish")
        self.assertEqual(response.context['object'], puzzle)

    def test_published_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
        puzzle = create_published_puzzle(editor=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Unpublish")
        self.assertEqual(response.context['object'], puzzle)

    def test_Published_puzzle_contains_correct_heading_for_non_editor(self):
        puzzle = create_published_puzzle(editor=self.other_user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Solve")
        self.assertEqual(response.context['object'], puzzle)
        self.assertIsNone(response.context['active_session'])

    def test_editor_response_context_contains_serialized_clues_list_with_answers(self):
        puzzle = create_published_puzzle(editor=self.user, clues_pts=[4, 2, 1, 4])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertEqual(len(json_clues_list), 4)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index + 1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clues_list[index]['answer'], clues[index].answer)
            self.assertEqual(json_clues_list[index]['parsing'], clues[index].parsing)
            self.assertEqual(json_clues_list[index]['mode'], 'PREVIEW')

    def test_non_editor_response_context_contains_serialized_clues_list_without_answers(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[4, 2, 1])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertEqual(len(json_clues_list), 3)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index + 1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clues_list[index]['answer'], "****-*")
            self.assertEqual(json_clues_list[index]['parsing'], '')
            self.assertEqual(json_clues_list[index]['mode'], 'PRESOLVE')

    def test_redirects_to_solve_puzzle_url_if_puzzle_has_active_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[4, 2, 1])
        create_session(puzzle=puzzle, solver=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertRedirects(response, "/solve_puzzle/" + str(puzzle.id) + "/", 302)


@skip
class SolvePuzzleViewTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create(username="tester", password="scretkey")
        self.other_user = User.objects.create(username="other_user", password="secretkey2")
        self.client.force_login(self.user)

    def test_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/solve_puzzle/1/")

    def test_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/solve_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_shows_error_for_editor_of_draft_puzzle(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[2, 4, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This puzzle is not published.")
        self.assertContains(response, "OK")

    def test_shows_error_for_non_editor_accessing_a_draft_puzzle(self):
        puzzle = create_draft_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_redirects_to_preview_when_editor_accesses_a_published_puzzle(self):
        puzzle = create_published_puzzle(editor=self.user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEquals(response.status_code, 302)
        self.assertEqual(response.url, "/preview_puzzle/" + str(puzzle.id) + "/")

    def test_creates_new_session_and_renders_solve_puzzle_page(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertTemplateUsed(response, "word_puzzle.html")
        self.assertEqual(response.context['heading'], "Solve Puzzle")
        self.assertEqual(response.context['object'], puzzle)
        self.assertIsNotNone(response.context['active_session'])
        json_session = json.loads(response.context['active_session'])
        self.assertEqual(json_session['session_id'], 1)
        self.assertEqual(json_session['elapsed_secs'], 0)
        self.assertEqual(json_session['score'], 0)
        self.assertEqual(json_session['num_clues'], 5)
        self.assertEqual(json_session['num_solved'], 0)
        self.assertEqual(json_session['num_revealed'], 0)

    def test_loads_existing_session_and_renders_solve_puzzle_page(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 2, 4, 5])
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        json_session = json.loads(response.context['active_session'])
        self.assertEqual(json_session['session_id'], 1)
        self.assertEqual(json_session['elapsed_secs'], 0)
        self.assertEqual(json_session['score'], 7)
        self.assertEqual(json_session['num_clues'], 5)
        self.assertEqual(json_session['num_solved'], 2)
        self.assertEqual(json_session['num_revealed'], 2)

    def test_with_existing_session_response_contains_clue_details(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 1, 5], has_parsing=True)
        clues = puzzle.get_clues()
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        json_clues = json.loads(response.context['clues'])
        for index, json_clue in enumerate(json_clues):
            self.assertEqual(json_clue['clue_num'], clues[index].clue_num)
            self.assertEqual(json_clue['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clue['points'], clues[index].points)

    def test_with_existing_session_response_contains_answers_for_solved_and_revealed_clues(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 3, 1, 5], has_parsing=True)
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        json_clues = json.loads(response.context['clues'])
        # SOLVED CLUE
        self.assertEqual(json_clues[0]['mode'], 'SOLVED')
        self.assertEqual(json_clues[0]['answer'], 'WORD-A')
        self.assertEqual(json_clues[0]['parsing'], 'Parsing for wordA')
        # REVEALED CLUE
        self.assertEqual(json_clues[1]['mode'], 'REVEALED')
        self.assertEqual(json_clues[1]['answer'], 'WORD-B')
        self.assertEqual(json_clues[1]['parsing'], 'Parsing for wordB')
        # UNSOLVED CLUE
        self.assertEqual(json_clues[3]['mode'], 'UNSOLVED')
        self.assertEqual(json_clues[3]['answer'], '****-*')  # Unsolved clue includes masked answer
        self.assertEqual(json_clues[3]['parsing'], '')

    def test_ajax_post_with_correct_answer_returns_updated_response(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[1, 3, 3, 1, 5])
        session = create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='3,4')
        data = json.dumps({'session_id': session.id, 'clue_num': 2, 'answer_input': 'WORD-B'})
        post_data = {'action': 'solve', 'data': data}
        response = self.client.post("/solve_puzzle/" + str(puzzle.id) + "/", post_data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(response.content)
        clues = json.loads(json_data['clues'])
        active_session = json_data['active_session']
        self.assertEqual(len(clues), 5)
        self.assertEqual(clues[1]['mode'], 'SOLVED')
        self.assertEqual(clues[1]['answer'], 'WORD-B')
        self.assertEqual(active_session['score'], 9)
        self.assertEqual(active_session['num_clues'], 5)
        self.assertEqual(active_session['num_solved'], 3)
        self.assertEqual(active_session['num_revealed'], 2)
        # Ensure score is re-calculated on save of correct answer
        session = PuzzleSession.objects.get(id=session.id)
        self.assertEqual(session.score, 9)

    def test_ajax_post_with_reveal_answer_returns_updated_response(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[1, 2, 3, 1, 5])
        session = create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='3')
        data = json.dumps({'session_id': session.id, 'clue_num': 2})
        response = self.client.post("/solve_puzzle/" + str(puzzle.id) + "/", {'action': 'reveal', 'data': data},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_data = json.loads(response.content)
        clues = json.loads(json_data['clues'])
        active_session = json_data['active_session']
        self.assertEqual(len(clues), 5)
        self.assertEqual(clues[1]['mode'], 'REVEALED')
        self.assertEqual(clues[1]['answer'], 'WORD-B')
        self.assertEqual(active_session['score'], 6)
        self.assertEqual(active_session['num_clues'], 5)
        self.assertEqual(active_session['num_solved'], 2)
        self.assertEqual(active_session['num_revealed'], 2)

    def test_ajax_post_with_wrong_answer_raises_error(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[1, 3, 3, 1, 5])
        session = create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        data = json.dumps({'session_id': session.id, 'clue_num': 2, 'answer_input': 'WORD-C'})
        post_data = {'action': 'solve', 'data': data}
        with self.assertRaises(AssertionError) as e:
            self.client.post("/solve_puzzle/" + str(puzzle.id) + "/", post_data,
                             HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(str(e.exception), "Incorrect answer")

    def test_ajax_post_with_timer_saves_elapsed_secs(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[1, 3, 1, 5, 4])
        session = create_session(puzzle=puzzle, solver=self.user, solved_clues='1,4', revealed_clues='2')
        data = json.dumps({'session_id': session.id, 'elapsed_secs': 1234})
        post_data = {'action': 'timer', 'data': data}
        self.client.post("/solve_puzzle/" + str(puzzle.id) + "/", post_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        session = PuzzleSession.objects.get(id=session.id)
        self.assertEqual(session.elapsed_seconds, 1234)
