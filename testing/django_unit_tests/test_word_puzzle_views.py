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

    def test_Shows_error_if_user_is_not_editor_for_unpublished_puzzle(self):
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
        self.assertEqual(response.context['heading'], "Preview & Publish Puzzle")
        self.assertEqual(response.context['object'], puzzle)

    def test_Response_context_contains_serialized_clues_list_and_show_answers_is_true(self):
        puzzle = create_published_puzzle(user=self.user, clues_pts=[4,2,1,4])
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['show_answers'], True)
        clues = puzzle.get_clues()
        json_clues_list = json.loads(response.context['clues'])
        self.assertEqual(len(json_clues_list), 4)
        for index in range(0, len(json_clues_list)):
            self.assertEqual(json_clues_list[index]['clue_num'], index+1)
            self.assertEqual(json_clues_list[index]['points'], clues[index].points)
            self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())
            self.assertEqual(json_clues_list[index]['answer'], clues[index].answer)
            self.assertEqual(json_clues_list[index]['parsing'], clues[index].parsing)

    # def test_Displays_puzzle_details(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user, desc='Description')
    #     puzzle.add_clue({'answer': 'WORD-A', 'clue_text': 'Clue 1 for word A', 'parsing': 'parsing', 'points': 1})
    #     puzzle.add_clue({'answer': 'WORD-B', 'clue_text': 'Clue 2 for word B', 'parsing': '', 'points': 2})
    #     puzzle.add_clue({'answer': 'WORD-C', 'clue_text': 'Clue 3 for word C', 'parsing': '', 'points': 3})
    #     puzzle.add_clue({'answer': 'WORD-D', 'clue_text': 'Clue 4 for word D', 'parsing': 'parsing for D', 'points': 4})
    #     response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
    #     self.assertContains(response, "Puzzle #" + str(puzzle.id))
    #     self.assertContains(response, "DONE")
    #     self.assertContains(response, str(puzzle))
    #     self.assertContains(response, puzzle.desc)
    #     self.assertContains(response, "Clues")


# class WordPuzzleViewTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create(username="test_user")
#         self.other_user = User.objects.create(username="other_user")
#         self.client.force_login(self.user)
#
#     def test_Response_context_contains_puzzle_object(self):
#         puzzle = create_published_puzzle(user=self.other_user)
#         response = self.client.get("/word_puzzle/" + str(puzzle.id) + "/")
#         self.assertEqual(response.context['object'], puzzle)
#
#     def test_Response_context_contains_serialized_clues_list(self):
#         puzzle = create_published_puzzle(user=self.other_user, clues_pts=[4,2,1,4])
#         response = self.client.get("/solve_puzzle/" + str(puzzle.id) + "/")
#         clues = puzzle.get_clues()
#         json_clues_list = json.loads(response.context['clues'])
#         self.assertEqual(len(json_clues_list), 4)
#         for index in range(0, len(json_clues_list)):
#             self.assertEqual(json_clues_list[index]['clue_num'], index+1)
#             self.assertEqual(json_clues_list[index]['points'], clues[index].points)
#             self.assertEqual(json_clues_list[index]['clue_text'], clues[index].get_decorated_clue_text())