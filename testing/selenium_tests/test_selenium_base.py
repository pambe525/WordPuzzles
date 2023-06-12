from django.contrib.auth.models import User

from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class BaseTemplateTests(BaseSeleniumTestCase):
    password = 'secretkey'

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)

    def test_Unauthenticated_page_has_no_menu_and_username(self):
        self.logout_user()
        self.set_mobile_size(False)  # In wide mode
        self.get('/')
        self.assert_not_exists(self.SPAN_USERNAME)
        self.assert_not_exists(self.NAV_MENU)
        self.set_mobile_size(True)  # In mobile mode
        self.assert_not_exists(self.SPAN_USERNAME)
        self.assert_not_exists(self.NAV_MENU)

    def test_Authenticated_page_displays_username(self):
        self.get('/')
        self.set_mobile_size(False)  # In wide mode
        self.assert_text_equals(self.SPAN_USERNAME, self.user.username)
        self.set_mobile_size(True)  # In mobile mode
        self.assert_text_equals(self.SPAN_USERNAME, self.user.username)

    def test_Authenticated_page_displays_menu_in_wide_mode(self):
        self.get('/')
        self.set_mobile_size(False)  # In wide mode
        self.assert_exists(self.NAV_MENU)
        self.assert_is_not_displayed(self.MENU_TOGGLE)

    def test_Authenticated_page_displays_menu_toggle_in_mobile_mode(self):
        self.set_mobile_size(True)  # In mobile mode
        self.get('/')
        self.assert_is_displayed(self.MENU_TOGGLE)
        self.assertFalse(self.do_click(self.MENUITEM_HOME))

    def test_Menu_toggle_click_displays_menu_in_mobile_mode(self):
        self.set_mobile_size(True)  # In mobile mode
        self.get('/')
        self.do_click(self.MENU_TOGGLE)
        self.selenium.implicitly_wait(1)
        self.assertTrue(self.do_click(self.MENUITEM_HOME))

    def test_Clicking_on_logo_in_authenticated_mode_redirects_to_home_page(self):
        self.get('/account')
        self.assert_page_title("Account Settings")
        self.do_click(self.LOGO)
        self.assert_page_title("Dashboard")

    def test_Nav_link_is_hilited_for_active_page(self):
        self.assert_active_page_nav_link_hilited("/", "Dashboard")
        self.assert_active_page_nav_link_hilited("/account", "Account Settings")
        self.assert_active_page_nav_link_hilited("/change_password", "Change Password")
        self.assert_active_page_nav_link_hilited("/release_notes", "Release Notes")
        self.assert_active_page_nav_link_hilited("/my_puzzles", "My Puzzles")
