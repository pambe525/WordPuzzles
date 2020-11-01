from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.forms.models import model_to_dict

from user_auth.forms import NewUserForm
from puzzles.models import Puzzle
import json

# ==============================================================================================
class HomeViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    def test_get_renders_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "home.html")
        self.assertContains(response, "Home")

    def test_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/")

# ==============================================================================================
class NewUserViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    def test_get_renders_view_if_user_is_not_authenticated(self):
        logout(self.client)  # logout the current user
        response = self.client.get(reverse("new_user"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "new_user.html")
        self.assertContains(response, "New User Registration")
        self.assertEquals(type(response.context['form']), NewUserForm)

    def test_get_redirects_to_home_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("new_user"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_post_with_validation_errors(self):
        # Password1 & Password2 do not match
        data_dict = {
            'username': 'pga', 'password1': 'tester1!', 'password2': 'tester2!', 'email': 'a@b.com'
        }
        response = self.client.post(reverse("new_user"), data_dict)
        self.assertEquals(response.status_code, 200)
        error_msg = "The two password fields didn't match."
        self.assertEquals(response.context['form'].errors['password2'][0], error_msg)

    def test_post_without_errors_authenticates_user(self):
        data_dict = {
            'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!', 'email': 'a@b.com'
        }
        self.client.logout()
        self.assertNotIn('_auth_user_id', self.client.session)  # No logged in user
        self.client.post(reverse("new_user"), data=data_dict)
        user = User.objects.get(username="pga")
        self.assertEquals(int(self.client.session['_auth_user_id']), user.id)
        self.assertTrue(user.is_authenticated)

    def test_post_without_errors_redirects_to_home_view(self):
        data_dict = {
            'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!', 'email': 'a@b.com'
        }
        response = self.client.post(reverse("new_user"), data_dict)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

# ==============================================================================================
class LogoutViewTests(TestCase):

    def test_get_logouts_user_and_redirects_to_login_view(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)
        self.assertIn('_auth_user_id', self.client.session)  # User is logged in
        response = self.client.get(reverse("logout"))
        self.assertNotIn('_auth_user_id', self.client.session)  # User is logged out
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login")

# ==============================================================================================
class LoginViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")
        user.save()
        self.client.force_login(user)

    def test_get_renders_view_if_user_is_not_authenticated(self):
        logout(self.client)  # logout the current user
        response = self.client.get(reverse("login"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "login.html")
        self.assertContains(response, "Sign In")
        self.assertEquals(type(response.context['form']), AuthenticationForm)

    def test_get_redirects_to_home_view_if_user_is_already_authenticated(self):
        response = self.client.get(reverse("login"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_post_with_validation_errors(self):
        logout(self.client)  # logout the current user
        # Username does not exist
        data_dict = {'username': 'pga', 'password': 'password1'}
        response = self.client.post(reverse("login"), data_dict)
        self.assertEquals(response.status_code, 200)
        error_msg = 'Please enter a correct username'
        self.assertIn(error_msg, response.context['form'].errors['__all__'][0], error_msg)

    def test_post_without_errors_logs_in_user(self):
        self.client.logout()
        data_dict = {'username': 'testuser', 'password': 'secretkey1'}
        self.client.post(reverse("login"), data=data_dict)
        user = auth.get_user(self.client)
        self.assertEquals(int(self.client.session['_auth_user_id']), user.id)
        self.assertTrue(user.is_authenticated)

    def test_post_without_errors_redirects_to_home_view(self):
        data_dict = {'username': 'testuser', 'password': 'secretkey1'}
        response = self.client.post(reverse("login"), data=data_dict)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

# ==============================================================================================
class NewPuzzleViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    ### GET Tests ------------------------------------------------------------------------------
    def test_GET_renders_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "edit_puzzle.html")

    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/new_xword_puzzle")

    def test_GET_detects_crossword_puzzle_from_url(self):
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "edit_puzzle.html")
        self.assertContains(response, "New Crossword Puzzle")

    def test_GET_detects_word_puzzle_from_url(self):
        response = self.client.get(reverse("new_word_puzzle"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "edit_puzzle.html")
        self.assertContains(response, "New Word Puzzle")

    ### POST Tests ------------------------------------------------------------------------------
    def test_POST_saves_new_record_if_id_is_zero_and_returns_saved_id(self):
        ajax_data_dict = self._create_mock_ajax_save_data_dict(id=0, size=13)
        response = self.client.post(reverse("new_word_puzzle"), data=ajax_data_dict)
        response_dict = response.json()
        self.assertEquals(response_dict['id'], 1)
        self._assert_db_record(1, json.loads(ajax_data_dict['data']))

    def test_POST_updates_record_if_existing_id_and_returns_saved_id(self):
        # first save a new record
        ajax_data_dict = self._create_mock_ajax_save_data_dict(id=0, size=13)
        response = self.client.post(reverse("new_word_puzzle"), data=ajax_data_dict)
        saved_id = response.json()['id']
        ajax_data_dict = self._create_mock_ajax_save_data_dict(id=saved_id, size=15, is_ready=True)
        response = self.client.post(reverse("new_word_puzzle"), data=ajax_data_dict)
        self.assertEquals(response.json()['id'], 1)
        self._assert_db_record(saved_id, json.loads(ajax_data_dict['data']))

    ### HELPER METHODS --------------------------------------------------------------------------
    def _create_mock_ajax_save_data_dict(self, **fields):
        puzzle_data = {'id': 0, 'size': 0, 'is_xword': True, 'desc':"", 'shared_at': None,
                       'is_ready': False, 'data':{'blocks': "", 'across':{}, 'down':{}}
        }
        puzzle_data.update(locals()['fields'])
        return {'action':'save', 'data':json.dumps(puzzle_data)}

    def _assert_db_record(self, puzzle_id, expected_data_dict):
        del expected_data_dict['id']
        data_dict = model_to_dict(Puzzle.objects.get(id=puzzle_id))
        data_dict['data'] = json.loads(data_dict['data'])
        del data_dict['id']
        del data_dict['editor']
        self.assertEquals(data_dict, expected_data_dict)

# ==============================================================================================
# class EditPuzzleViewTests(TestCase):
#     def setUp(self):
#         # Create a logged in user
#         user = User.objects.get_or_create(username="testuser")[0]
#         self.client.force_login(user)
#
#     ### GET Tests ------------------------------------------------------------------------------
#     #
#     def test_new_xword_GET_renders_view_if_user_is_authenticated(self):
#         response = self.client.get(reverse("new_xword"))
#         self.assertEquals(response.status_code, 200)
#         self.assertEquals(response.templates[0].name, "edit_puzzle.html")
#         self.assertContains(response, "New Crossword Puzzle")
#         puzzle_data = json.loads(response.context['data'])
#         self.assertEquals(0, puzzle_data['puzzle_id'])
#
#     def test_new_xword_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
#         logout(self.client)
#         response = self.client.get(reverse("new_xword"))
#         self.assertEquals(response.status_code, 302)
#         self.assertEquals(response.url, "/login?next=/new_xword")
#
#     def test_edit_xword_GET_with_puzzle_id_zero_treats_it_as_new_xword(self):
#         response = self.client.get("/edit_xword/0/")
#         self.assertEquals(response.status_code, 200)
#         self.assertEquals(response.templates[0].name, "edit_puzzle.html")
#         self.assertContains(response, "New Crossword Puzzle")
#         puzzle_data = json.loads(response.context['data'])
#         self.assertEquals(0, puzzle_data['puzzle_id'])
#
#     def test_edit_xword_GET_existing_puzzle_id_sets_html_response_title(self):
#         puzzle_id = self._create_new_puzzle_record()  # first create a record
#         response = self.client.get("/edit_xword/"+str(puzzle_id)+"/")
#         self.assertEquals(response.status_code, 200)
#         self.assertEquals(response.templates[0].name, "edit_puzzle.html")
#         self.assertContains(response, "Edit Crossword Puzzle")
#         puzzle_data = json.loads(response.context['data'])
#         self.assertEquals(puzzle_id, puzzle_data['puzzle_id'])
#
#     def test_edit_xword_GET_existing_puzzle_id_returns_puzzle_data(self):
#         puzzle_id = self._create_new_puzzle_record()  # first create a record
#         response = self.client.get("/edit_xword/"+str(puzzle_id)+"/")
#         self.assertEquals(response.status_code, 200)
#         puzzle_data = json.loads(response.context['data'])
#         self.assertEquals(5, puzzle_data['size'])
#         self.assertEquals(False, puzzle_data['is_ready'])
#         self.assertEquals(True, puzzle_data['is_xword'])
#         self.assertEquals(False, puzzle_data['is_ready'])
#         self.assertEquals("", puzzle_data['desc'])
#         self.assertEquals(None, puzzle_data['shared_at'])
#         self.assertEquals("0,1,2,3,6", puzzle_data['data']['blocks'])
#         self.assertEquals({"0-3": {"word": "one", "clue": "clue for one (3)"}}, puzzle_data['data']['across'])
#         self.assertEquals({"1-0": {"word": "four", "clue": "clue for four (4)"}}, puzzle_data['data']['down'])
#
#     def test_edit_xword_GET_flashes_error_message_if_puzzle_id_does_not_exist(self):
#         response = self.client.get("/edit_xword/1/")
#         self.assertEquals(response.status_code, 200)
#         self.assertEquals(response.context['error_message'], "Puzzle ID 1 does not exist")
#         self.assertNotContains(response, "Edit Crossword Puzzle")
#
#     def test_edit_xword_GET_flashes_error_message_if_current_user_is_not_editor(self):
#         puzzle_id = self._create_new_puzzle_record()  # first create a record
#         logout(self.client)
#         user = User.objects.get_or_create(username="newuser")[0]
#         self.client.force_login(user)
#         response = self.client.get("/edit_xword/1/")
#         self.assertEquals(response.context['error_message'], "You are not authorized to edit this puzzle")
#         self.assertNotContains(response, "Edit Crossword Puzzle")
#
#     ### POST Tests ------------------------------------------------------------------------------
#     #
#     def test_new_xword_POST_saves_an_empty_grid_and_returns_puzzle_id(self):
#         data = {'action':'save', 'data':json.dumps({'puzzle_id': 0, 'size': 10,
#                 'is_ready': False, 'data':{'blocks': "", 'across':{}, 'down':{}}})}
#         response = self.client.post(reverse('new_xword'), data=data)
#         self.assertEquals(1, response.json()['puzzle_id'])
#         records = Puzzle.objects.get_queryset()
#         self.assertEqual(len(records), 1)
#         self.assertEqual(records[0].id, 1)
#         self.assertEqual(records[0].size, 10)
#         self.assertEqual(records[0].is_ready, 0)
#         self.assertEqual(json.loads(records[0].data)['blocks'], '')
#         self.assertEqual(json.loads(records[0].data)['across'], {})
#         self.assertEqual(json.loads(records[0].data)['down'], {})
#
#     def test_new_xword_POST_saves_a_populated_grid_correctly(self):
#         data = {'puzzle_id': 0, 'grid_size': 5, 'is_ready': False, 'data':{'blocks': "0,1,2",
#                 "across": {"0-3": {"word": "one", "clue": "clue for one (3)"}},
#                 "down": {"1-0": {"word": "four", "clue": "clue for four (4)"}}}
#                 }
#         response = self.client.post(reverse('new_xword'), data={'action':'save','data':json.dumps(data)})
#         self.assertEquals(1, response.json()['puzzle_id'])
#         records = Puzzle.objects.get_queryset()
#         self.assertEqual(len(records), 1)
#         self.assertEqual(records[0].id, 1)
#         self.assertEqual(records[0].size, data['grid_size'])
#         self.assertEqual(records[0].is_ready, 0)
#         self.assertEqual(json.loads(records[0].data)['blocks'], data['blocks'])
#         self.assertEquals(json.loads(records[0].data)['across'], data['across'])
#         self.assertEquals(json.loads(records[0].data)['down'], data['down'])
#
#     def test_new_xword_POST_second_save_updates_record(self):
#         data = {'puzzle_id': 0, 'grid_size': 5, 'is_ready': False, 'blocks': "0,1,2,3",
#                 "across": {"0-3": {"word": "one", "clue": "clue for one (3)"}},
#                 "down": {"1-0": {"word": "four", "clue": "clue for four (4)"}}}
#         response = self.client.post(reverse('new_xword'), data={'action':'save','data':json.dumps(data)})
#         data['puzzle_id'] = response.json()['puzzle_id']
#         data['size'] = 6
#         data['blocks'] = "0,1,2,8,10"
#         data['is_ready'] = 'True'
#         data['across']['0-3']['word'] = "two"
#         data['down']['1-0']['word'] = "five"
#         data['down']['1-0']['clue'] = "clue for five (4)"
#         response = self.client.post(reverse('new_xword'), data={'action':'save','data':json.dumps(data)})  # 2nd save
#         records = Puzzle.objects.get_queryset()
#         self.assertEqual(len(records), 1)
#         self.assertEqual(records[0].id, 1)
#         self.assertEqual(records[0].size, data['grid_size'])
#         self.assertEqual(records[0].is_ready, 1)
#         self.assertEqual(json.loads(records[0].data)['blocks'], data['blocks'])
#         self.assertEqual(json.loads(records[0].data)['across'], data['across'])
#         self.assertEqual(json.loads(records[0].data)['down'], data['down'])
#
#     def test_new_xword_POST_delete_action_raises_error_if_record_does_not_exist(self):
#         data={'action':'delete', 'puzzle_id': 2}
#         response = self.client.post(reverse('new_xword'), data=data)
#         self.assertTrue("Puzzle id does not exist" in response.json()["error_message"])
#
#     def test_new_xword_POST_delete_action_deletes_record(self):
#         puzzle_id = self._create_new_puzzle_record()
#         data = {'action': 'delete', 'puzzle_id': puzzle_id}
#         self.client.post(reverse('new_xword'), data=data)
#         records = Puzzle.objects.get_queryset()
#         self.assertEqual(len(records), 0)
#
#     ### HELPER FUNCTIONS ------------------------------------------------------------------------------
#     #
#     def _create_new_puzzle_record(self):
#         data = {'puzzle_id': 0, 'size': 5, 'is_ready': False, 'is_xword': True, 'desc':"", 'shared_at': None,
#                 'data':{'blocks': "0,1,2,3,6", 'across': {"0-3": {"word": "one", "clue": "clue for one (3)"}},
#                 'down': {"1-0": {"word": "four", "clue": "clue for four (4)"}}}
#                 }
#         response = self.client.post(reverse('new_xword'), data={'action':'save','data':json.dumps(data)})
#         return response.json()['puzzle_id']
