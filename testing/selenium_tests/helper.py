from selenium import webdriver
from selenium.webdriver.common.by import By


class Helper():
    selenium = webdriver.Chrome()

    def set_input_text(self, input_id, input_text):
        self.selenium.find_element(By.ID, input_id).send_keys(input_text)

    def click_btn(self, btn_id):
        self.selenium.find_element(By.ID, btn_id).click()

    def login_user(self, url, username, password):
        self.selenium.get(url)
        self.set_input_text('id_username', username)
        self.set_input_text('id_password', password)
        self.click_btn('btnSignIn')
