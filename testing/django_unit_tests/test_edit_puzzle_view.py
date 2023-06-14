from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TransactionTestCase

from puzzles.models import WordPuzzle


class BaseEditPuzzleTest(TransactionTestCase):
    reset_sequences = True
    target_page = None

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="test_user")[0]
        self.client.force_login(self.user)

    def unauthenticated_user_test(self):
        logout(self.client)
        response = self.client.get(self.target_page + "1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=" + self.target_page + "1/")

    def user_is_not_editor_test(self):
        other_user = User.objects.create(username="other_user", email="abc@cde.com")
        new_puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get(self.target_page + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle 1")
        self.assertContains(response, "This operation is not permitted")
        self.assertContains(response, "Ok")

    def puzzle_does_not_exist_test(self):
        response = self.client.get(self.target_page + "3/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle 3")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "Ok")


class NewPuzzleViewTests(BaseEditPuzzleTest):
    target_page = "/new_puzzle"

    def test_POST_creates_new_puzzle_and_redirects_to_edit_puzzle_page(self):
        puzzle_data = {'type': 0, 'desc': 'new description'}
        self.assertEqual(0, len(WordPuzzle.objects.all()))
        response = self.client.post(self.target_page, puzzle_data)
        created_puzzle = WordPuzzle.objects.all()[0]
        self.assertEqual(self.user, created_puzzle.editor)
        self.assertEqual(0, created_puzzle.type)
        self.assertEqual(puzzle_data['desc'], created_puzzle.desc)
        self.assertRedirects(response, "/edit_puzzle/" + str(created_puzzle.id) + "/")


class DeletePuzzleViewTests(BaseEditPuzzleTest):
    target_page = "/delete_puzzle/"

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        self.unauthenticated_user_test()

    def test_GET_shows_error_if_user_is_not_editor(self):
        self.user_is_not_editor_test()

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        self.puzzle_does_not_exist_test()

    def test_GET_redirects_to_confirm_page(self):
        new_puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        response = self.client.get(self.target_page + str(new_puzzle.id) + "/")
        self.assertTemplateUsed(response, "delete_confirm.html")
        self.assertEqual(200, response.status_code)
        self.assertTrue(WordPuzzle.objects.filter(id=new_puzzle.id).exists())  # NOT deleted

    def test_POST_deletes_puzzle_and_redirects_to_my_puzzles_page(self):
        new_puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        response = self.client.post(self.target_page + str(new_puzzle.id) + "/")
        self.assertFalse(WordPuzzle.objects.filter(id=new_puzzle.id).exists())  # Deleted
        self.assertRedirects(response, "/my_puzzles")


class EditPuzzleViewTests(BaseEditPuzzleTest):
    target_page = "/edit_puzzle/"

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        self.unauthenticated_user_test()

    def test_GET_shows_error_if_user_is_not_editor(self):
        self.user_is_not_editor_test()

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        self.puzzle_does_not_exist_test()

    def test_POST_saves_desc_field(self):
        before_save_puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.assertIsNone(before_save_puzzle.desc)
        puzzle_data = {'desc': 'Puzzle instructions'}
        response = self.client.post(self.target_page + str(before_save_puzzle.id) + '/', puzzle_data)
        after_save_puzzle = WordPuzzle.objects.get(id=before_save_puzzle.id)
        self.assertEqual(0, after_save_puzzle.type)
        self.assertEqual(puzzle_data['desc'], after_save_puzzle.desc)
        self.assertEqual(puzzle_data['desc'], response.context['form']['desc'].value())
        self.assertEqual(response.context['object'], after_save_puzzle)

    def test_GET_response_with_form_data_and_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Some text here")
        response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(puzzle.desc, response.context['form'].initial['desc'])
        self.assertEqual(0, response.context['object'].total_points)
        self.assertEqual(0, response.context['object'].size)
        self.assertEqual(0, len(response.context['clues']))
        self.assertFalse(response.context['has_gaps'])
        self.assertEqual(200, response.status_code)

    def test_GET_response_with_existing_clues_sorted_by_clue_number(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clues_data = [{'clue_num': 3, 'clue_text': 'Third clue', 'answer': 'answer three'},
                      {'clue_num': 1, 'clue_text': 'First clue', 'answer': 'answer one'},
                      {'clue_num': 2, 'clue_text': 'Second clue', 'answer': 'answer two'}]
        puzzle.add_clues(clues_data)
        response = self.client.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assertEqual(3, response.context['object'].total_points)
        self.assertEqual(3, response.context['object'].size)
        self.assertEqual(len(response.context['clues']), 3)
        self.assertFalse(response.context['has_gaps'])
        # First sorted clue in response list is the 2nd in clues_data
        self.assertEqual(puzzle, response.context['clues'][0].puzzle)
        self.assertEqual(clues_data[1]['clue_num'], response.context['clues'][0].clue_num)
        self.assertEqual(clues_data[1]['clue_text'], response.context['clues'][0].clue_text)
        self.assertEqual(clues_data[1]['answer'], response.context['clues'][0].answer)
        self.assertEqual(None, response.context['clues'][0].parsing)
        self.assertEqual(1, response.context['clues'][0].points)
        # Second sorted clue in response list is the 3rd in clues_data
        self.assertEqual(puzzle, response.context['clues'][1].puzzle)
        self.assertEqual(clues_data[2]['clue_num'], response.context['clues'][1].clue_num)
        self.assertEqual(clues_data[2]['clue_text'], response.context['clues'][1].clue_text)
        self.assertEqual(clues_data[2]['answer'], response.context['clues'][1].answer)
        self.assertEqual(None, response.context['clues'][1].parsing)
        self.assertEqual(1, response.context['clues'][1].points)
        # Third sorted clue in response list is the 1st in clues_data
        self.assertEqual(puzzle, response.context['clues'][0].puzzle)
        self.assertEqual(clues_data[0]['clue_num'], response.context['clues'][2].clue_num)
        self.assertEqual(clues_data[0]['clue_text'], response.context['clues'][2].clue_text)
        self.assertEqual(clues_data[0]['answer'], response.context['clues'][2].answer)
        self.assertEqual(None, response.context['clues'][2].parsing)
        self.assertEqual(1, response.context['clues'][2].points)

    def test_GET_response_with_numbering_gaps_in_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clues_data = [{'clue_num': 3, 'clue_text': 'Third clue', 'answer': 'answer three'},
                      {'clue_num': 4, 'clue_text': 'Fourth clue', 'answer': 'answer four'},
                      {'clue_num': 2, 'clue_text': 'Second clue', 'answer': 'answer two'}]
        puzzle.add_clues(clues_data)
        response = self.client.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assertEqual(len(response.context['clues']), 3)
        self.assertTrue(response.context['has_gaps'])


class AddCluesViewTests(BaseEditPuzzleTest):
    target_page = "/add_clues/"

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        self.unauthenticated_user_test()

    def test_GET_shows_error_if_user_is_not_editor(self):
        self.user_is_not_editor_test()

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        self.puzzle_does_not_exist_test()

    def test_GET_response_context(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertTemplateUsed("add_clues.html")
        self.assertEqual(response.context['id'], puzzle.id)
        self.assertEqual(response.context['title'], str(puzzle))
        self.assertIn('clues', response.context['form'].base_fields)
        self.assertIn('answers', response.context['form'].base_fields)

    def test_POST_response_with_invalid_form_input(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle_data = {'clues': '1. first\n2. secomd', 'answers': '1. answer'}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", puzzle_data)
        self.assertEqual(puzzle.id, response.context['id'])
        self.assertEqual(str(puzzle), response.context['title'])
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual('Corresponding cross-entry for #2 missing.', response.context['form'].errors['answers'][0])

    def test_POST_redirects_to_edit_puzzle_page_with_valid_form_input(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle_data = {'clues': '1. first\n2. secomd', 'answers': '1. answer one\n2. answer two'}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", puzzle_data)
        self.assertRedirects(response, "/edit_puzzle/" + str(puzzle.id) + "/")
