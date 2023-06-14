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

    #
    # def test_GET_form_initialization_with_blank_object(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user)
    #     response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
    #     self.assertEqual(response.context['object'].id, 1)
    #     self.assertEqual(response.context['object'].editor, self.user)
    #     self.assertEqual(response.context['object'].size, 0)
    #     self.assertEqual(response.context['object'].total_points, 0)
    #     self.assertEqual(response.context['form']['type'].initial, 1)
    #     self.assertIsNone(response.context['form']['desc'].initial)
    #
    # def test_GET_with_no_clues_displayed(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user)
    #     response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
    #     self.assertEqual(len(response.context['clues']), 0)
    #     self.assertContains(response, "Clues [0 points]")
    #     self.assertContains(response, "No clues exist. Use ADD CLUE to create clues.")
    #     self.assertContains(response, "SAVE")
    #     self.assertContains(response, "DONE")
    #     self.assertContains(response, "ADD CLUE")
    #
    # def test_GET_form_with_existing_data(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions", type=0)
    #     response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
    #     self.assertEqual(response.context['form'].initial['type'], 0)
    #     self.assertEqual(response.context['form'].initial['desc'], "Instructions")
    #     self.assertFalse(response.context['saved'])
    #
    # def test_GET_displays_all_puzzle_clues(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user)
    #     clue1_data = {'answer': "FIRST WORD", 'clue_text': 'Clue for first word', 'parsing': 'DEF1', 'points': 1}
    #     clue2_data = {'answer': "SECOND WORD", 'clue_text': 'Clue for 2nd word', 'parsing': 'DEF2', 'points': 2}
    #     puzzle.add_clue(clue1_data)
    #     puzzle.add_clue(clue2_data)
    #     response = self.client.get('/edit_puzzle/' + str(puzzle.id) + '/')
    #     self.assertEqual(response.context['object'].total_points, 3)
    #     self.assertEqual(response.context['object'].size, 2)
    #     self.assertContains(response, "Clues [3 points]")
    #     self.assertEqual(len(response.context['clues']), 2)
    #     self.assertEqual(response.context['clues'][0].clue_num, 1)
    #     self.assertEqual(response.context['clues'][0].clue_text, 'Clue for first word')
    #     self.assertEqual(response.context['clues'][0].parsing, 'DEF1')
    #     self.assertEqual(response.context['clues'][0].points, 1)
    #

    #
    # def test_POST_save_shows_all_puzzle_clues(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user)
    #     puzzle_data = {'type': 1, 'desc': 'Puzzle instructions'}
    #     clue1_data = {'answer': "FIRST", 'clue_text': 'Clue for word', 'parsing': 'DEF1', 'points': 2}
    #     clue2_data = {'answer': "SECOND", 'clue_text': 'Clue for 2nd word', 'parsing': 'DEF2', 'points': 3}
    #     puzzle.add_clue(clue1_data)
    #     puzzle.add_clue(clue2_data)
    #     response = self.client.post('/edit_puzzle/' + str(puzzle.id) + '/', puzzle_data)
    #     self.assertEqual(response.context['object'].total_points, 5)
    #     self.assertEqual(response.context['object'].size, 2)
    #     self.assertEqual(len(response.context['clues']), 2)
    #     self.assertEqual(response.context['clues'][0].clue_num, 1)
    #     self.assertEqual(response.context['clues'][0].clue_text, 'Clue for word')
    #     self.assertEqual(response.context['clues'][0].parsing, 'DEF1')
    #     self.assertEqual(response.context['clues'][0].points, 2)


class AddCluesViewTests(BaseEditPuzzleTest):
    target_page = "/add_clues/"

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        self.unauthenticated_user_test()

    def test_GET_shows_error_if_user_is_not_editor(self):
        self.user_is_not_editor_test()

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        self.puzzle_does_not_exist_test()

    def test_response_context(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        response = self.client.get(self.target_page + str(puzzle.id) + "/")
        self.assertTemplateUsed("add_clues.html")
        self.assertEqual(response.context['id'], puzzle.id)
        self.assertEqual(response.context['title'], str(puzzle))
        self.assertIn('AddCluesForm', str(response.context['form']))
