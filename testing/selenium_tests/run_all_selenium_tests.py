import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner
from testing.selenium_tests.singleton_webdriver import SingletonWebDriver

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'WordPuzzles.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    singleton_driver = SingletonWebDriver()
    singleton_driver.start_webdriver()
    singleton_driver.is_persistent = True
    failures = test_runner.run_tests(['testing.selenium_tests.test_selenium_dashboard'])
    singleton_driver.active_webdriver.quit()
    sys.exit(bool(failures))
