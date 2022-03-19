from os import name as os_name

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select


### This class is required to run all selenium tests in a single browser instance
class SingletonWebDriver(object):
    _instance = None
    _browser = 'Firefox'

    webdriver = None
    is_persistent = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonWebDriver, cls).__new__(cls)
        return cls._instance

    def _create_webdriver(self):
        if os_name == 'nt':
            if self._browser == 'Chrome':
                webdriver_path = 'C:\\Users\Prashant\Documents\PyCharmProjects\chromedriver.exe'
                driver = webdriver.Chrome(executable_path=webdriver_path)
            else:
                webdriver_path = 'C:\\Users\Prashant\Documents\PyCharmProjects\geckodriver.exe'
                driver = webdriver.Firefox(executable_path=webdriver_path)
        else:
            path = '/Library/Frameworks/Python.framework/Versions/3.8/bin/'
            if self._browser == 'Firefox':
                webdriver_path = path + 'geckodriver'
                driver = webdriver.Firefox(executable_path=webdriver_path)
            else:
                webdriver_path = path + 'chromedriver'
                driver = webdriver.Chrome(executable_path=webdriver_path)
        return driver

    def start_webdriver(self):
        if self.webdriver is None:
            self.webdriver = self._create_webdriver()
        return self.webdriver

    def quit_webdriver(self):
        if not self.is_persistent:
            self.webdriver.quit()
            self.webdriver = None


class HelperMixin:
    selenium = None
    server_url = None
    testcase = None

    @staticmethod
    def get_selenium_webdriver():
        return SingletonWebDriver().start_webdriver()

    @staticmethod
    def quit_selenium_webdriver():
        SingletonWebDriver().quit_webdriver()

    def get(self, url):
        self.selenium.get(self.server_url + url)

    def set_input_text(self, input_id, input_text):
        element = self.selenium.find_element(By.ID, input_id)
        element.clear()
        element.send_keys(input_text)

    def set_input_xpath(self, xpath, input_text):
        element = self.selenium.find_element(By.XPATH, xpath)
        element.clear()
        element.send_keys(input_text)

    def click_btn(self, btn_id):
        self.selenium.find_element(By.ID, btn_id).click()

    def click_xpath(self, xpath):
        self.selenium.find_element(By.XPATH, xpath).click()

    def login_user(self, username, password):
        self.get('/login')
        self.set_input_text('id_username', username)
        self.set_input_text('id_password', password)
        self.click_xpath("//button[@id='btnSignIn']")

    def get_password_reset_url(self, user, password_reset_base_url):
        base64_encoded_id = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url_args = {'uidb64': base64_encoded_id, 'token': token}
        reset_path = reverse(password_reset_base_url, kwargs=reset_url_args)
        return reset_path

    def assert_current_url(self, url):
        self.testcase.assertEqual(self, self.selenium.current_url, self.server_url + url)

    def assert_xpath_text(self, xpath, text, index=0):
        element = self.selenium.find_elements(By.XPATH, xpath)[index]
        self.testcase.assertEqual(self, element.text, text)

    def assert_xpath_value(self, xpath, text, index=0):
        element = self.selenium.find_elements(By.XPATH, xpath)[index]
        self.testcase.assertEqual(self, element.get_attribute('value'), text)

    def assert_xpath_items(self, xpath, count):
        self.testcase.assertEqual(self, len(self.selenium.find_elements(By.XPATH, xpath)), count)

    def assert_xpath_contains(self, xpath, text, index=0):
        self.testcase.assertTrue(self, text in self.selenium.find_elements(By.XPATH, xpath)[index].text)

    def assert_xpath_exists(self, xpath):
        self.testcase.assertTrue(self, len(self.selenium.find_elements(By.XPATH, xpath)) > 0)

    def assert_xpath_not_exists(self, xpath):
        self.testcase.assertTrue(self, len(self.selenium.find_elements(By.XPATH, xpath)) == 0)

    def assert_selected_text(self, xpath, text):
        selector = Select(self.selenium.find_element(By.XPATH, xpath))
        self.testcase.assertEqual(self, selector.first_selected_option.text, text)

    def get_xpath(self, xpath):
        return self.selenium.find_elements(By.XPATH, xpath)

    def select_xpath_by_text(self, xpath, visible_text):
        selector = Select(self.selenium.find_element(By.XPATH, xpath))
        selector.select_by_visible_text(visible_text)


### Parent class from which all selenium test cases will be derived
class SeleniumTestCase(HelperMixin, StaticLiveServerTestCase):
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