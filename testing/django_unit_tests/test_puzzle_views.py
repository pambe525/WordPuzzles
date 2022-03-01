from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from puzzles.models import WordPuzzle, Clue


class NewPuzzleViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.client.force_login(self.user)

    def test_NEW_PUZZLE_get_redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_puzzle"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/new_puzzle")

    def test_NEW_PUZZLE_get_creates_puzzle_and_redirects_to_EDIT_PUZZLE_view_with_id(self):
        self.assertEqual(len(WordPuzzle.objects.all()), 0)
        response = self.client.get(reverse("new_puzzle"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/edit_puzzle/1/")
        self.assertEqual(len(WordPuzzle.objects.all()), 1)


class DeletePuzzleViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.client.force_login(self.user)

    def test_DELETE_PUZZLE_CONFIRM_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/delete_puzzle_confirm/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/delete_puzzle_confirm/1/")

    def test_DELETE_PUZZLE_CONFIRM_get_returns_delete_confirmation_options(self):
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/delete_puzzle_confirm/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "delete_puzzle.html")
        self.assertContains(response, "Delete Puzzle #1")
        self.assertContains(response, "This puzzle and all associated clues will be permanently")
        self.assertContains(response, "DELETE")
        self.assertContains(response, "CANCEL")

    def test_DELETE_PUZZLE_get_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="otheruser")
        new_puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/delete_puzzle/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Puzzle #1")
        self.assertContains(response, "You cannot delete this puzzle")
        self.assertContains(response, "OK")

    def test_DELETE_PUZZLE_get_shows_error_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/delete_puzzle/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Puzzle #1")
        self.assertContains(response, "Puzzle #1 does not exist.")
        self.assertContains(response, "OK")

    def test_DELETE_PUZZLE_deletes_puzzle_and_redirects_to_home(self):
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/delete_puzzle/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        self.assertFalse(WordPuzzle.objects.filter(id=1).exists())


class EditPuzzleViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/edit_puzzle/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/edit_puzzle/1/")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="otheruser")
        new_puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/edit_puzzle/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Puzzle #1")
        self.assertContains(response, "You cannot edit this puzzle")
        self.assertContains(response, "OK")
        self.assertNotContains(response, "SAVE")
        self.assertNotContains(response, "DONE")

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/edit_puzzle/3/")
        self.assertContains(response, "Edit Puzzle #3")
        self.assertContains(response, "Puzzle #3 does not exist.")
        self.assertContains(response, "OK")
        self.assertNotContains(response, "SAVE")
        self.assertNotContains(response, "DONE")

    def test_GET_renders_template_and_form(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions", size=0)
        response = self.client.get('/edit_puzzle/1/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Puzzle #1")
        self.assertEqual(response.context['form'].initial['type'], 1)
        self.assertEqual(response.context['form'].initial['desc'], "Instructions")
        self.assertFalse(response.context['saved'])
        self.assertContains(response, "SAVE")
        self.assertContains(response, "DONE")
        self.assertContains(response, "ADD CLUE")
        self.assertContains(response, "Clues [0 points]")

    def test_POST_saves_puzzle_data(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle_data = {'type': 1, 'desc': 'Puzzle instructions'}
        response = self.client.post('/edit_puzzle/' + str(puzzle.id) + '/', puzzle_data)
        self.assertEqual(response.context['form']['type'].value(), '1')
        self.assertEqual(response.context['form']['desc'].value(), "Puzzle instructions")
        self.assertTrue(response.context['saved'])

    def test_GET_shows_all_puzzle_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue1_data = {'answer': "FIRST WORD", 'clue_text': 'Clue for first word', 'parsing': 'DEF1', 'points': 1}
        clue2_data = {'answer': "SECOND WORD", 'clue_text': 'Clue for 2nd word', 'parsing': 'DEF2', 'points': 2}
        puzzle.add_clue(clue1_data)
        puzzle.add_clue(clue2_data)
        response = self.client.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assertEqual(response.context['total_points'], 3)
        self.assertEqual(len(response.context['clues']), 2)
        self.assertEqual(response.context['clues'][0].clue_num, 1)
        self.assertEqual(response.context['clues'][0].clue_text, 'Clue for first word')
        self.assertEqual(response.context['clues'][0].parsing, 'DEF1')
        self.assertEqual(response.context['clues'][0].points, 1)

    def test_POST_save_shows_all_puzzle_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle_data = {'type': 1, 'desc': 'Puzzle instructions'}
        clue1_data = {'answer': "FIRST", 'clue_text': 'Clue for word', 'parsing': 'DEF1', 'points': 2}
        clue2_data = {'answer': "SECOND", 'clue_text': 'Clue for 2nd word', 'parsing': 'DEF2', 'points': 3}
        puzzle.add_clue(clue1_data)
        puzzle.add_clue(clue2_data)
        response = self.client.post('/edit_puzzle/' + str(puzzle.id) + '/', puzzle_data)
        self.assertEqual(response.context['total_points'], 5)
        self.assertEqual(len(response.context['clues']), 2)
        self.assertEqual(response.context['clues'][0].clue_num, 1)
        self.assertEqual(response.context['clues'][0].clue_text, 'Clue for word')
        self.assertEqual(response.context['clues'][0].parsing, 'DEF1')
        self.assertEqual(response.context['clues'][0].points, 2)


class EditClueViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/new_clue/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/new_clue/1/")
        response = self.client.get("/edit_clue/1/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/edit_clue/1/1/")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="otheruser")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/new_clue/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assertContains(response, "You cannot edit this puzzle")
        self.assertContains(response, "OK")
        self.assertNotContains(response, "SAVE")
        self.assertNotContains(response, "CANCEL")

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/new_clue/5/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Edit Clue 1 for Puzzle #5")
        self.assertContains(response, "Puzzle #5 does not exist.")
        self.assertContains(response, "OK")
        self.assertNotContains(response, "SAVE")
        self.assertNotContains(response, "CANCEL")

    def test_GET_new_clue_renders_template_and_clue_edit_form(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        response = self.client.get('/new_clue/' + str(puzzle.id) + '/')
        self.assertContains(response, "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assertEqual(response.context['form']['answer'].value(), None)
        self.assertEqual(response.context['form']['clue_text'].value(), None)
        self.assertEqual(response.context['form']['parsing'].value(), None)
        self.assertEqual(response.context['form']['points'].value(), 1)
        self.assertContains(response, "SAVE")
        self.assertContains(response, "CANCEL")

    def test_GET_existing_clue_renders_template_and_clue_edit_form(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue = puzzle.add_clue({'answer': 'TEST', 'clue_text': 'Clue text desc', 'parsing': 'easy', 'points': 1})
        response = self.client.get('/edit_clue/' + str(puzzle.id) + '/' + str(clue.clue_num) + '/')
        self.assertContains(response, "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assertEqual(response.context['form']['answer'].value(), 'TEST')
        self.assertEqual(response.context['form']['clue_text'].value(), 'Clue text desc')
        self.assertEqual(response.context['form']['parsing'].value(), 'easy')
        self.assertEqual(response.context['form']['points'].value(), 1)
        self.assertContains(response, "SAVE")
        self.assertContains(response, "CANCEL")

    def test_POST_new_clue_form_creates_new_clue_and_redirects_to_edit_puzzle_view(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_form_data = {'answer': "MY WORD", 'clue_text': 'clue to my word', 'parsing': '', 'points': 2}
        response = self.client.post('/edit_clue/' + str(puzzle.id) + '/1/', clue_form_data)
        self.assertEqual(response.url, '/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(updated_puzzle.size, 1)
        self.assertEqual(updated_puzzle.total_points, 2)

    def test_POST_new_clue_form_does_not_save_form_if_errors(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_form_data = {'answer': "word", 'clue_text': '', 'parsing': '', 'points': 2}
        response = self.client.post('/edit_clue/' + str(puzzle.id) + '/1/', clue_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_clue.html")
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 0)

    def test_POST_existing_clue_form_updates_clue_and_redirects_to_edit_puzzle_view(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_data = {'answer': 'TEST', 'clue_text': 'Clue text desc', 'parsing': 'easy', 'points': 1}
        clue = puzzle.add_clue(clue_data)
        mod_clue_data = {'answer': 'MOD-TEST', 'clue_text': 'Clue text', 'parsing': 'not easy', 'points': 2}
        response = self.client.post('/edit_clue/' + str(puzzle.id) + '/' + str(clue.clue_num) + '/', mod_clue_data)
        self.assertEqual(response.url, '/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        updated_clue = Clue.objects.get(puzzle=puzzle.id, id=clue.id)
        self.assertEqual(updated_clue.answer, 'MOD-TEST')
        self.assertEqual(updated_clue.clue_text, 'Clue text')
        self.assertEqual(updated_clue.parsing, 'not easy')
        self.assertEqual(updated_clue.points, 2)
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.total_points, 2)


class DeleteClueViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.client.force_login(self.user)

    def test_DELETE_CLUE_CONFIRM_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'points': 1})
        response = self.client.get("/delete_clue_confirm/" + str(puzzle.id) + "/" + str(clue.clue_num) + '/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/delete_clue_confirm/1/1/")

    def test_DELETE_CLUE_CONFIRM_get_returns_delete_confirmation_options(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.get("/delete_clue_confirm/" + str(puzzle.id) + '/' + str(clue.clue_num) + '/')
        # self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "delete_clue.html")
        self.assertContains(response, "Delete Clue 1 of Puzzle #1")
        self.assertContains(response, "This clue will be permanently deleted")
        self.assertContains(response, "DELETE")
        self.assertContains(response, "CANCEL")

    def test_DELETE_CLUE_get_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="otheruser")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        clue = puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.get("/delete_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Clue 1 of Puzzle #1")
        self.assertContains(response, "You cannot delete this clue")
        self.assertContains(response, "OK")

    def test_DELETE_CLUE_get_shows_error_if_puzzle_or_clue_does_not_exist(self):
        response = self.client.get("/delete_clue/1/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Clue 1 of Puzzle #1")
        self.assertContains(response, "This clue does not exist.")
        self.assertContains(response, "OK")

    def test_DELETE_CLUE_deletes_clue_updates_points_and_redirects_to_edit_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.get("/delete_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/edit_puzzle/" + str(puzzle.id) + '/')
        self.assertFalse(Clue.objects.filter(puzzle=puzzle, clue_num=1).exists())
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.size, 0)
        self.assertEqual(puzzle.total_points, 0)

    def test_DELETE_CLUE_renumbers_clues_to_eliminate_gaps(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue1 = puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': '', 'points': 1})
        clue2 = puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue 2', 'parsing': '', 'points': 2})
        clue3 = puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue 3', 'parsing': '', 'points': 3})
        clue4 = puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue 4', 'parsing': '', 'points': 4})
        response = self.client.get("/delete_clue/" + str(puzzle.id) + "/2/")
        clues = Clue.objects.filter(puzzle=puzzle)
        self.assertEqual(len(clues), 3)
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.size, 3)
        self.assertEqual(puzzle.total_points, 8)
        self.assertEqual(clues[0].clue_num, 1)
        self.assertEqual(clues[1].clue_num, 2)
        self.assertEqual(clues[2].clue_num, 3)

class PreviewPuzzleViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="tester")
        self.client.force_login(self.user)

    def test_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/preview_puzzle/1/")

    def test_get_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="otheruser")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preview for Puzzle #" + str(puzzle.id))
        self.assertContains(response, "OK")
        self.assertNotContains(response, "DONE")
        self.assertContains(response, "You cannot preview this puzzle")

    def test_get_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/preview_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Preview for Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")
        self.assertNotContains(response, "DONE")

    def test_get_displays_puzzle_details(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc='Description')
        clue1 = puzzle.add_clue({'answer': 'WORD-A', 'clue_text': 'Clue 1 for word A', 'parsing': 'this is a parsing', 'points': 1})
        clue2 = puzzle.add_clue({'answer': 'WORD-B', 'clue_text': 'Clue 2 for word B', 'parsing': '', 'points': 2})
        clue3 = puzzle.add_clue({'answer': 'WORD-C', 'clue_text': 'Clue 3 for word C', 'parsing': '', 'points': 3})
        clue4 = puzzle.add_clue({'answer': 'WORD-D', 'clue_text': 'Clue 4 for word D', 'parsing': 'parsin for D', 'points': 4})
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertContains(response, "Preview for Puzzle #" + str(puzzle.id))
        self.assertContains(response, "DONE")
        self.assertContains(response, str(puzzle))
        self.assertContains(response, puzzle.desc)
        self.assertContains(response, "Clues")


