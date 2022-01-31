from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By

class UserAuthTests(LiveServerTestCase):

    selenium = webdriver.Firefox()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_Login(self):
        self.selenium.get(self.live_server_url + '/login')
        self.selenium.implicitly_wait(10)
        username_input = self.selenium.find_element(By.NAME, "btnSignIn")
        self.assertIsNotNone(username_input)
        #username_input.send_keys('myuser')
        ##password_input = self.selenium.find_element_by_name("password")
        #password_input.send_keys('secret')
        #self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()