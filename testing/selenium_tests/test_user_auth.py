from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from selenium.webdriver.common.by import By

from testing.selenium_tests.helper import Helper


class UserAuthTests(StaticLiveServerTestCase):
    helper = Helper()
    selenium = helper.selenium
    password = 'secretkey1'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user("testuser", "user@test.com", self.password)

    def test_SignUp_with_invalid_input_displays_errors(self):
        self.helper.get(self.live_server_url + '/signup')
        self.helper.set_input_text('id_username', 'someuser')
        self.helper.set_input_text('id_password1', 'password1')
        self.helper.set_input_text('id_password2', 'password2')  # passwords do not match
        self.helper.set_input_text('id_email', 'abc@cde.com')
        self.assertEquals(len(self.selenium.find_elements(By.CLASS_NAME, 'errorlist')), 0)
        self.helper.click_btn('btnSignUp')
        error_msg = self.selenium.find_elements(By.CLASS_NAME, 'errorlist')[0].text
        self.assertTrue("The two password fields didn" in error_msg)

    def test_SignUp_with_valid_input_authenticates_user_and_redirects_to_home_page(self):
        self.helper.get(self.live_server_url + '/signup')
        self.helper.set_input_text('id_username', 'someuser')
        self.helper.set_input_text('id_password1', 'secretkey')
        self.helper.set_input_text('id_password2', 'secretkey')
        self.helper.set_input_text('id_email', 'abc@cde.com')
        self.assertEquals(len(self.selenium.find_elements(By.CLASS_NAME, 'errorlist')), 0)
        self.helper.click_btn('btnSignUp')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')

    def test_SignUp_links_to_login_page(self):
        self.selenium.get(self.live_server_url + '/signup')
        self.helper.click_btn('lnkSignIn')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/login')

    def test_LogIn_with_invalid_input_displays_errors(self):
        self.selenium.get(self.live_server_url + '/login')
        self.helper.set_input_text('id_username', 'someuser')  # invalid username
        self.helper.set_input_text('id_password', self.password)
        self.assertEquals(len(self.selenium.find_elements(By.CLASS_NAME, 'errorlist')), 0)
        self.helper.click_btn('btnSignIn')
        error_msg = self.selenium.find_elements(By.CLASS_NAME, 'errorlist')[0].text
        self.assertTrue("Please enter a correct username and password" in error_msg)

    def test_Login_with_valid_input_authenticates_user_and_redirects_to_home_page(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')

    def test_Login_links_to_signup_page(self):
        self.selenium.get(self.live_server_url + '/login')
        self.helper.click_btn('lnkSignUp')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/signup')

    def test_Login_links_to_reset_password_page(self):
        self.selenium.get(self.live_server_url + '/login')
        self.helper.click_btn('lnkReset')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/password_reset')

    def test_Auth_pages_redirect_to_home_page_if_user_is_already_logged_in(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + '/login')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')
        self.selenium.get(self.live_server_url + '/signup')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')
        self.selenium.get(self.live_server_url + '/password_reset')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')
        self.selenium.get(self.live_server_url + '/password_reset_done')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')
        self.selenium.get(self.live_server_url + '/password_reset_confirm/MQ/code/')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')
        self.selenium.get(self.live_server_url + '/password_reset_complete')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/')

    def test_Password_reset_cancel_redirects_to_login_page(self):
        self.selenium.get(self.live_server_url + '/password_reset')
        self.helper.click_btn('lnkSignIn')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/login')

    def test_Password_reset_send_email_shows_email_sent_message(self):
        self.selenium.get(self.live_server_url + '/password_reset')
        self.helper.set_input_text('id_email', 'bad@email.com')
        self.helper.click_btn('btnReset')
        self.assertEquals(len(self.selenium.find_elements(By.TAG_NAME, 'form')), 0)

    def test_Password_reset_confirm_cancel_redirects_to_login_page(self):
        self.selenium.get(self.live_server_url + self.get_password_reset_url())
        self.helper.click_btn('lnkSignIn')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/login')

    def test_Password_reset_confirm_with_input_resets_password(self):
        self.selenium.get(self.live_server_url + self.get_password_reset_url())
        self.assertEquals(len(self.selenium.find_elements(By.TAG_NAME, 'form')), 1)
        self.helper.set_input_text('id_new_password1', "secretkey2")
        self.helper.set_input_text('id_new_password2', "secretkey2")
        self.helper.click_btn('btnReset')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/password_reset_complete')
        title = self.selenium.find_element(By.TAG_NAME, 'h2').text
        self.assertEquals(title, "Password reset complete")

    def test_Password_reset_complete_links_to_login_page(self):
        self.selenium.get(self.live_server_url + "/password_reset_complete")
        self.helper.click_btn('lnkSignIn')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/login')

    # HELPER FUNCTION
    def get_password_reset_url(self):
        base64_encoded_id = urlsafe_base64_encode(force_bytes(self.user.id))
        token = PasswordResetTokenGenerator().make_token(self.user)
        reset_url_args = {'uidb64': base64_encoded_id, 'token': token}
        reset_path = reverse('password_reset_confirm', kwargs=reset_url_args)
        return reset_path
