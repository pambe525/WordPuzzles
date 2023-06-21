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

    # def test_EDIT_PUZZLE_shows_error_if_puzzle_is_published(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user)
    #     add_clue(puzzle, {'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
    #     self.client.get(self.target_page + str(puzzle.id) + "/")  # Publish puzzle
    #     response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "puzzle_error.html")
    #     self.assertContains(response, "Puzzle " + str(puzzle.id))
    #     self.assertContains(response, "Published puzzle cannot be edited. Unpublish to edit.")

    # def test_PREVIEW_PUZZLE_does_not_show_error_if_puzzle_is_published(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user)
    #     testing.data_setup_utils.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
    #     self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
    #     response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
    #     self.assertTemplateUsed(response, "word_puzzle.html")
    #     self.assertContains(response, "Puzzle #" + str(puzzle.id))


@skip
class UnpublishPuzzleViewTest(BaseEditPuzzleTest):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_GET_redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/unpublish_puzzle/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/unpublish_puzzle/1/")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="other_user")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/unpublish_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "OK")
        self.assertContains(response, "This operation is not permitted since you are not the editor.")

    def test_GET_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/unpublish_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_GET_sets_shared_at_field_to_None_and_redirects_to_homepage(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        testing.data_setup_utils.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
        response = self.client.get("/unpublish_puzzle/" + str(puzzle.id) + "/")  # Unublish puzzle
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)
