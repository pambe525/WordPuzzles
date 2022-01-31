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

    def test_SignUp_with_invalid_input_displays_errors(self):
        self.selenium.get(self.live_server_url + '/signup')
        username_input = self.selenium.find_element(By.ID, "id_username")
        password1_input = self.selenium.find_element(By.ID, "id_password1")
        password2_input = self.selenium.find_element(By.ID, "id_password2")
        email_input = self.selenium.find_element(By.ID, "id_email")
        signin_btn = self.selenium.find_element(By.NAME, "btnSignUp")
        #username_input.send_keys('myuser')
        ##password_input = self.selenium.find_element_by_name("password")
        #password_input.send_keys('secret')
        #self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()

    def __enterInput(self, input_id, text):
        self.selenium.find_element(By.ID, input_id).send_keys(text)