import os

from django.conf import settings
from django.contrib.auth import (SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY)
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from selenium.common import ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from testing.selenium_tests.singleton_webdriver import SingletonWebDriver


class HelperMixin:
    selenium = None
    server_url = None
    testcase = None
    cookie_path = os.getcwd() + '/cookies.pkl'

    @staticmethod
    def get_selenium_webdriver(headless=True):
        return SingletonWebDriver().start_webdriver(headless)

    @staticmethod
    def quit_selenium_webdriver():
        SingletonWebDriver().quit_webdriver()

    @staticmethod
    def create_session_cookie(user):
        session = SessionStore()
        session[SESSION_KEY] = user.pk
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()
        cookie = {'name': settings.SESSION_COOKIE_NAME, 'value': session.session_key, 'secure': False, 'path': '/'}
        return cookie

    def get(self, url):
        self.selenium.get(self.server_url + url)

    def set_input_text(self, xpath, input_text):
        element = self.selenium.find_element(By.XPATH, xpath)
        element.clear()
        element.send_keys(input_text)

    def do_click(self, xpath):
        try:
            self.selenium.find_element(By.XPATH, xpath).click()
            return True
        except WebDriverException:
            return False

    def auto_login_user(self, user):
        session_cookie = self.create_session_cookie(user)
        self.get('/login')
        self.selenium.add_cookie(session_cookie)
        self.selenium.refresh()

    def logout_user(self):
        self.get('/logout')

    def login_user(self, username, password):
        self.get('/login')
        self.set_input_text("//input[@id='id_username']", username)
        self.set_input_text("//input[@id='id_password']", password)
        self.do_click("//button[@id='btnSignIn']")

    def get_password_reset_url(self, user, password_reset_base_url):
        base64_encoded_id = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url_args = {'uidb64': base64_encoded_id, 'token': token}
        reset_path = reverse(password_reset_base_url, kwargs=reset_url_args)
        return reset_path

    def assert_current_url(self, url):
        self.testcase.assertEqual(self, self.selenium.current_url, self.server_url + url)

    def assert_text_equals(self, xpath, text, index=0):
        element = self.selenium.find_elements(By.XPATH, xpath)[index]
        self.testcase.assertEqual(self, element.text, text)

    def assert_attribute_equals(self, xpath, attr, val, index=0):
        element = self.selenium.find_elements(By.XPATH, xpath)[index]
        self.testcase.assertEqual(self, element.get_attribute(attr), val)

    def assert_attribute_contains(self, xpath, attr, val, index=0):
        element = self.selenium.find_elements(By.XPATH, xpath)[index]
        self.testcase.assertTrue(self, val in element.get_attribute(attr))

    def assert_item_count(self, xpath, count):
        self.testcase.assertEqual(self, len(self.selenium.find_elements(By.XPATH, xpath)), count)

    def assert_text_contains(self, xpath, text, index=0):
        self.testcase.assertTrue(self, text in self.selenium.find_elements(By.XPATH, xpath)[index].text)

    def assert_exists(self, xpath):
        self.testcase.assertTrue(self, len(self.selenium.find_elements(By.XPATH, xpath)) > 0)

    def assert_not_exists(self, xpath):
        self.testcase.assertTrue(self, len(self.selenium.find_elements(By.XPATH, xpath)) == 0)

    def assert_selected_text(self, xpath, text):
        selector = Select(self.selenium.find_element(By.XPATH, xpath))
        self.testcase.assertEqual(self, selector.first_selected_option.text, text)

    def get_element(self, xpath, index=0):
        return self.selenium.find_elements(By.XPATH, xpath)[index]

    def select_by_text(self, xpath, visible_text):
        selector = Select(self.selenium.find_element(By.XPATH, xpath))
        selector.select_by_visible_text(visible_text)

    def assert_is_not_displayed(self, xpath, index=0):
        self.testcase.assertFalse(self, self.selenium.find_elements(By.XPATH, xpath)[index].is_displayed())

    def assert_is_displayed(self, xpath, index=0):
        self.testcase.assertTrue(self, self.selenium.find_elements(By.XPATH, xpath)[index].is_displayed())

    def wait_until_invisible(self, xpath):
        WebDriverWait(self.selenium, 5).until(EC.invisibility_of_element((By.XPATH, xpath)))

    def wait_until_visible(self, xpath):
        # element = self.selenium.find_element(By.XPATH, xpath)
        WebDriverWait(self.selenium, 5).until(EC.visibility_of_element_located((By.XPATH, xpath)))

    def wait_until_clickable(self, xpath):
        WebDriverWait(self.selenium, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))


# Parent class from which all selenium test cases will be derived
class BaseSeleniumTestCase(HelperMixin, StaticLiveServerTestCase):
    SPAN_USERNAME = "//span[contains(@class,'current-user')]"
    NAV_MENU = "//nav[contains(@class,'navbar')]"
    MENU_TOGGLE = "//a[contains(@class,'menu-toggle-button')]"
    MENUITEM_HOME = "//nav/ul/li[1]"
    LOGO = "//img[@class='logo']"
    PAGE_TITLE = "//div[@class='page-title']"
    SUBTITLE = "//div[contains(@class,'subtitle')]"
    ACTIVE_MENUITEM = "//nav/ul/li/a[@class='active']"
    reset_sequences = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = cls.get_selenium_webdriver()
        cls.server_url = cls.live_server_url
        cls.testcase = cls

    @classmethod
    def tearDownClass(cls):
        cls.quit_selenium_webdriver()
        super().tearDownClass()

    def set_mobile_size(self, flag=True):
        if flag:
            self.selenium.set_window_size(390, 840)
        else:
            self.selenium.set_window_size(800, 1080)

    def assert_page_title(self, title):
        self.assert_text_equals(self.PAGE_TITLE, title)

    def assert_subtitle(self, title, index=0):
        self.assert_text_equals(self.SUBTITLE, title, index)

    def assert_active_page_nav_link_hilited(self, page_url, page_title):
        self.get(page_url)
        self.assert_page_title(page_title)
        self.assert_text_equals(self.ACTIVE_MENUITEM, page_title)

    @staticmethod
    def utc_to_local(utc_datetime):
        if os.name == "nt":
            dt_format = '%#m/%#d/%Y, %#I:%M:%S %p'
        else:
            dt_format = '%-m/%-d/%Y, %-I:%M:%S %p'
        return utc_datetime.astimezone().strftime(dt_format)
