from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.contrib import auth

from user_auth.forms import NewUserForm


# When url is /signup ...
class SignUpViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")
        self.new_user_data = {
            'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!', 'email': 'a@b.com',
        }

    def test_Renders_signin_page_if_user_is_not_authenticated(self):
        response = self.client.get('/signup')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "signup.html")
        self.assertContains(response, "Sign Up as New User")
        self.assertEquals(type(response.context['form']), NewUserForm)
        self.assertContains(response, "Log In")

    def test_Redirects_to_home_page_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/signup')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_Signup_form_has_validation_messages_if_form_has_errors(self):
        # Password1 & Password2 do not match
        self.new_user_data['password2'] = 'tester2!'
        response = self.client.post('/signup', self.new_user_data)
        self.assertEquals(200, response.status_code)
        self.assertEquals('signup.html', response.templates[0].name)
        error_msg = 'The two password fields didn'
        self.assertTrue(error_msg in response.context['form'].errors['password2'][0])

    def test_User_is_saved_and_authenticated_if_signup_form_has_no_errors(self):
        self.assertNotIn('_auth_user_id', self.client.session)  # No logged in user
        self.client.post('/signup', self.new_user_data)
        user = User.objects.get(username="pga")
        self.assertEquals(int(self.client.session['_auth_user_id']), user.id)
        self.assertTrue(user.is_authenticated)

    def test_Redirects_to_home_page_after_proper_signup(self):
        response = self.client.post('/signup', self.new_user_data)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

# When url is /logout ...
class LogoutViewTests(TestCase):

    def test_Logs_out_user_and_redirects_to_login_page(self):
        # Create a logged in user
        user = User.objects.get_or_create(username="testuser")[0]
        self.client.force_login(user)
        self.assertIn('_auth_user_id', self.client.session)  # User is logged in
        response = self.client.get(reverse("logout"))
        self.assertNotIn('_auth_user_id', self.client.session)  # User is logged out
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login")


# When url is /login ...
class LoginViewTests(TestCase):
    def setUp(self):
        # Create a logged in user
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")
        # self.client.force_login(user)

    def test_Renders_login_page_if_user_is_not_authenticated(self):
        response = self.client.get('/login')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "signup.html")
        self.assertContains(response, "Sign In")
        self.assertEquals(type(response.context['form']), AuthenticationForm)
        self.assertContains(response, "Sign Up")

    def test_Redirects_to_home_page_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/login')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_Login_has_validation_errors_with_incorrect_login(self):
        # Username does not exist
        login_data = {'username': 'pga', 'password': 'password1', 'btnSignIn': 'Sign In'}
        response = self.client.post('/login', login_data)
        self.assertEquals(response.status_code, 200)
        error_msg = 'Please enter a correct username and password'
        self.assertTrue(error_msg in response.context['signin_form'].errors['__all__'][0])

    def test_Authenticates_user_if_login_has_no_errors(self):
        data_dict = {'username': 'testuser', 'password': 'secretkey1'}
        self.client.post('/login', data=data_dict)
        user = auth.get_user(self.client)
        self.assertEquals(int(self.client.session['_auth_user_id']), user.id)
        self.assertTrue(user.is_authenticated)

    def test_Redirects_to_home_page_after_signin(self):
        data_dict = {'username': 'testuser', 'password': 'secretkey1'}
        response = self.client.post('/login', data=data_dict)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

def validate_login_page(self, response):
    self.assertEquals(response.status_code, 200)
    self.assertEquals(response.templates[0].name, "login.html")
    self.assertContains(response, "Sign In")
    self.assertContains(response, "New User")
    self.assertEquals(type(response.context['signup_form']), NewUserForm)
    self.assertEquals(type(response.context['signin_form']), AuthenticationForm)