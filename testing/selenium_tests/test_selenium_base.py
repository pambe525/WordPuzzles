from django.contrib.auth.models import User

from puzzles.models import WordPuzzle
from testing.data_setup_utils import create_published_puzzle, create_user, create_session
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class BaseTemplateTests(BaseSeleniumTestCase):
    password = 'secretkey'

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)

    def test_Unauthenticated_page_has_no_menu_and_username(self):
        self.get('/')
        self.set_mobile_size(False)    # In wide mode
        self.assert_not_exists(self.SPAN_USERNAME)
        self.assert_not_exists(self.NAV_MENU)
        self.set_mobile_size(True)     # In mobile mode
        self.assert_not_exists(self.SPAN_USERNAME)
        self.assert_not_exists(self.NAV_MENU)

    def test_Authenticated_page_displays_username(self):
        self.auto_login_user(self.user)
        self.get('/')
        self.set_mobile_size(False)    # In wide mode
        self.assert_text_equals(self.SPAN_USERNAME, self.user.username)
        self.set_mobile_size(True)     # In mobile mode
        self.assert_text_equals(self.SPAN_USERNAME, self.user.username)

    def test_Authenticated_page_displays_menu_in_wide_mode(self):
        self.auto_login_user(self.user)
        self.get('/')
        self.set_mobile_size(False)    # In wide mode
        self.assert_exists(self.NAV_MENU)
        self.assert_is_not_displayed(self.MENU_TOGGLE)

    def test_Authenticated_page_displays_menu_toggle_in_mobile_mode(self):
        self.auto_login_user(self.user)
        self.set_mobile_size(True)    # In mobile mode
        self.get('/')
        self.assert_is_displayed(self.MENU_TOGGLE)
        self.selenium.implicitly_wait(2)
        nav_menu = self.get_element(self.NAV_MENU)
        self.assertLess(nav_menu.location['x'], 0)   # Out of viewport

    def test_Menu_toggle_click_displays_menu_in_mobile_mode(self):
        self.auto_login_user(self.user)
        self.set_mobile_size(True)    # In mobile mode
        self.get('/')
        self.do_click(self.MENU_TOGGLE)
        self.selenium.implicitly_wait(1000)
        nav_menu = self.get_element(self.NAV_MENU)
        self.assertEquals(nav_menu.location['x'], 0)  # Out of viewport


