import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

os.environ['DJANGO_SETTINGS_MODULE'] = 'WordPuzzles.settings'
django.setup()

from testing.selenium_tests.selenium_helper_mixin import SingletonWebDriver

if __name__ == "__main__":
#    os.environ['DJANGO_SETTINGS_MODULE'] = 'WordPuzzles.settings'
#    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    webdriver = SingletonWebDriver()
    webdriver.start_webdriver()
    webdriver.is_persistent = True
    failures = test_runner.run_tests(['testing.selenium_tests'])
    webdriver.webdriver.quit()
    sys.exit(bool(failures))