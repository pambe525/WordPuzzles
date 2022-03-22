import json

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase

from puzzles.models import WordPuzzle
from testing.django_unit_tests.unit_test_helpers import create_published_puzzle

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
        puzzle = WordPuzzle.objects.create(editor=self.other_user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "OK")
        self.assertContains(response, "This operation is not permitted since you are not the editor.")

    def test_Shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/preview_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_Response_context_contains_heading_and_puzzle_object(self):
        puzzle = create_published_puzzle(user=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['heading'], "Preview Puzzle")
        self.assertEqual(response.context['object'], puzzle)

    def test_Response_context_contains_serialized_clues_list(self):
        puzzle = create_published_puzzle(user=self.user, clues_pts=[4,2,1,4])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertEqual(len(json_clues_list), 4)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index+1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clues_list[index]['answer'], clues[index].answer)
            self.assertEqual(json_clues_list[index]['parsing'], clues[index].parsing)
