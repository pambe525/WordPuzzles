import json

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase

from puzzles.models import WordPuzzle
from testing.django_unit_tests.unit_test_helpers import create_published_puzzle, create_draft_puzzle


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
        puzzle = create_draft_puzzle(user=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Publish")
        self.assertEqual(response.context['object'], puzzle)
        self.assertTrue(response.context['show_answers'])

    def test_Published_puzzle_contains_correct_heading_and_puzzle_object_for_editor(self):
        puzzle = create_published_puzzle(user=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Unpublish")
        self.assertEqual(response.context['object'], puzzle)
        self.assertTrue(response.context['show_answers'])

    def test_Published_puzzle_contains_correct_heading_for_non_editor(self):
        puzzle = create_published_puzzle(user=self.other_user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['heading'], "Preview Puzzle & Solve")
        self.assertEqual(response.context['object'], puzzle)
        self.assertFalse(response.context['show_answers'])

    def test_Editor_response_context_contains_serialized_clues_list_with_answers(self):
        puzzle = create_published_puzzle(user=self.user, clues_pts=[4,2,1,4])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertTrue(response.context['show_answers'])
        self.assertEqual(len(json_clues_list), 4)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index+1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clues_list[index]['answer'], clues[index].answer)
            self.assertEqual(json_clues_list[index]['parsing'], clues[index].parsing)

    def test_Non_editor_response_context_contains_serialized_clues_list_without_answers(self):
        puzzle = create_published_puzzle(user=self.other_user, clues_pts=[4,2,1])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertFalse(response.context['show_answers'])
        self.assertEqual(len(json_clues_list), 3)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index+1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertFalse('answer' in json_clues_list[index])
            self.assertFalse('parsing' in json_clues_list[index])