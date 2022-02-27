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
        self.assertContains(response, "PREVIEW")
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
        clue = puzzle.add_clue({'answer':'TEST', 'clue_text':'Clue text desc', 'parsing':'easy', 'points':1})
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
        response = self.client.post('/new_clue/' + str(puzzle.id) + '/', clue_form_data)
        self.assertEqual(response.url, '/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(updated_puzzle.size, 1)
        self.assertEqual(updated_puzzle.total_points, 2)

    def test_POST_existing_clue_form_updates_clue_and_redirects_to_edit_puzzle_view(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Instructions")
        clue_data = {'answer':'TEST', 'clue_text':'Clue text desc', 'parsing':'easy', 'points':1}
        clue = puzzle.add_clue(clue_data)
        mod_clue_data = {'answer':'MOD-TEST', 'clue_text':'Clue text', 'parsing':'not easy', 'points':2}
        response = self.client.post('/edit_clue/' + str(puzzle.id) + '/'+ str(clue.clue_num) + '/', mod_clue_data)
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

# ====================================================================================================
'''
    ### GET Tests ------------------------------------------------------------------------------
    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/new_xword_puzzle")

    def test_GET_new_xword_puzzle_returns_is_word_as_true(self):
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEqual(response.templates[0].name, "edit_puzzle.html")
        data = json.loads(response.context['data'])
        self.assertEqual(None, data['id'])
        self.assertTrue(data['is_xword'])

    def test_GET_new_word_puzzle_returns_is_word_as_false(self):
        response = self.client.get(reverse("new_word_puzzle"))
        self.assertEqual(response.templates[0].name, "edit_puzzle.html")
        data = json.loads(response.context['data'])
        self.assertEqual(None, data['id'])
        self.assertFalse(data['is_xword'])

    def test_GET_edit_puzzle_with_zero_puzzle_id_raises_error(self):
        response = self.client.get("/edit_puzzle/0/")
        self.assertEqual(response.templates[0].name, "edit_puzzle.html")
        self.assertEqual("Puzzle id 0 does not exist", response.context['error_message'])

    def test_GET_edit_puzzle_raises_error_message_if_current_user_is_not_editor(self):
        record = Puzzle.objects.create(editor=self.user)
        self.assertEqual(record.id, 1)
        logout(self.client)
        self.user = User.objects.get_or_create(username="newuser")[0]
        self.client.force_login(self.user)
        response = self.client.get("/edit_puzzle/1/")
        self.assertEqual(response.context['error_message'], "You are not authorized to edit this puzzle")

    def test_GET_edit_puzzle_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/edit_puzzle/1/")
        self.assertEqual(response.context['error_message'], "Puzzle id 1 does not exist")

    def test_GET_edit_puzzle_with_existing_puzzle_id_returns_puzzle_data(self):
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        record = self.create_new_puzzle_record(size=10, shared_at=timestamp)  # first create a record
        response = self.client.get("/edit_puzzle/" + str(record.id) + "/")
        puzzle_data = json.loads(response.context['data'])
        self.assertEqual(record.id, puzzle_data['id'])
        self.assertEqual(record.size, puzzle_data['size'])
        self.assertEqual(record.is_xword, puzzle_data['is_xword'])
        self.assertEqual(record.desc, puzzle_data['desc'])
        self.assertEqual(record.shared_at, puzzle_data['shared_at'])
        self.assertEqual(record.data, json.dumps(puzzle_data['data']))

    ### POST Tests ------------------------------------------------------------------------------
    def test_POST_raises_error_if_id_does_not_exist(self):
        ajax_data_dict = self.create_mock_ajax_save_data_dict(id=1, size=15)  # Not-existent ID
        response = self.client.post(reverse("new_word_puzzle"), data=ajax_data_dict)
        self.assertIn("does not exist", response.json()['error_message'])

    def test_POST_saves_new_record_if_id_is_null_and_returns_saved_id(self):
        ajax_data_dict = self.create_mock_ajax_save_data_dict(size=13)  # id=None by default
        response = self.client.post(reverse("new_word_puzzle"), data=ajax_data_dict)
        self.assertEqual(response.json()['id'], 1)
        self.assert_db_record(1, json.loads(ajax_data_dict['data']))

    def test_POST_second_save_updates_record(self):
        ajax_data_dict = self.create_mock_ajax_save_data_dict(
            size=5, data={'blocks': "0,1,2,3", 'across': {"0-3": {"word": "one", "clue": "clue for one (3)"}},
                          'down': {"1-0": {"word": "four", "clue": "clue for four (4)"}}}
        )
        response = self.client.post(reverse('new_xword_puzzle'), data=ajax_data_dict)
        id = response.json()['id']
        ajax_data_dict = self.create_mock_ajax_save_data_dict(id=id,
                                                              size=5, data={'blocks': "0,1,2,3,10", 'across': {
                "0-3": {"word": "two", "clue": "clue for one (3)"}},
                                                                            'down': {"1-0": {"word": "five",
                                                                                             "clue": "clue for five (4)"}}}
                                                              )
        response = self.client.post(reverse('new_xword_puzzle'), data=ajax_data_dict)  # 2nd save
        records = Puzzle.objects.get_queryset()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, id)
        expected_data = json.loads(ajax_data_dict['data'])
        self.assertEqual(records[0].size, expected_data['size'])
        self.assertEqual(records[0].is_xword, expected_data['is_xword'])
        self.assertEqual(json.loads(records[0].data)['blocks'], expected_data['data']['blocks'])
        self.assertEqual(json.loads(records[0].data)['across'], expected_data['data']['across'])
        self.assertEqual(json.loads(records[0].data)['down'], expected_data['data']['down'])

    def test_POST_delete_action_raises_error_if_record_does_not_exist(self):
        data = {'action': 'delete', 'id': '2'}
        response = self.client.post(reverse('new_xword_puzzle'), data=data)
        self.assertIn("does not exist", response.json()["error_message"])

    def test_POST_delete_action_deletes_record(self):
        record = self.create_new_puzzle_record()
        data = {'action': 'delete', 'id': str(record.id)}
        self.client.post(reverse('new_xword_puzzle'), data=data)
        records = Puzzle.objects.get_queryset()
        self.assertEqual(len(records), 0)

    ### HELPER METHODS --------------------------------------------------------------------------
    def get_puzzle_data_dict(self, **fields):
        puzzle_data = {'id': None, 'size': 0, 'is_xword': True, 'desc': "", 'shared_at': None,
                       'data': {'blocks': "", 'across': {}, 'down': {}}
                       }
        puzzle_data.update(locals()['fields'])
        return puzzle_data

    def create_new_puzzle_record(self, **fields):
        puzzle_data = self.get_puzzle_data_dict(**fields)
        puzzle_data['editor'] = self.user
        puzzle_data['data'] = json.dumps(puzzle_data['data'])
        record = Puzzle(**puzzle_data)
        record.save()
        return record

    def create_mock_ajax_save_data_dict(self, **fields):
        puzzle_data = self.get_puzzle_data_dict(**fields)
        return {'action': 'save', 'data': json.dumps(puzzle_data)}

    def assert_db_record(self, puzzle_id, expected_data_dict):
        del expected_data_dict['id']
        data_dict = model_to_dict(Puzzle.objects.get(id=puzzle_id))
        data_dict['data'] = json.loads(data_dict['data'])
        del data_dict['id']
        del data_dict['editor']
        self.assertEqual(data_dict, expected_data_dict)
'''
