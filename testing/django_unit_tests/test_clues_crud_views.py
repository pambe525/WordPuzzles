from unittest.case import skip

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase

import testing.data_setup_utils
from puzzles.models import WordPuzzle, Clue
from testing.data_setup_utils import add_clue
from testing.django_unit_tests.test_puzzle_crud_views import BaseEditPuzzleTest


class AddCluesViewTests(BaseEditPuzzleTest):
    target_page = "/add_clues/"
    redirect_page = "/edit_puzzle/"

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
        puzzle_data = {'clues': '1. first\n2. second', 'answers': '1. answer'}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", puzzle_data)
        self.assertEqual(puzzle.id, response.context['id'])
        self.assertEqual(str(puzzle), response.context['title'])
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual('Corresponding cross-entry for #2 missing.',
                         response.context['form'].errors['answers'][0])
        self.assertFalse(Clue.objects.filter(puzzle=puzzle).exists())

    def test_POST_with_valid_form_input_saves_and_redirects_to_edit_puzzle_page_(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        clues_data = {'clues': '5. fifth clue (6,5)\n2. second clue', 'answers': '5. answer fifth\n 2 answer two'}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", clues_data)
        self.assertRedirects(response, self.redirect_page + str(puzzle.id) + "/")
        saved_clues = Clue.objects.filter(puzzle=puzzle)
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        # Puzzle clue counts must be updated
        self.assertEqual(2, updated_puzzle.size)
        self.assertEqual(2, updated_puzzle.total_points)
        self.assertEqual(2, len(saved_clues))
        # first saved clue (#5) - note: answers are NOT capitalized before saving;
        # answer lengths, if specified, are preserved
        self.assertEqual(5, saved_clues[0].clue_num)
        self.assertEqual('fifth clue (6,5)', saved_clues[0].clue_text)
        self.assertEqual('answer fifth', saved_clues[0].answer)
        self.assertEqual(None, saved_clues[0].parsing)
        self.assertEqual(1, saved_clues[0].points)
        # second saved clue (#2)
        self.assertEqual(2, saved_clues[1].clue_num)
        self.assertEqual('second clue', saved_clues[1].clue_text)
        self.assertEqual('answer two', saved_clues[1].answer)
        self.assertEqual(None, saved_clues[1].parsing)
        self.assertEqual(1, saved_clues[1].points)

    def test_POST_with_repeated_answer(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        prev_form_data = {'clues': '1 first clue (5,3)\n2. clue two',
                          'answers': '1 first one\n2 repeated'}
        self.client.post(self.target_page + str(puzzle.id) + "/", prev_form_data)
        new_form_data = {'clues': '3 clue three\n4. fourth clue',
                         'answers': '3 answer three\n4.REPEATED '}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", new_form_data)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(len(response.context['form']['clues'].errors), 0)
        self.assertEqual(response.context['form']['answers'].errors[0],
                         '#4 answer is same as answer in clue #2.')

    def test_POST_with_existing_clue_nums_updates_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle_data = {'clues': '5. fifth clue \n2. second clue', 'answers': '5. answer fifth\n 2 answer two'}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", puzzle_data)
        more_puzzle_data = {'clues': '5. fifth clue mod \n6. new clue', 'answers': '6. new answer\n 5 mod answer'}
        response = self.client.post(self.target_page + str(puzzle.id) + "/", more_puzzle_data)
        saved_clues = Clue.objects.filter(puzzle=puzzle)
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        # Puzzle clue counts must be updated
        self.assertEqual(3, updated_puzzle.size)
        self.assertEqual(3, updated_puzzle.total_points)
        self.assertEqual(3, len(saved_clues))
        # first saved clue (#5)
        self.assertEqual(5, saved_clues[0].clue_num)
        self.assertEqual('fifth clue mod', saved_clues[0].clue_text)
        self.assertEqual('mod answer', saved_clues[0].answer)
        # second saved clue (#2) - unchanged
        self.assertEqual(2, saved_clues[1].clue_num)
        self.assertEqual('second clue', saved_clues[1].clue_text)
        self.assertEqual('answer two', saved_clues[1].answer)
        # second saved clue (#6) - new
        self.assertEqual(6, saved_clues[2].clue_num)
        self.assertEqual('new clue', saved_clues[2].clue_text)
        self.assertEqual('new answer', saved_clues[2].answer)


class EditClueViewTests(TransactionTestCase):
    target_page = "/edit_clue/"
    reset_sequences = True

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="test_user")[0]
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(self.target_page + "1/1/")
        self.assertEqual(302, response.status_code)
        self.assertEqual("/login?next=" + self.target_page + "1/1/", response.url)

    def test_GET_shows_error_if_user_is_not_editor_of_puzzle(self):
        other_user = User.objects.create(username="other_user", email="abc@xyz")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        clue = Clue.objects.create(puzzle=puzzle, clue_num=1)
        response = self.client.get("/edit_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Clue 1 for Puzzle " + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/edit_clue/5/1/")
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle 5")
        self.assertContains(response, "This puzzle does not exist.")

    def test_GET_raises_error_message_if_clue_does_not_exist(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/edit_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, "puzzle_error.html")
        self.assertContains(response, "Puzzle " + str(puzzle.id))
        self.assertContains(response, "This clue does not exist.")

    def test_GET_renders_template_and_clue_form(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = Clue.objects.create(puzzle=puzzle, clue_num=1, clue_text='Clue text desc', answer='test')
        response = self.client.get(self.target_page + str(puzzle.id) + '/' + str(clue.clue_num) + '/')
        self.assertEqual(puzzle.id, response.context['id'])
        self.assertEqual(1, response.context['clue_num'])
        self.assertEqual("test", response.context['form']['answer'].value())
        self.assertEqual('Clue text desc', response.context['form']['clue_text'].value(), )
        self.assertIsNone(response.context['form']['parsing'].value())
        self.assertEqual(1, response.context['form']['points'].value())

    def test_POST_form_updates_clue_and_redirects_to_edit_puzzle_view(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_data = {'clue_text': 'Clue text desc', 'answer': 'test', 'points': 1}
        clue = add_clue(puzzle, clue_data)
        mod_clue_data = {'answer': 'MOD-TEST', 'clue_text': 'Mod clue text', 'points': 2}
        response = self.client.post('/edit_clue/' + str(puzzle.id) + '/' + str(clue.clue_num) + '/', mod_clue_data)
        self.assertEqual(response.url, '/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        updated_clue = Clue.objects.get(puzzle=puzzle.id, id=clue.id)
        self.assertEqual(updated_clue.answer, 'MOD-TEST')
        self.assertEqual(updated_clue.clue_text, 'Mod clue text')
        self.assertEqual(updated_clue.points, 2)
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.total_points, 2)

    def test_POST_form_has_errors_on_incorrect_input_and_no_redirect(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_data = {'clue_text': 'Clue text', 'answer': 'test', 'points': 1}
        clue = add_clue(puzzle, clue_data)
        mod_clue_data = {'clue_text': 'Mod clue text', 'answer': 'in_correct!', 'points': 2}
        url = self.target_page + str(puzzle.id) + '/' + str(clue.clue_num) + '/'
        response = self.client.post(url, mod_clue_data)
        self.assertTemplateUsed('edit_clue.html')
        saved_clue = Clue.objects.get(puzzle=puzzle.id, id=1)
        self.assertEqual(saved_clue.answer, 'test')
        self.assertEqual(response.context['id'], puzzle.id)
        self.assertEqual(response.context['clue_num'], 1)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.context['form']['answer'].errors[0],
                         "Answer cannot contain non-alphabet characters")
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.total_points, 1)

    def test_POST_form_checks_if_edited_answer_is_repeated(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        add_clue(puzzle, {'clue_text': 'first clue', 'answer': 'ans one', 'points': 1})
        add_clue(puzzle, {'clue_text': 'second clue', 'answer': 'repeat this', 'points': 2})
        clue = add_clue(puzzle, {'clue_text': 'third clue', 'answer': 'change this', 'points': 1})
        mod_clue_data = {'clue_text': 'Mod clue text', 'answer': 'repeat this', 'points': 2}
        url = self.target_page + str(puzzle.id) + '/' + str(clue.clue_num) + '/'
        response = self.client.post(url, mod_clue_data)
        self.assertTemplateUsed('edit_clue.html')
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(response.context['form']['answer'].errors[0], "Answer is same as in clue #2.")


class DeleteClueViewTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = add_clue(puzzle, {'points': 1})
        response = self.client.get("/delete_clue/" + str(puzzle.id) + "/" + str(clue.clue_num) + '/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/delete_clue/1/1/")

    def test_POST_deletes_clue_updates_points_and_redirects_to_edit_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = add_clue(puzzle, {'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.post("/delete_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/edit_puzzle/" + str(puzzle.id) + '/')
        self.assertFalse(Clue.objects.filter(puzzle=puzzle, clue_num=clue.id).exists())
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.size, 0)
        self.assertEqual(puzzle.total_points, 0)
