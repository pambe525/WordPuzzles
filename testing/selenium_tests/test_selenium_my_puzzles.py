from django.contrib.auth.models import User
from puzzles.models import WordPuzzle
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class MyPuzzlesTests(BaseSeleniumTestCase):
    password = 'secretkey'
    target_page = "/my_puzzles"

    DRAFTS_TAB = "//.nav-tabs/li[@id='drafts-tab']"
    SCHEDULED_TAB = "//li[@id='scheduled-tab']"
    PUBLISHED_TAB = "//li[@id='published-tab']"
    ACTIVE_TAB = "//nav[@class='nav-tabs']//li[@class='active']"
    ACTIVE_CONTENT = "//div[contains(@class,'active-tab')]"
    MODAL_DIALOG = "//dialog"
    NEW_PUZZLE_BTN = "//button[@id='btnNewPuzzle']"
    CREATE_PUZZLE_BTN = "//button[@type='submit']"
    CLOSE_BTN = "//button[@id='btnClose']"
    TYPE_FIELD = "//select[@id='id_type']"
    DESC_FIELD = "//textarea[@id='id_desc']"
    EDIT_PUZZLE_PAGE_DESC = "//div[@class='note-text']"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)

    def test_Redirect_to_login_if_user_is_not_authenticated(self):
        self.logout_user()
        self.get(self.target_page)
        self.assert_current_url('/login?next=/my_puzzles')

    def test_Drafts_is_default_active_tab(self):
        self.get(self.target_page)
        self.assert_text_equals(self.ACTIVE_TAB, "Drafts")
        self.assert_text_contains(self.ACTIVE_CONTENT, "My Draft Puzzles")

    def test_Clicking_on_a_tab_activates_tab_content(self):
        self.get(self.target_page)
        self.do_click(self.SCHEDULED_TAB)
        self.assert_text_equals(self.ACTIVE_TAB, "Scheduled")
        self.assert_text_contains(self.ACTIVE_CONTENT, "My Scheduled Puzzles")
        self.do_click(self.PUBLISHED_TAB)
        self.assert_text_equals(self.ACTIVE_TAB, "Published")
        self.assert_text_contains(self.ACTIVE_CONTENT, "My Published Puzzles")

    def test_New_Puzzle_button_activates_dialog_that_can_be_closed(self):
        self.get(self.target_page)
        self.assert_is_not_displayed(self.MODAL_DIALOG)
        self.do_click(self.NEW_PUZZLE_BTN)
        self.assert_is_displayed(self.MODAL_DIALOG)
        self.do_click(self.CLOSE_BTN)
        self.assert_is_not_displayed(self.MODAL_DIALOG)
        self.assert_current_url(self.target_page)

    def test_CreatePuzzle_btn_creates_new_puzzle_and_redirects_to_puzzle_page(self):
        self.get(self.target_page)
        self.do_click(self.NEW_PUZZLE_BTN)
        self.set_input_text(self.DESC_FIELD, "Instructions")
        self.select_by_text(self.TYPE_FIELD, "Non-cryptic Clues")
        self.do_click(self.CREATE_PUZZLE_BTN)
        new_puzzle = WordPuzzle.objects.all()[0]
        self.assert_current_url('/edit_puzzle/' + str(new_puzzle.id) + '/')
        self.assert_subtitle("Puzzle " + str(new_puzzle.id) + ": Non-cryptic Clues")
        self.assert_text_equals(self.EDIT_PUZZLE_PAGE_DESC, "Instructions", )

