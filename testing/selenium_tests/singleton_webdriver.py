import atexit

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


class SingletonWebDriver(object):
    _instance = None
    _browser = 'Firefox'

    active_webdriver = None
    is_persistent = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonWebDriver, cls).__new__(cls)
        return cls._instance

    def _create_webdriver(self):
        if self._browser == 'Chrome':
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        elif self._browser == 'Firefox':
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))
        else:
            driver = webdriver.Safari()
        return driver

    def start_webdriver(self):
        if self.active_webdriver is None:
            self.active_webdriver = self._create_webdriver()
        return self.active_webdriver

    def quit_webdriver(self):
        if not self.is_persistent:
            self.active_webdriver.quit()
            self.active_webdriver = None

@atexit.register
def cleanup_driver():
    driver = SingletonWebDriver().active_webdriver
    if driver is not None: driver.quit()