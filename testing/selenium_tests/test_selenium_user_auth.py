from django.contrib.auth.models import User
from selenium.webdriver.common.by import By

from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class UserAuthTests(BaseSeleniumTestCase):
    user = None
    password = 'secretkey1'

    USERNAME = "//input[@id='id_username']"
    PASSWORD1 = "//input[@id='id_password1']"
    PASSWORD2 = "//input[@id='id_password2']"
    PASSWORD = "//input[@id='id_password']"
    EMAIL = "//input[@id='id_email']"
    OLD_PASSWORD = "//input[@id='id_old_password']"
    NEW_PASSWORD1 = "//input[@id='id_new_password1']"
    NEW_PASSWORD2 = "//input[@id='id_new_password2']"
    ERROR_LIST = "//*[contains(@class,'errorlist')]"
    SIGNUP_LNK = "//a[@id='lnkSignUp']"
    SIGNUP_BTN = "//button[@id='btnSignUp']"
    SIGNIN_LNK = "//a[@id='lnkSignIn']"
    SIGNIN_BTN = "//button[@id='btnSignIn']"
    CHANGE_BTN = "//button[@id='btnChange']"
    SAVE_BTN = "//button[@id='btnSave']"
    FIRST_NAME = "//input[@id='id_first_name']"
    LAST_NAME = "//input[@id='id_last_name']"
    ACCOUNT_LNK = "//a[@id='lnkAccount']"
    EDIT_LNK = "//a[@id='lnkEditAccount']"
    RESET_BTN = "//button[@id='btnReset']"
    RESET_LNK = "//a[@id='lnkReset']"
    FORM = "//form"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)

    def test_SignUp_with_invalid_input_displays_errors(self):
        self.get('/signup')
        self.set_input_text(self.USERNAME, 'someuser')
        self.set_input_text(self.PASSWORD1, 'password1')
        self.set_input_text(self.PASSWORD2, 'password2')  # passwords do not match
        self.set_input_text(self.EMAIL, 'abc@cde.com')
        self.assert_item_count(self.ERROR_LIST, 0)
        self.do_click(self.SIGNUP_BTN)
        self.assert_text_contains(self.ERROR_LIST, "The two password fields didn")

    def test_SignUp_with_valid_input_authenticates_user_and_redirects_to_home_page(self):
        self.get('/signup')
        self.set_input_text(self.USERNAME, 'someuser')
        self.set_input_text(self.PASSWORD1, 'secretkey')
        self.set_input_text(self.PASSWORD2, 'secretkey')
        self.set_input_text(self.EMAIL, 'abc@cde.com')
        self.assert_item_count(self.ERROR_LIST, 0)
        self.do_click(self.SIGNUP_BTN)
        self.assert_current_url('/')

    def test_SignUp_links_to_login_page(self):
        self.get('/signup')
        self.do_click(self.SIGNIN_LNK)
        self.assert_current_url('/login')

    def test_LogIn_with_invalid_input_displays_errors(self):
        self.get('/login')
        self.set_input_text(self.USERNAME, 'someuser')  # invalid username
        self.set_input_text(self.PASSWORD, self.password)
        self.assert_item_count(self.ERROR_LIST, 0)
        self.do_click(self.SIGNIN_BTN)
        error_msg = "Please enter a correct username and password"
        self.assert_text_contains(self.ERROR_LIST, error_msg)

    def test_Login_with_valid_input_authenticates_user_and_redirects_to_home_page(self):
        self.login_user(self.user.username, self.password)
        self.assert_current_url('/')

    def test_Login_links_to_signup_page(self):
        self.get('/login')
        self.do_click(self.SIGNUP_LNK)
        self.assert_current_url('/signup')

    def test_Login_links_to_reset_password_page(self):
        self.get('/login')
        self.do_click(self.RESET_LNK)
        self.assert_current_url('/password_reset')

    def test_Auth_pages_redirect_to_home_page_if_user_is_already_logged_in(self):
        self.login_user(self.user.username, self.password)
        self.get('/login')
        self.assert_current_url('/')
        self.get('/signup')
        self.assert_current_url('/')
        self.get('/password_reset')
        self.assert_current_url('/')
        self.get('/password_reset_done')
        self.assert_current_url('/')
        self.get('/password_reset_confirm/MQ/code/')
        self.assert_current_url('/')
        self.get('/password_reset_complete')
        self.assert_current_url('/')

    def test_Password_reset_cancel_redirects_to_login_page(self):
        self.get('/password_reset')
        self.do_click(self.SIGNIN_LNK)
        self.assert_current_url('/login')

    def test_Password_reset_send_email_shows_email_sent_message(self):
        self.get('/password_reset')
        self.set_input_text(self.EMAIL, 'bad@email.com')
        self.do_click(self.RESET_BTN)
        self.assert_item_count(self.FORM, 0)

    def test_Password_reset_confirm_cancel_redirects_to_login_page(self):
        password_reset_url = self.get_password_reset_url(self.user, 'password_reset_confirm')
        self.get(password_reset_url)
        self.do_click(self.SIGNIN_LNK)
        self.assert_current_url('/login')

    def test_Password_reset_confirm_with_input_resets_password(self):
        password_reset_url = self.get_password_reset_url(self.user, 'password_reset_confirm')
        self.get(password_reset_url)
        self.assert_item_count(self.FORM, 1)
        self.set_input_text(self.NEW_PASSWORD1, "secretkey2")
        self.set_input_text(self.NEW_PASSWORD2, "secretkey2")
        self.do_click(self.RESET_BTN)
        self.assert_current_url('/password_reset_complete')
        self.assert_page_title("Password Reset Complete")

    def test_Password_reset_complete_links_to_login_page(self):
        self.get("/password_reset_complete")
        self.do_click(self.SIGNIN_LNK)
        self.assert_current_url('/login')

    def test_Account_page_redirects_to_login_if_user_is_not_authenticated(self):
        self.get("/account")
        self.assert_current_url('/login?next=/account')

    def test_Account_page_has_readonly_user_fields_with_existing_data(self):
        self.auto_login_user(self.user)
        self.get("/account")
        username = self.selenium.find_element(By.ID, 'id_username')
        first_name = self.selenium.find_element(By.ID, 'id_first_name')
        last_name = self.selenium.find_element(By.ID, 'id_last_name')
        email = self.selenium.find_element(By.ID, 'id_email')
        self.assertEqual(username.get_attribute('value'), 'testuser')
        self.assertEqual(email.get_attribute('value'), 'user@test.com')
        self.assertEqual(first_name.get_attribute('value'), '')
        self.assertEqual(last_name.get_attribute('value'), '')
        self.assertFalse(username.is_enabled())
        self.assertFalse(email.is_enabled())
        self.assertFalse(first_name.is_enabled())
        self.assertFalse(last_name.is_enabled())

    def test_Account_page_on_edit_btn_click_redirects_to_Account_Edit(self):
        self.auto_login_user(self.user)
        self.get("/account")
        self.do_click(self.EDIT_LNK)
        self.assert_current_url('/account/edit/')

    def test_Account_Edit_page_redirects_to_login_if_user_is_not_authenticated(self):
        self.get("/account/edit/")
        self.assertIn('/login', self.selenium.current_url)

    def test_Account_Edit_page_has_editable_user_fields_with_existing_data(self):
        self.auto_login_user(self.user)
        self.get("/account/edit/")
        username = self.selenium.find_element(By.ID, 'id_username')
        email = self.selenium.find_element(By.ID, 'id_email')
        first_name = self.selenium.find_element(By.ID, 'id_first_name')
        last_name = self.selenium.find_element(By.ID, 'id_last_name')
        self.assertEqual(username.get_attribute('value'), 'testuser')
        self.assertEqual(email.get_attribute('value'), 'user@test.com')
        self.assertEqual(first_name.get_attribute('value'), '')
        self.assertEqual(last_name.get_attribute('value'), '')
        self.assertTrue(username.is_enabled())
        self.assertTrue(email.is_enabled())
        self.assertTrue(first_name.is_enabled())
        self.assertTrue(last_name.is_enabled())

    def test_Account_Edit_page_cancel_btn_redirects_to_Accounts_page(self):
        self.auto_login_user(self.user)
        self.get("/account/edit/")
        self.do_click(self.ACCOUNT_LNK)
        self.assert_current_url('/account')

    def test_Account_Edit_page_has_errors_if_data_is_bad(self):
        self.auto_login_user(self.user)
        User.objects.create_user("testuser2", "user2@test.com", self.password)
        self.get("/account/edit/")
        self.set_input_text(self.USERNAME, "testuser2")
        self.do_click(self.SAVE_BTN)
        self.assert_text_equals(self.ERROR_LIST, "A user with that username already exists.")

    def test_Account_Edit_page_saves_data_and_redirects_to_accounts_page(self):
        self.auto_login_user(self.user)
        self.get("/account/edit/")
        self.set_input_text(self.USERNAME, "testuser2")
        self.set_input_text(self.FIRST_NAME, "Django")
        self.set_input_text(self.LAST_NAME, "Tester")
        self.set_input_text(self.EMAIL, "user2@test.com")
        self.do_click(self.SAVE_BTN)
        self.assert_current_url('/account')
        username = self.selenium.find_element(By.ID, 'id_username')
        email = self.selenium.find_element(By.ID, 'id_email')
        first_name = self.selenium.find_element(By.ID, 'id_first_name')
        last_name = self.selenium.find_element(By.ID, 'id_last_name')
        self.assertEqual(username.get_attribute('value'), 'testuser2')
        self.assertEqual(email.get_attribute('value'), 'user2@test.com')
        self.assertEqual(first_name.get_attribute('value'), 'Django')
        self.assertEqual(last_name.get_attribute('value'), 'Tester')

    def test_Change_Password_page_redirects_to_login_if_user_is_not_authenticated(self):
        self.get("/change_password")
        self.assertIn('/login', self.selenium.current_url)

    def test_Change_Password_page_has_validation_errors_with_bad_input(self):
        self.auto_login_user(self.user)
        self.get("/change_password")
        self.set_input_text(self.OLD_PASSWORD, "secrekey")
        self.set_input_text(self.NEW_PASSWORD1, "secretkey1")
        self.set_input_text(self.NEW_PASSWORD2, "secretkey1")
        self.do_click(self.CHANGE_BTN)
        error_msg = "Your old password was entered incorrectly. Please enter it again."
        self.assert_text_equals(self.ERROR_LIST, error_msg)

    def test_Change_Password_page_changes_password_and_redirects_to_confirmation(self):
        self.auto_login_user(self.user)
        self.get("/change_password")
        self.set_input_text(self.OLD_PASSWORD, "secretkey1")
        self.set_input_text(self.NEW_PASSWORD1, "secretkey2")
        self.set_input_text(self.NEW_PASSWORD2, "secretkey2")
        self.do_click(self.CHANGE_BTN)
        self.assert_current_url('/change_password_done')
