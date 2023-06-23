from unittest import skip

from django.contrib.auth.models import User

from puzzles.models import WordPuzzle
from testing.data_setup_utils import add_clue
from testing.django_unit_tests.test_puzzle_crud_views import BaseEditPuzzleTest


class PublishPuzzleViewTest(BaseEditPuzzleTest):
    target_page = "/publish_puzzle/"

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_POST_shows_error_if_puzzle_has_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.post(self.target_page + str(puzzle.id) + "/")  # Publish puzzle
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, "No clues to publish.  Add clues before publishing.")

    def test_POST_sets_shared_at_field_to_now_and_redirects_to_puzzles_list(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        add_clue(puzzle, {'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.assertIsNone(puzzle.shared_at)
        response = self.client.post(self.target_page + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNotNone(updated_puzzle.shared_at)

    def test_POST_does_nothing_if_shared_at_is_already_set(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        add_clue(puzzle, {'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.client.post(self.target_page + str(puzzle.id) + "/")  # Publish puzzle
        shared_at = WordPuzzle.objects.get(id=puzzle.id).shared_at
        response = self.client.post("/publish_puzzle/" + str(puzzle.id) + "/")  # do it again
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(shared_at, updated_puzzle.shared_at)


class UnpublishPuzzleViewTest(BaseEditPuzzleTest):
    target_page = "/unpublish_puzzle/"

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_POST_sets_shared_at_field_to_None_and_redirects_to_homepage(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        add_clue(puzzle, {'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        puzzle.publish()
        response = self.client.post(self.target_page + str(puzzle.id) + "/")  # Unpublish puzzle
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)
