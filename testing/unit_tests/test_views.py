import json
from datetime import datetime

from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from puzzles.models import Puzzle
from user_auth.forms import NewUserForm


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
        error_msg = 'The two password fields didn'
        self.assertTrue(error_msg in response.context['form'].errors['password2'][0])

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
class EditPuzzleViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        self.user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(self.user)

    ### GET Tests ------------------------------------------------------------------------------
    def test_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/new_xword_puzzle")

    def test_GET_new_xword_puzzle_returns_is_word_as_true(self):
        response = self.client.get(reverse("new_xword_puzzle"))
        self.assertEquals(response.templates[0].name, "edit_puzzle.html")
        data = json.loads(response.context['data'])
        self.assertEquals(None, data['id'])
        self.assertTrue(data['is_xword'])

    def test_GET_new_word_puzzle_returns_is_word_as_false(self):
        response = self.client.get(reverse("new_word_puzzle"))
        self.assertEquals(response.templates[0].name, "edit_puzzle.html")
        data = json.loads(response.context['data'])
        self.assertEquals(None, data['id'])
        self.assertFalse(data['is_xword'])

    def test_GET_edit_puzzle_with_zero_puzzle_id_raises_error(self):
        response = self.client.get("/edit_puzzle/0/")
        self.assertEquals(response.templates[0].name, "edit_puzzle.html")
        self.assertEquals("Puzzle id 0 does not exist", response.context['error_message'])

    def test_GET_edit_puzzle_raises_error_message_if_current_user_is_not_editor(self):
        record = Puzzle.objects.create(editor=self.user)
        self.assertEquals(record.id, 1)
        logout(self.client)
        self.user = User.objects.get_or_create(username="newuser")[0]
        self.client.force_login(self.user)
        response = self.client.get("/edit_puzzle/1/")
        self.assertEquals(response.context['error_message'], "You are not authorized to edit this puzzle")

    def test_GET_edit_puzzle_raises_error_message_if_puzzle_id_does_not_exist(self):
        response = self.client.get("/edit_puzzle/1/")
        self.assertEquals(response.context['error_message'], "Puzzle id 1 does not exist")

    def test_GET_edit_puzzle_with_existing_puzzle_id_returns_puzzle_data(self):
        timestamp = datetime.now(tz=timezone.utc).isoformat()
        record = self.create_new_puzzle_record(size=10, shared_at=timestamp)  # first create a record
        response = self.client.get("/edit_puzzle/" + str(record.id) + "/")
        puzzle_data = json.loads(response.context['data'])
        self.assertEqual(record.size, puzzle_data['size'])
        self.assertEqual(record.is_ready, puzzle_data['is_ready'])
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
        self.assertEquals(response.json()['id'], 1)
        self.assert_db_record(1, json.loads(ajax_data_dict['data']))

    def test_POST_second_save_updates_record(self):
        ajax_data_dict = self.create_mock_ajax_save_data_dict(
            size=5, data={'blocks':"0,1,2,3", 'across':{"0-3": {"word": "one", "clue": "clue for one (3)"}},
            'down':{"1-0": {"word": "four", "clue": "clue for four (4)"}}}
        )
        response = self.client.post(reverse('new_xword_puzzle'), data=ajax_data_dict)
        id = response.json()['id']
        ajax_data_dict = self.create_mock_ajax_save_data_dict(id=id,
            size=5, data={'blocks':"0,1,2,3,10", 'across':{"0-3": {"word": "two", "clue": "clue for one (3)"}},
            'down':{"1-0": {"word": "five", "clue": "clue for five (4)"}}}
        )
        response = self.client.post(reverse('new_xword_puzzle'), data=ajax_data_dict)  # 2nd save
        records = Puzzle.objects.get_queryset()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, id)
        expected_data = json.loads(ajax_data_dict['data'])
        self.assertEqual(records[0].size, expected_data['size'])
        self.assertEqual(records[0].is_ready, expected_data['is_ready'])
        self.assertEqual(records[0].is_xword, expected_data['is_xword'])
        self.assertEqual(json.loads(records[0].data)['blocks'], expected_data['data']['blocks'])
        self.assertEqual(json.loads(records[0].data)['across'], expected_data['data']['across'])
        self.assertEqual(json.loads(records[0].data)['down'], expected_data['data']['down'])

    def test_POST_delete_action_raises_error_if_record_does_not_exist(self):
        data={'action':'delete', 'id': 2}
        response = self.client.post(reverse('new_xword_puzzle'), data=data)
        self.assertIn("does not exist", response.json()["error_message"])

    def test_POST_delete_action_deletes_record(self):
        record = self.create_new_puzzle_record()
        data = {'action': 'delete', 'id': record.id}
        self.client.post(reverse('new_xword_puzzle'), data=data)
        records = Puzzle.objects.get_queryset()
        self.assertEqual(len(records), 0)

    ### HELPER METHODS --------------------------------------------------------------------------
    def get_puzzle_data_dict(self, **fields):
        puzzle_data = {'id': None, 'size': 0, 'is_xword': True, 'desc': "", 'shared_at': None,
                       'is_ready': False, 'data': {'blocks': "", 'across': {}, 'down': {}}
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
        self.assertEquals(data_dict, expected_data_dict)
