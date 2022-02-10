from selenium import webdriver
from selenium.webdriver.common.by import By
from os import name as os_name

class Helper:

    if os_name == 'nt':
        #webdriver_path = 'C:\\Users\Prashant\Documents\PyCharmProjects\chromedriver.exe'
        #selenium = webdriver.Chrome(executable_path=webdriver_path)
        webdriver_path = 'C:\\Users\Prashant\Documents\PyCharmProjects\geckodriver.exe'
        selenium = webdriver.Firefox(executable_path=webdriver_path)
    else: selenium = webdriver.Chrome()

    def get(self, url):
        self.selenium.get(url)

    def set_input_text(self, input_id, input_text):
        self.selenium.find_element(By.ID, input_id).send_keys(input_text)

    def click_btn(self, btn_id):
        self.selenium.find_element(By.ID, btn_id).click()

    def login_user(self, url, username, password):
        self.selenium.get(url)
        self.set_input_text('id_username', username)
        self.set_input_text('id_password', password)
        self.click_btn('btnSignIn')
