import json

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase

from puzzles.models import WordPuzzle
from testing.django_unit_tests.unit_test_helpers import create_published_puzzle, create_draft_puzzle, create_session


class PreviewPuzzleViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester", password="scretkey")
        self.other_user = User.objects.create(username="other_user", password="secretkey2")
        self.client.force_login(self.user)

    def test_Redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/preview_puzzle/1/")

    def test_Shows_error_if_user_is_not_editor_for_draft_puzzle(self):
        puzzle = create_draft_puzzle(self.other_user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_Shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/preview_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_Draft_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
        puzzle = create_draft_puzzle(editor=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Publish")
        self.assertEqual(response.context['object'], puzzle)

    def test_Published_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
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

    def test_Editor_response_context_contains_serialized_clues_list_with_answers(self):
        puzzle = create_published_puzzle(editor=self.user, clues_pts=[4, 2, 1, 4])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertEqual(len(json_clues_list), 4)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index + 1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clues_list[index]['answer_footprint'], '4-1')
            self.assertEqual(json_clues_list[index]['answer'], clues[index].answer)
            self.assertEqual(json_clues_list[index]['parsing'], clues[index].parsing)

    def test_Non_editor_response_context_contains_serialized_clues_list_without_answers(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[4, 2, 1])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertEqual(len(json_clues_list), 3)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index + 1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['answer_footprint'], '4-1')
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertFalse('answer' in json_clues_list[index])
            self.assertFalse('parsing' in json_clues_list[index])

    def test_Redirects_to_solve_puzzle_url_if_puzzle_has_active_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[4, 2, 1])
        create_session(puzzle=puzzle, solver=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertRedirects(response, "/solve_puzzle/" + str(puzzle.id) + "/", 302)


class SolvePuzzleViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester", password="scretkey")
        self.other_user = User.objects.create(username="other_user", password="secretkey2")
        self.client.force_login(self.user)

    def test_Redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/solve_puzzle/1/")

    def test_Shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/solve_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_Shows_error_for_editor_of_draft_puzzle(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[2, 4, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This puzzle is not published.")
        self.assertContains(response, "OK")

    def test_Shows_error_for_non_editor_accessing_a_draft_puzzle(self):
        puzzle = create_draft_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_Redirects_to_preview_when_editor_accesses_a_published_puzzle(self):
        puzzle = create_published_puzzle(editor=self.user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertEquals(response.status_code, 302)
        self.assertTemplateUsed("word_puzzle.html")

    def test_Creates_new_session_and_renders_solve_puzzle_page(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        self.assertTemplateUsed("word_puzzle.html")
        self.assertEqual(response.context['heading'], "Solve Puzzle")
        self.assertEqual(response.context['object'], puzzle)
        self.assertIsNotNone(response.context['active_session'])
        json_session = json.loads(response.context['active_session'])
        self.assertEqual(json_session['puzzle_id'], puzzle.id)
        self.assertEqual(json_session['solver_id'], self.user.id)
        self.assertEqual(json_session['elapsed_secs'], 0)
        self.assertEqual(json_session['solved_clues'], [])
        self.assertEqual(json_session['revealed_clues'], [])
        self.assertEqual(json_session['score'], 0)

    def test_Loads_existing_session_and_renders_solve_puzzle_page(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 4, 5])
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        json_session = json.loads(response.context['active_session'])
        self.assertEqual(json_session['puzzle_id'], puzzle.id)
        self.assertEqual(json_session['solver_id'], self.user.id)
        self.assertEqual(json_session['elapsed_secs'], 0)
        self.assertEqual(json_session['solved_clues'], [1, 5])
        self.assertEqual(json_session['revealed_clues'], [2, 3])
        self.assertEqual(json_session['score'], 7)

    def test_With_existing_session_response_contains_clue_details(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 1, 5], has_parsing=True)
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        json_clues = json.loads(response.context['clues'])
        self.assertEqual(json_clues[0]['clue_num'], 1)
        self.assertEqual(json_clues[0]['clue_text'], "Clue for WordA (4-1)")
        self.assertEqual(json_clues[0]['points'], 2)
        self.assertEqual(json_clues[0]['answer_footprint'], '4-1')
        self.assertEqual(json_clues[0]['parsing'], "Parsing for wordA")
        self.assertEqual(json_clues[0]['answer'], 'WORD-A')

    def test_With_existing_session_response_contains_answers_for_solved_and_revealed_clues(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3, 1, 1, 5])
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1,5', revealed_clues='2,3')
        response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
        json_clues = json.loads(response.context['clues'])
        self.assertTrue('answer' in json_clues[0])
        self.assertTrue('answer' in json_clues[1])
        self.assertTrue('answer' in json_clues[2])
        self.assertTrue('answer' in json_clues[4])
        self.assertFalse('answer' in json_clues[3])   # Unsolved clue does not include answer
        self.assertTrue('parsing' in json_clues[0])
        self.assertFalse('parsing' in json_clues[3])
