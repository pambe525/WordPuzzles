from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase

from puzzles.models import WordPuzzle, Clue


class NewPuzzleViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_GET_redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/new_puzzle")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/new_puzzle")

    def test_GET_creates_new_puzzle(self):
        self.assertEqual(len(WordPuzzle.objects.all()), 0)
        self.client.get("/new_puzzle")
        self.assertEqual(len(WordPuzzle.objects.all()), 1)

    def test_GET_redirects_to_EDIT_PUZZLE(self):
        response = self.client.get("/new_puzzle")
        new_puzzle = WordPuzzle.objects.all()[0]
        self.assertEqual(new_puzzle.editor, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/edit_puzzle/" + str(new_puzzle.id) + "/")


class EditPuzzleViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="test_user")[0]
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/edit_puzzle/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/edit_puzzle/1/")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="other_user")
        new_puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/edit_puzzle/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #1")
        self.assertContains(response, "This operation is not permitted")
        self.assertContains(response, "OK")

    def test_GET_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/edit_puzzle/3/")
        self.assertContains(response, "Puzzle #3")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")
        self.assertNotContains(response, "SAVE")
        self.assertNotContains(response, "DONE")

    def test_GET_form_initialization_with_blank_object(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['object'].id, 1)
        self.assertEqual(response.context['object'].editor, self.user)
        self.assertEqual(response.context['object'].size, 0)
        self.assertEqual(response.context['object'].total_points, 0)
        self.assertEqual(response.context['form']['type'].initial, 1)
        self.assertIsNone(response.context['form']['desc'].initial)

    def test_GET_with_no_clues_displayed(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(len(response.context['clues']), 0)
        self.assertContains(response, "Clues [0 points]")
        self.assertContains(response, "No clues exist. Use ADD CLUE to create clues.")
        self.assertContains(response, "SAVE")
        self.assertContains(response, "DONE")
        self.assertContains(response, "ADD CLUE")

    def test_GET_form_with_existing_data(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions", type=0)
        response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.context['form'].initial['type'], 0)
        self.assertEqual(response.context['form'].initial['desc'], "Instructions")
        self.assertFalse(response.context['saved'])

    def test_GET_displays_all_puzzle_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue1_data = {'answer': "FIRST WORD", 'clue_text': 'Clue for first word', 'parsing': 'DEF1', 'points': 1}
        clue2_data = {'answer': "SECOND WORD", 'clue_text': 'Clue for 2nd word', 'parsing': 'DEF2', 'points': 2}
        puzzle.add_clue(clue1_data)
        puzzle.add_clue(clue2_data)
        response = self.client.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assertEqual(response.context['object'].total_points, 3)
        self.assertEqual(response.context['object'].size, 2)
        self.assertContains(response, "Clues [3 points]")
        self.assertEqual(len(response.context['clues']), 2)
        self.assertEqual(response.context['clues'][0].clue_num, 1)
        self.assertEqual(response.context['clues'][0].clue_text, 'Clue for first word')
        self.assertEqual(response.context['clues'][0].parsing, 'DEF1')
        self.assertEqual(response.context['clues'][0].points, 1)

    def test_POST_saves_puzzle_data(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle_data = {'type': 1, 'desc': 'Puzzle instructions'}
        response = self.client.post('/edit_puzzle/' + str(puzzle.id) + '/', puzzle_data)
        saved_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(saved_puzzle.type, puzzle_data['type'])
        self.assertEqual(saved_puzzle.desc, puzzle_data['desc'])
        self.assertEqual(response.context['form']['type'].value(), str(puzzle_data['type']))
        self.assertEqual(response.context['form']['desc'].value(), puzzle_data['desc'])
        self.assertTrue(response.context['saved'])

    def test_POST_save_shows_all_puzzle_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle_data = {'type': 1, 'desc': 'Puzzle instructions'}
        clue1_data = {'answer': "FIRST", 'clue_text': 'Clue for word', 'parsing': 'DEF1', 'points': 2}
        clue2_data = {'answer': "SECOND", 'clue_text': 'Clue for 2nd word', 'parsing': 'DEF2', 'points': 3}
        puzzle.add_clue(clue1_data)
        puzzle.add_clue(clue2_data)
        response = self.client.post('/edit_puzzle/' + str(puzzle.id) + '/', puzzle_data)
        self.assertEqual(response.context['object'].total_points, 5)
        self.assertEqual(response.context['object'].size, 2)
        self.assertEqual(len(response.context['clues']), 2)
        self.assertEqual(response.context['clues'][0].clue_num, 1)
        self.assertEqual(response.context['clues'][0].clue_text, 'Clue for word')
        self.assertEqual(response.context['clues'][0].parsing, 'DEF1')
        self.assertEqual(response.context['clues'][0].points, 2)


class DeletePuzzleViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/delete_puzzle_confirm/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/delete_puzzle_confirm/1/")

    def test_GET_returns_delete_confirmation_options(self):
        new_puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/delete_puzzle_confirm/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("delete_confirm.html")
        self.assertContains(response, "Delete Puzzle #1")
        self.assertContains(response, "This puzzle and all associated clues will be permanently")
        self.assertContains(response, "DELETE")
        self.assertContains(response, "CANCEL")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="other_user")
        new_puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/delete_puzzle_confirm/" + str(new_puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #1")
        self.assertContains(response, "This operation is not permitted")
        self.assertContains(response, "OK")

    def test_GET_shows_error_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/delete_puzzle_confirm/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #1")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_POST_deletes_puzzle_and_redirects_to_home(self):
        WordPuzzle.objects.create(editor=self.user)
        response = self.client.post("/delete_puzzle_confirm/1/")
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed("home.html")
        self.assertFalse(WordPuzzle.objects.filter(id=1).exists())


class EditClueViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="test_user")[0]
        self.client.force_login(self.user)

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/new_clue/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/new_clue/1/")
        response = self.client.get("/edit_clue/1/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/edit_clue/1/1/")

    def test_GET_new_clue_shows_error_if_user_is_not_editor_of_puzzle(self):
        other_user = User.objects.create(username="other_user")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/new_clue/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_GET_edit_clue_shows_error_if_user_is_not_editor_of_puzzle(self):
        other_user = User.objects.create(username="other_user")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        puzzle.add_clue({'answer': 'TEST', 'clue_text': 'Clue text desc', 'parsing': '', 'points': 1})
        response = self.client.get("/edit_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Clue 1 for Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_GET_new_clue_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/new_clue/5/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #5")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_GET_edit_clue_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/edit_clue/5/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #5")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_GET_edit_clue_raises_error_message_if_clue_does_not_exist(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/edit_clue/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "This clue does not exist.")
        self.assertContains(response, "OK")

    def test_GET_new_clue_renders_template_and_clue_edit_form(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get('/new_clue/' + str(puzzle.id) + '/')
        self.assertContains(response, "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assertEqual(response.context['form']['answer'].value(), None)
        self.assertEqual(response.context['form']['clue_text'].value(), None)
        self.assertEqual(response.context['form']['parsing'].value(), None)
        self.assertEqual(response.context['form']['points'].value(), 1)
        self.assertContains(response, "SAVE")
        self.assertContains(response, "CANCEL")

    def test_GET_edit_clue_renders_template_and_clue_edit_form(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'answer': 'TEST', 'clue_text': 'Clue text desc', 'parsing': 'easy', 'points': 1})
        response = self.client.get('/edit_clue/' + str(puzzle.id) + '/' + str(clue.clue_num) + '/')
        self.assertContains(response, "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assertEqual(response.context['form']['answer'].value(), 'TEST')
        self.assertEqual(response.context['form']['clue_text'].value(), 'Clue text desc')
        self.assertEqual(response.context['form']['parsing'].value(), 'easy')
        self.assertEqual(response.context['form']['points'].value(), 1)
        self.assertContains(response, "SAVE")
        self.assertContains(response, "CANCEL")

    def test_POST_new_clue_form_creates_clue_and_redirects_to_edit_puzzle_view(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_form_data = {'answer': "MY WORD", 'clue_text': 'clue to my word', 'parsing': '', 'points': 2}
        response = self.client.post('/new_clue/' + str(puzzle.id) + '/', clue_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTemplateUsed('edit_puzzle.html')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(updated_puzzle.size, 1)
        self.assertEqual(updated_puzzle.total_points, 2)

    def test_POST_new_clue_form_does_not_save_form_if_errors(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_form_data = {'answer': "word", 'clue_text': '', 'parsing': '', 'points': 2}
        response = self.client.post('/new_clue/' + str(puzzle.id) + '/', clue_form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "edit_clue.html")
        self.assertContains(response, "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 0)

    def test_POST_edit_clue_form_updates_clue_and_redirects_to_edit_puzzle_view(self):
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

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'points': 1})
        response = self.client.get("/delete_clue_confirm/" + str(puzzle.id) + "/" + str(clue.clue_num) + '/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/delete_clue_confirm/1/1/")

    def test_GET_returns_delete_confirmation_options(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.get("/delete_clue_confirm/" + str(puzzle.id) + '/' + str(clue.clue_num) + '/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("delete_confirm.html")
        self.assertContains(response, "Delete Clue 1 for Puzzle #1")
        self.assertContains(response, "This clue will be permanently deleted")
        self.assertContains(response, "DELETE")
        self.assertContains(response, "CANCEL")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="other_user")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.get("/delete_clue_confirm/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Clue 1 for Puzzle #1")
        self.assertContains(response, "This operation is not permitted since you are not the editor.")
        self.assertContains(response, "OK")

    def test_GET_shows_error_if_puzzle_or_clue_does_not_exist(self):
        response = self.client.get("/delete_clue_confirm/1/1/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Clue 1 for Puzzle #1")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/delete_clue_confirm/" + str(puzzle.id) + "/1/")
        self.assertContains(response, "This clue does not exist.")

    def test_POST_deletes_clue_updates_points_and_redirects_to_edit_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': '', 'points': 1})
        response = self.client.post("/delete_clue_confirm/" + str(puzzle.id) + "/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/edit_puzzle/" + str(puzzle.id) + '/')
        self.assertFalse(Clue.objects.filter(puzzle=puzzle, clue_num=1).exists())
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.size, 0)
        self.assertEqual(puzzle.total_points, 0)

    def test_POST_renumbers_clues_after_delete_to_eliminate_gaps(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': '', 'points': 1})
        puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue 2', 'parsing': '', 'points': 2})
        puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue 3', 'parsing': '', 'points': 3})
        puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue 4', 'parsing': '', 'points': 4})
        self.client.post("/delete_clue_confirm/" + str(puzzle.id) + "/2/")
        clues = Clue.objects.filter(puzzle=puzzle)
        self.assertEqual(len(clues), 3)
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.size, 3)
        self.assertEqual(puzzle.total_points, 8)
        self.assertEqual(clues[0].clue_num, 1)
        self.assertEqual(clues[1].clue_num, 2)
        self.assertEqual(clues[2].clue_num, 3)


class PublishPuzzleViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="test_user")
        self.client.force_login(self.user)

    def test_GET_redirects_to_LOGIN_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get("/publish_puzzle/1/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/publish_puzzle/1/")

    def test_GET_shows_error_if_user_is_not_editor(self):
        other_user = User.objects.create(username="other_user")
        puzzle = WordPuzzle.objects.create(editor=other_user)
        response = self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "OK")
        self.assertContains(response, "This operation is not permitted since you are not the editor.")

    def test_GET_shows_error_if_puzzle_does_not_exist(self):
        response = self.client.get("/publish_puzzle/50/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_GET_sets_shared_at_field_to_now_and_redirects_to_homepage(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.assertIsNone(puzzle.shared_at)
        response = self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNotNone(updated_puzzle.shared_at)

    def test_GET_does_nothing_if_shared_at_is_already_set(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
        shared_at = WordPuzzle.objects.get(id=puzzle.id).shared_at
        response = self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # do it again
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(shared_at, updated_puzzle.shared_at)

    def test_GET_shows_error_if_puzzle_has_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("/puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "No clues to publish.  Add clues before publishing.")
        self.assertContains(response, "OK")

    def test_EDIT_PUZZLE_shows_error_if_puzzle_is_published(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
        response = self.client.get("/edit_puzzle/" + str(puzzle.id) + "/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed("/puzzle_error.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))
        self.assertContains(response, "Published puzzle cannot be edited. Unpublish to edit.")
        self.assertContains(response, "OK")

    def test_PREVIEW_PUZZLE_does_not_show_error_if_puzzle_is_published(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
        response = self.client.get("/preview_puzzle/" + str(puzzle.id) + "/")
        self.assertTemplateUsed("/word_puzzle.html")
        self.assertContains(response, "Puzzle #" + str(puzzle.id))


class UnpublishPuzzleViewTest(TestCase):
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
        self.assertTemplateUsed("puzzle_error.html")
        self.assertContains(response, "Puzzle #50")
        self.assertContains(response, "This puzzle does not exist.")
        self.assertContains(response, "OK")

    def test_GET_sets_shared_at_field_to_None_and_redirects_to_homepage(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD', 'clue_text': 'some clue text', 'points': 1})
        self.client.get("/publish_puzzle/" + str(puzzle.id) + "/")  # Publish puzzle
        response = self.client.get("/unpublish_puzzle/" + str(puzzle.id) + "/")  # Unublish puzzle
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)