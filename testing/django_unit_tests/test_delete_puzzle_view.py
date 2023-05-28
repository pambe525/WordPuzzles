from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TransactionTestCase
from puzzles.models import WordPuzzle


class DeletePuzzleViewTests(TransactionTestCase):
    reset_sequences = True
    target_page = "/delete_puzzle/"

    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get(self.target_page + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/delete_puzzle/1/")

    def test_GET_returns_delete_confirmation_options(self):
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get(self.target_page + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "delete_confirm.html")
        self.assertContains(response, "Delete Puzzle 1")
        self.assertContains(response, "This puzzle and all associated clues will be permanently")
        self.assertContains(response, "Delete")
        self.assertContains(response, "Cancel")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="other_user", email="abc@cde.com")
        new_puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get(self.target_page + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle 1")
        self.assertContains(response, "This operation is not permitted")
        self.assertContains(response, "Ok")

    def test_GET_shows_error_if_puzzle_id_does_not_exist(self):
        response = self.client.get(self.target_page+"1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle 1")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "Ok")

    def test_POST_deletes_puzzle_and_redirects_to_my_puzzles(self):
        WordPuzzle.objects.create(editor=self.user)
        response = self.client.post(self.target_page+"1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/my_puzzles")
        self.assertFalse(WordPuzzle.objects.filter(id=1).exists())

