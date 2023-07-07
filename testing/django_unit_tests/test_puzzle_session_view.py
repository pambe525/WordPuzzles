import json
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.utils.timezone import now

from puzzles.models import WordPuzzle, SolverSession, SolvedClue
from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle


# class PreviewPuzzleViewTest(TransactionTestCase):
#     reset_sequences = True
#
#     def setUp(self):
#         self.user = User.objects.create(username="tester", password="scretkey")
#         self.other_user = User.objects.create(username="other_user", password="secretkey2")
#         self.client.force_login(self.user)
#
#     def test_redirects_to_login_view_if_user_is_not_authenticated(self):
#         logout(self.client)
#         puzzle = WordPuzzle.objects.create(editor=self.user)
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         self.assertEqual(response.status_code, 302)
#         self.assertEqual(response.url, "/login?next=/preview_puzzle/1/")
#
#     def test_shows_error_if_user_is_not_editor_for_draft_puzzle(self):
#         puzzle = create_draft_puzzle(self.other_user)
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Puzzle #" + str(puzzle.id))
#         self.assertContains(response, "This operation is not permitted since you are not the editor.")
#         self.assertContains(response, "OK")
#
#     def test_shows_error_if_puzzle_does_not_exist(self):
#         response = self.client.get("/preview_puzzle/50/")
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, "puzzle_error.html")
#         self.assertContains(response, "Puzzle #50")
#         self.assertContains(response, "This puzzle does not exist.")
#         self.assertContains(response, "OK")
#
#     def test_draft_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
#         puzzle = create_draft_puzzle(editor=self.user)
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         self.assertEqual(response.context['heading'], "Preview Puzzle & Publish")
#         self.assertEqual(response.context['object'], puzzle)
#
#     def test_published_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
#         puzzle = create_published_puzzle(editor=self.user)
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         self.assertEqual(response.context['heading'], "Preview Puzzle & Unpublish")
#         self.assertEqual(response.context['object'], puzzle)
#
#     def test_Published_puzzle_contains_correct_heading_for_non_editor(self):
#         puzzle = create_published_puzzle(editor=self.other_user)
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         self.assertEqual(response.context['heading'], "Preview Puzzle & Solve")
#         self.assertEqual(response.context['object'], puzzle)
#         self.assertIsNone(response.context['active_session'])
#
#     def test_editor_response_context_contains_serialized_clues_list_with_answers(self):
#         puzzle = create_published_puzzle(editor=self.user, clues_pts=[4, 2, 1, 4])
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         clues = puzzle.get_clues()
#         json_clues_list = json.loads(response.context['clues'])
#         self.assertEqual(len(json_clues_list), 4)
#         for index in range(0, len(json_clues_list)):
#             self.assertEqual(json_clues_list[index]['clue_num'], index + 1)
#             self.assertEqual(json_clues_list[index]['points'], clues[index].points)
#             self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
#             self.assertEqual(json_clues_list[index]['answer'], clues[index].answer)
#             self.assertEqual(json_clues_list[index]['parsing'], clues[index].parsing)
#             self.assertEqual(json_clues_list[index]['mode'], 'PREVIEW')
#
#     def test_non_editor_response_context_contains_serialized_clues_list_without_answers(self):
#         puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[4, 2, 1])
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         clues = puzzle.get_clues()
#         json_clues_list = json.loads(response.context['clues'])
#         self.assertEqual(len(json_clues_list), 3)
#         for index in range(0, len(json_clues_list)):
#             self.assertEqual(json_clues_list[index]['clue_num'], index + 1)
#             self.assertEqual(json_clues_list[index]['points'], clues[index].points)
#             self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
#             self.assertEqual(json_clues_list[index]['answer'], "****-*")
#             self.assertEqual(json_clues_list[index]['parsing'], '')
#             self.assertEqual(json_clues_list[index]['mode'], 'PRESOLVE')
#
#     def test_redirects_to_solve_puzzle_url_if_puzzle_has_active_session(self):
#         puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[4, 2, 1])
#         create_session(puzzle=puzzle, solver=self.user)
#         response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
#         self.assertRedirects(response, "/solve_puzzle/" + str(puzzle.id) + "/", 302)


class PuzzleSessionViewTest(TransactionTestCase):
    reset_sequences = True
    target_page = "/puzzle_session/"

    def setUp(self):
        self.user = User.objects.create(username="tester", password="scretkey")
        self.other_user = User.objects.create(username="other_user", password="secretkey2", email="abc@cde.com")
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/puzzle_session/1/")

    def test_GET_has_error_if_puzzle_does_not_exist(self):
        response = self.client.get(self.target_page + "50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle 50")
        self.assertContains(response, "This puzzle does not exist.")

    def test_GET_has_error_if_puzzle_is_not_published(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[2, 4, 1, 4, 5])
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertEqual(response.context['err_msg'], "This puzzle is not published.")

    def test_GET_redirects_to_edit_puzzle_view_if_user_is_editor(self):
        puzzle = create_published_puzzle(editor=self.user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/edit_puzzle/" + str(puzzle.id) + "/")

    def test_GET_returns_response_with_no_active_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        clues = puzzle.get_clues()
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.context['puzzle'], puzzle)
        self.assertEqual(len(response.context['clues']), len(clues))
        first_clue = response.context['clues'][0]
        self.assertEqual(first_clue.clue_num, clues[0].clue_num)
        self.assertEqual(first_clue.clue_text, clues[0].get_decorated_clue_text())
        self.assertEqual(first_clue.points, clues[0].points)
        self.assertEqual(first_clue.state, 0)
        self.assertIsNone(response.context['session'])

    def test_POST_creates_new_solve_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.post(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.target_page + str(puzzle.id) + "/")
        session = SolverSession.objects.get(puzzle=puzzle, solver=self.user)
        self.assertLessEqual(session.started_at, now())
        self.assertIsNone(session.finished_at)
        self.assertIsNone(session.group_session)

    def test_GET_returns_response_with_existing_solve_session_info(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        clues = puzzle.get_clues()
        session = SolverSession.objects.create(puzzle=puzzle, solver=self.user)
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.context['puzzle'], puzzle)
        self.assertEqual(len(response.context['clues']), len(clues))
        self.assertIsNotNone(response.context['session'])
        self.assertEqual(response.context['session'].score, 0)
        self.assertEqual(response.context['session'].solved, 0)
        self.assertEqual(response.context['session'].revealed, 0)
        self.assertIsNone(session.finished_at)

    def test_GET_with_previous_session_returns_solved_and_revealed_clues_with_score(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 1])
        clues = puzzle.get_clues()
        session = SolverSession.objects.create(puzzle=puzzle, solver=self.user)
        SolvedClue.objects.create(clue=clues[1], solver=self.user, session=session)
        SolvedClue.objects.create(clue=clues[3], solver=self.user, session=session)
        SolvedClue.objects.create(clue=clues[4], solver=self.user, session=session, revealed=True)
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.context['puzzle'], puzzle)
        self.assertEqual(len(response.context['clues']), len(clues))
        self.assertEqual(response.context['clues'][1].state, 1)
        self.assertEqual(response.context['clues'][3].state, 1)
        self.assertEqual(response.context['clues'][4].state, 2)
        self.assertEqual(response.context['session'], session)
        self.assertEqual(response.context['session'].score, 7)
        self.assertEqual(response.context['session'].solved, 2)
        self.assertEqual(response.context['session'].revealed, 1)
        self.assertIsNone(session.finished_at)


class AjaxAnswerRequestTest(TransactionTestCase):
    reset_sequences = True
    target_page = "/ajax_answer_request"

    def setUp(self):
        self.user = User.objects.create(username="tester", password="scretkey")
        self.other_user = User.objects.create(username="other_user", password="secretkey2", email="abc@cde.com")
        self.client.force_login(self.user)

    def test_POST_checks_invalid_answer(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        session = SolverSession.objects.create(puzzle=puzzle, solver=self.user)
        data = {'action': 'check', 'data': {'session_id': session.id, 'puzzle_id': puzzle.id, 'clue_num': 2,
                'input_answer': 'WORD A'}}
        response = self.client.post(self.target_page, data=data, content_type='application/json')
        self.assertEqual(json.loads(response.content)['err_msg'], "Answer is incorrect.")

    def test_POST_with_valid_answer_saves_solved_clue_and_reloads_page(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        clues = puzzle.get_clues()
        session = SolverSession.objects.create(puzzle=puzzle, solver=self.user)
        data = {'action': 'check', 'data': {'session_id': session.id, 'puzzle_id': puzzle.id, 'clue_num': 2,
                'input_answer': clues[1].answer}}
        response = self.client.post(self.target_page, data=data, content_type='application/json')
        self.assertEqual(json.loads(response.content)['err_msg'], "")
        solved_clue = SolvedClue.objects.get(session=session, clue=clues[1], solver=self.user)
        self.assertFalse(solved_clue.revealed)
        self.assertTemplateUsed("puzzle_session.html")

    def test_POST_with_reveal_action_saves_clue_as_revealed(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        clues = puzzle.get_clues()
        session = SolverSession.objects.create(puzzle=puzzle, solver=self.user)
        data = {'action': 'reveal', 'data':{'session_id': session.id, 'puzzle_id': puzzle.id, 'clue_num': 3}}
        response = self.client.post(self.target_page, data=data, content_type='application/json')
        self.assertEqual(json.loads(response.content)['err_msg'], "")
        solved_clue = SolvedClue.objects.get(session=session, clue=clues[2], solver=self.user)
        self.assertTrue(solved_clue.revealed)
        self.assertTemplateUsed("puzzle_session.html")

    def test_POST_sets_finish_timestamp_on_session_if_no_remaining_clues(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1])  # 3 clues
        clues = puzzle.get_clues()
        session = SolverSession.objects.create(puzzle=puzzle, solver=self.user)
        self.assertIsNone(session.finished_at)
        # Preset 2 of 3 clues as resolved
        SolvedClue.objects.create(clue=clues[0], solver=self.user, session=session, revealed=False)
        SolvedClue.objects.create(clue=clues[1], solver=self.user, session=session, revealed=True)
        updated_session = SolverSession.objects.get(puzzle=puzzle, solver=self.user)
        self.assertIsNone(session.finished_at)
        # Now solve last clue
        data = {'action': 'reveal', 'data': {'session_id': session.id, 'puzzle_id': puzzle.id, 'clue_num': 3}}
        response = self.client.post(self.target_page, data=data, content_type='application/json')
        # Check session is updated and finish date is set
        updated_session = SolverSession.objects.get(puzzle=puzzle, solver=self.user)
        self.assertIsNotNone(updated_session.finished_at)