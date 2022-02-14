from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib import auth
from user_auth.forms import NewUserForm
from django import utils
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

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
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")

    def test_Renders_login_page_if_user_is_not_authenticated(self):
        response = self.client.get('/login')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "login.html")
        self.assertContains(response, "Sign In")
        self.assertEquals(type(response.context['form']), AuthenticationForm)

    def test_Redirects_to_home_page_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/login')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/")

    def test_Login_has_validation_errors_with_incorrect_login(self):
        # Username does not exist
        login_data = {'username': 'pga', 'password': 'password1'}
        response = self.client.post('/login', login_data)
        self.assertEquals(response.status_code, 200)
        error_msg = 'Please enter a correct username and password'
        self.assertTrue(error_msg in response.context['form'].errors['__all__'][0])

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

# When url is /password_reset or /password_reset_done ...
class PasswordResetViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")

    def test_Password_reset_shows_form_if_user_is_not_authenticated(self):
        response = self.client.get('/password_reset')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "password_reset.html")
        self.assertContains(response, "SEND EMAIL")
        self.assertEquals(type(response.context['form']), PasswordResetForm)
        self.assertContains(response, "Reset Password")
        self.assertNotContains(response, "Password reset sent")

    def test_Password_reset_has_redirect_code_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/password_reset')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "password_reset.html")
        self.assertContains(response, "window.location.replace")
        self.assertNotContains(response, "Reset Password")
        self.assertNotContains(response, "Password reset sent")

    def test_Password_reset_done_shows_message_if_user_is_not_authenticated(self):
        response = self.client.get('/password_reset_done')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "password_reset.html")
        self.assertContains(response, "RE-ENTER EMAIL")
        self.assertContains(response, "Password reset sent")
        self.assertNotContains(response, "Reset Password")

# When url is /password_reset_confirm or /password_reset_complete ...
class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")

    def test_Password_reset_confirm_has_redirect_code_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/password_reset_confirm/mq/code/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "password_reset_confirm.html")
        self.assertContains(response, "window.location.replace")
        self.assertNotContains(response, "Enter new password")
        self.assertNotContains(response, "Password reset complete")

    def test_Password_reset_complete_has_redirect_code_if_user_is_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/password_reset_complete')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "password_reset_confirm.html")
        self.assertContains(response, "window.location.replace")
        self.assertNotContains(response, "Enter new password")
        self.assertNotContains(response, "Password reset complete")

    def test_Password_reset_complete_shows_link_to_login_if_user_is_not_authenticated(self):
        response = self.client.get('/password_reset_complete')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.templates[0].name, "password_reset_confirm.html")
        self.assertContains(response, "SIGN IN")
        self.assertContains(response, "Password reset complete")
        self.assertNotContains(response, "Enter new password")

# When url is /account or /account/edit
class UserAccountView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey1")

    def test_Account_redirects_to_login_if_user_is_not_authenticated(self):
        response = self.client.get('/account')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/login?next=/account')

    def test_Account_shows_form_fields_has_exiting_user_data_and_readonly_fields(self):
        self.client.force_login(self.user)
        response = self.client.get('/account')
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'fieldset disabled="disabled"')
        self.assertEquals(response.context['form'].initial['username'], "testuser")
        self.assertEquals(response.context['form'].initial['first_name'], "")
        self.assertEquals(response.context['form'].initial['last_name'], "")
        self.assertEquals(response.context['form'].initial['email'], "abc@email.com")
        self.assertContains(response, "EDIT")

    def test_Account_Edit_redirects_to_login_if_user_is_not_authenticated(self):
        response = self.client.get('/account/edit/')
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, '/login?next=/account/edit/')

    def test_Account_Edit_shows_form_fields_with_exiting_user_data_and_editable_fields(self):
        self.client.force_login(self.user)
        response = self.client.get('/account/edit/')
        self.assertEquals(response.status_code, 200)
        self.assertNotContains(response, 'fieldset disabled="disabled"')
        self.assertEquals(response.context['form'].initial['email'], "abc@email.com")
        self.assertEquals(response.context['form'].initial['username'], "testuser")
        self.assertEquals(response.context['form'].initial['first_name'], "")
        self.assertEquals(response.context['form'].initial['last_name'], "")
        self.assertNotContains(response, "EDIT")
        self.assertContains(response, "SAVE")
        self.assertContains(response, "CANCEL")

    def test_Account_Edit_shows_form_errors_if_data_input_is_bad(self):
        self.client.force_login(self.user) # testuser
        self.user = User.objects.create_user("testuser2", "cde@email.com", "secretkey2")
        user_update = {'username':'testuser2', 'email':''}
        response = self.client.post('/account/edit/', user_update)  #change username to existing one
        self.assertEquals(response.status_code, 200)
        error_msg1 = 'A user with that username already exists.'
        error_msg2 = 'Email is required.'
        self.assertEquals(error_msg1, response.context['form'].errors['username'][0])
        self.assertEquals(error_msg2, response.context['form'].errors['email'][0])

    def test_Account_Edit_saves_data_if_data_input_is_good_and_redirects_to_account(self):
        self.client.force_login(self.user)
        user_update = {'username':'testuser2', 'email':'cde@email.com', 'first_name': 'Django', 'last_name': 'Tester'}
        response = self.client.post('/account/edit/', user_update)
        self.assertEquals(response.status_code, 302)  # redirect
        updated_user = User.objects.get(id=self.user.id)
        self.assertEquals(updated_user.username, 'testuser2')
        self.assertEquals(updated_user.email, 'cde@email.com')
        self.assertEquals(updated_user.first_name, 'Django')
        self.assertEquals(updated_user.last_name, 'Tester')