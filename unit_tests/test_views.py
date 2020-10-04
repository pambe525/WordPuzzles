from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from user_auth.forms import NewUserForm
from puzzles.models import Crossword


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
        self.assertEquals(0, response.context['pk'])

    def test_new_xword_GET_redirects_to_login_view_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("new_xword"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login?next=/new_xword")

    def test_new_xword_POST_returns_error_if_grid_size_is_zero(self):
        data = {'grid_size': 0, 'grid_content': ""}
        response = self.client.post(reverse('new_xword'), data=data)
        self.assertTrue(response.context['has_error'])
        self.assertEquals("Grid size cannot be zero", response.context['message'])

    def test_new_xword_POST_returns_error_if_grid_content_does_not_match_grid_size(self):
        data = {'grid_size': 10, 'grid_content': " "*99}
        response = self.client.post(reverse('new_xword'), data=data)
        self.assertTrue(response.context['has_error'])
        self.assertEquals("Grid content length must match no. of grid squares", response.context['message'])

    def test_new_xword_POST_saves_validated_data_and_returns_puzzle_id(self):
        data = {'grid_size': 10, 'grid_content': " "*100}
        response = self.client.post(reverse('new_xword'), data=data)
        self.assertFalse(response.context['has_error'])
        self.assertEquals("", response.context['message'])
        self.assertEquals(1, response.context['puzzle_id'])
        self.assertEqual(len(Crossword.objects.get_queryset()), 1)

    def test_new_xword_POST_saves_data_correctly(self):
        data = {'grid_size': 10, 'grid_content': " " * 100}
        self.client.post(reverse('new_xword'), data=data)
        self.assertEqual(len(Crossword.objects.get_queryset()), 1)
        db_record = Crossword.objects.get(pk=1)
        self.assertEquals(data['grid_size'], db_record.grid_size)
        self.assertEquals(data['grid_content'], db_record.grid_content)
        self.assertEquals(1, db_record.editor.id)

