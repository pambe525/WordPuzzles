from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from user_auth.forms import NewUserForm
from puzzles.models import Crossword
import json


# ==============================================================================================
#
class HomeViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    def test_get_renders_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "home.html")
        self.assertContains(response, "Home Page")

    def test_get_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/")

# ==============================================================================================
#
class EditUserViewTests(TestCase):
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
            'username': 'pga', 'password1': 'teter1!', 'password2': 'tester2!', 'email': 'a@b.com'
        }
        response = self.client.post(reverse("new_user"), data_dict)
        self.assertEquals(response.status_code, 200)
        error_msg = 'The two password fields didn’t match.'
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
#
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
#
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
#
class NewCrosswordViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)

    def test_new_xword_GET_renders_view_if_user_is_authenticated(self):
        response = self.client.get(reverse("new_xword"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "edit_xword.html")
        self.assertContains(response, "New Crossword Puzzle")
        self.assertEquals(0, response.context['puzzle_id'])

    def test_new_xword_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_xword"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/new_xword")

    def test_new_xword_POST_returns_error_if_grid_size_is_zero(self):
        data = {'data': json.dumps({'grid_size': 0})}
        with self.assertRaises(Exception) as context:
            self.client.post(reverse('new_xword'), data=data)
        self.assertTrue("Grid size cannot be zero" in str(context.exception))

    def test_new_xword_POST_returns_error_if_puzzle_id__or_content_is_missing(self):
        data = {'data':json.dumps({'grid_size': 10, 'blocks':""})}
        with self.assertRaises(Exception) as context:
            self.client.post(reverse('new_xword'), data=data)
        self.assertTrue("Missing keys in grid data" in str(context.exception))
        data = {'data':json.dumps({'puzzle_id': 0, 'grid_size': 10})}
        with self.assertRaises(Exception) as context:
            self.client.post(reverse('new_xword'), data=data)
        self.assertTrue("Missing keys in grid data" in str(context.exception))

    def test_new_xword_POST_returns_error_if_is_ready_key_is_missing(self):
        data = {'data':json.dumps({'puzzle_id': 0, 'grid_size': 10, 'blocks':"1,2,3"})}
        with self.assertRaises(Exception) as context:
            self.client.post(reverse('new_xword'), data=data)
        self.assertTrue("Missing keys in grid data" in str(context.exception))

    def test_new_xword_POST_saves_an_empty_grid_and_returns_puzzle_id(self):
        data = {'data':json.dumps({'puzzle_id': 0, 'grid_size': 10, 'is_ready': 'False', 'blocks': ""})}
        response = self.client.post(reverse('new_xword'), data=data)
        self.assertEquals(1, response.json()['puzzle_id'])
        records = Crossword.objects.get_queryset()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, 1)
        self.assertEqual(records[0].grid_size, 10)
        self.assertEqual(records[0].is_ready, 0)
        self.assertEqual(records[0].grid_blocks, "")
        self.assertEqual(records[0].across_words, "")
        self.assertEqual(records[0].down_words, "")

    def test_new_xword_POST_saves_a_populated_grid_correctly(self):
        data = {'puzzle_id': 0, 'grid_size': 5, 'is_ready': 'False', 'blocks': "0,1,2",
                "across": {"0-3": {"word": "one", "clue": "clue for one (3)"}},
                "down": {"1-0": {"word": "four", "clue": "clue for four (4)"}}}
        response = self.client.post(reverse('new_xword'), data={'data':json.dumps(data)})
        self.assertEquals(1, response.json()['puzzle_id'])
        records = Crossword.objects.get_queryset()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, 1)
        self.assertEqual(records[0].grid_size, data['grid_size'])
        self.assertEqual(records[0].is_ready, 0)
        self.assertEqual(records[0].grid_blocks, data['blocks'])
        self.assertEqual(records[0].across_words, json.dumps(data['across']))
        self.assertEqual(records[0].down_words, json.dumps(data['down']))

    def test_new_xword_POST_second_save_updates_record(self):
        data = {'puzzle_id': 0, 'grid_size': 5, 'is_ready': 'False', 'blocks': "0,1,2,3",
                "across": {"0-3": {"word": "one", "clue": "clue for one (3)"}},
                "down": {"1-0": {"word": "four", "clue": "clue for four (4)"}}}
        response = self.client.post(reverse('new_xword'), data={'data':json.dumps(data)})
        data['puzzle_id'] = response.json()['puzzle_id']
        data['grid_size'] = 6
        data['blocks'] = "0,1,2,8,10"
        data['is_ready'] = 'True'
        data['across']['0-3']['word'] = "two"
        data['down']['1-0']['word'] = "five"
        data['down']['1-0']['clue'] = "clue for five (4)"
        response = self.client.post(reverse('new_xword'), data={'data':json.dumps(data)})  # second save
        records = Crossword.objects.get_queryset()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].id, 1)
        self.assertEqual(records[0].grid_size, data['grid_size'])
        self.assertEqual(records[0].is_ready, 1)
        self.assertEqual(records[0].grid_blocks, data['blocks'])
        self.assertEqual(records[0].across_words, json.dumps(data['across']))
        self.assertEqual(records[0].down_words, json.dumps(data['down']))
