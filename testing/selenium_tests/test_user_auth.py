from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
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
        password_reset_url = self.helper.get_password_reset_url(self.user, 'password_reset_confirm')
        self.selenium.get(self.live_server_url + password_reset_url)
        self.helper.click_btn('lnkSignIn')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/login')

    def test_Password_reset_confirm_with_input_resets_password(self):
        password_reset_url = self.helper.get_password_reset_url(self.user, 'password_reset_confirm')
        self.selenium.get(self.live_server_url + password_reset_url)
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

    def test_Account_page_redirects_to_login_if_user_is_not_authenticated(self):
        self.selenium.get(self.live_server_url + "/account")
        self.assertIn(self.live_server_url + '/login', self.selenium.current_url)

    def test_Account_page_has_readonly_user_fields_with_existing_data(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/account")
        username = self.selenium.find_element(By.ID, 'id_username')
        first_name = self.selenium.find_element(By.ID, 'id_first_name')
        last_name = self.selenium.find_element(By.ID, 'id_last_name')
        email = self.selenium.find_element(By.ID, 'id_email')
        self.assertEquals(username.get_attribute('value'), 'testuser')
        self.assertEquals(email.get_attribute('value'), 'user@test.com')
        self.assertEquals(first_name.get_attribute('value'), '')
        self.assertEquals(last_name.get_attribute('value'), '')
        self.assertFalse(username.is_enabled())
        self.assertFalse(email.is_enabled())
        self.assertFalse(first_name.is_enabled())
        self.assertFalse(last_name.is_enabled())

    def test_Account_page_on_edit_btn_click_redirects_to_Account_Edit(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/account")
        self.helper.click_btn('lnkEditAccount')
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/account/edit/')

    def test_Account_Edit_page_redirects_to_login_if_user_is_not_authenticated(self):
        self.selenium.get(self.live_server_url + "/account/edit/")
        self.assertIn(self.live_server_url + '/login', self.selenium.current_url)

    def test_Account_Edit_page_has_editable_user_fields_with_existing_data(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/account/edit/")
        username = self.selenium.find_element(By.ID, 'id_username')
        email = self.selenium.find_element(By.ID, 'id_email')
        first_name = self.selenium.find_element(By.ID, 'id_first_name')
        last_name = self.selenium.find_element(By.ID, 'id_last_name')
        self.assertEquals(username.get_attribute('value'), 'testuser')
        self.assertEquals(email.get_attribute('value'), 'user@test.com')
        self.assertEquals(first_name.get_attribute('value'), '')
        self.assertEquals(last_name.get_attribute('value'), '')
        self.assertTrue(username.is_enabled())
        self.assertTrue(email.is_enabled())
        self.assertTrue(first_name.is_enabled())
        self.assertTrue(last_name.is_enabled())

    def test_Account_Edit_page_cancel_btn_redirects_to_Accounts_page(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/account/edit/")
        self.helper.click_btn("lnkAccount")
        self.assertTrue(True)

    def test_Account_Edit_page_has_errors_if_data_is_bad(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        User.objects.create_user("testuser2", "user2@test.com", self.password)
        self.selenium.get(self.live_server_url + "/account/edit/")
        self.helper.set_input_text("id_username", "testuser2")
        self.helper.click_btn("btnSave")
        errors = self.selenium.find_element(By.CLASS_NAME, 'errorlist')
        self.assertEquals(errors.text, "A user with that username already exists.")

    def test_Account_Edit_page_saves_data_and_redirects_to_accounts_page(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/account/edit/")
        self.helper.set_input_text("id_username", "testuser2")
        self.helper.set_input_text("id_first_name", "Django")
        self.helper.set_input_text("id_last_name", "Tester")
        self.helper.set_input_text("id_email", "user2@test.com")
        self.helper.click_btn("btnSave")
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/account')
        username = self.selenium.find_element(By.ID, 'id_username')
        email = self.selenium.find_element(By.ID, 'id_email')
        first_name = self.selenium.find_element(By.ID, 'id_first_name')
        last_name = self.selenium.find_element(By.ID, 'id_last_name')
        self.assertEquals(username.get_attribute('value'), 'testuser2')
        self.assertEquals(email.get_attribute('value'), 'user2@test.com')
        self.assertEquals(first_name.get_attribute('value'), 'Django')
        self.assertEquals(last_name.get_attribute('value'), 'Tester')

    def test_Change_Password_page_redirects_to_login_if_user_is_not_authenticated(self):
        self.selenium.get(self.live_server_url + "/change_password")
        self.assertIn(self.live_server_url + '/login', self.selenium.current_url)

    def test_Change_Password_page_has_validation_errors_with_bad_input(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/change_password")
        self.helper.set_input_text("id_old_password", "secrekey")
        self.helper.set_input_text("id_new_password1", "secretkey1")
        self.helper.set_input_text("id_new_password2", "secretkey1")
        self.helper.click_btn("btnChange")
        errors = self.selenium.find_element(By.CLASS_NAME, 'errorlist')
        self.assertEquals(errors.text, "Your old password was entered incorrectly. Please enter it again.")

    def test_Change_Password_page_changes_password_and_redirects_to_confirmation(self):
        self.helper.login_user(self.live_server_url + '/login', self.user.username, self.password)
        self.selenium.get(self.live_server_url + "/change_password")
        self.helper.set_input_text("id_old_password", "secretkey1")
        self.helper.set_input_text("id_new_password1", "secretkey2")
        self.helper.set_input_text("id_new_password2", "secretkey2")
        self.helper.click_btn("btnChange")
        self.assertEquals(self.selenium.current_url, self.live_server_url + '/change_password_done')
