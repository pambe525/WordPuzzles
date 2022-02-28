from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from puzzles.models import WordPuzzle

from testing.selenium_tests.selenium_helper_mixin import HelperMixin


class DashboardTests(StaticLiveServerTestCase, HelperMixin):
    user = None
    password = 'secretkey'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.server_url = cls.live_server_url
        cls.selenium = super().get_webdriver(cls, 'Firefox')
        cls.testcase = cls

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.login_user(username=self.user.username, password=self.password)

    def test_Unpopulated_dasboard(self):
        self.get('/')
        self.assert_xpath_items("//h3", 2)
        self.assert_xpath_text("//h3", "Recent Puzzles", 0)
        self.assert_xpath_text("//h3", "My Draft Puzzles", 1)
        self.assert_xpath_items("//div[contains(@class, 'notetext')]", 2)
        self.assert_xpath_contains("//div[contains(@class, 'notetext')]", "No puzzles have been posted", 0)
        self.assert_xpath_contains("//div[contains(@class, 'notetext')]", "no draft puzzles", 1)

    def test_New_Puzzle_button_creates_puzzle_and_badge_for_puzzle(self):
        self.get('/')
        self.click_btn('btnNewPuzzle')
        # Creates puzzle and redirects to edit puzzle page
        puzzle_id = WordPuzzle.objects.all()[0].id
        self.assert_current_url('/edit_puzzle/' + str(puzzle_id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle_id))
        # Find and click DONE btn on edit puzzle page
        self.click_xpath("//a[text()='DONE']")
        # Redirects to dashboard and displays new puzzle badge
        self.assert_current_url('/')
        self.assert_xpath_items("//div[contains(@class,'badge badge')]", 1)
        badge_header =  "Puzzle #" + str(puzzle_id) + ": 0 Cryptic Clues [0 points]"
        self.assert_xpath_text("//div[contains(@class,'badge badge')]/a", badge_header)

    def test_Puzzle_badge_header_link_redirects_to_edit_puzzle_page(self):
        self.get('/')
        # Create a new puzzle
        self.click_btn('btnNewPuzzle')
        self.click_xpath("//a[text()='DONE']")
        # Click on edit puzzle icon in new puzzle badge
        self.click_xpath("//div/a[@class='h5']")
        # Edit puzzle page
        puzzle_id = WordPuzzle.objects.all()[0].id
        self.assert_current_url('/edit_puzzle/' + str(puzzle_id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle_id))

    def test_Delete_Puzzle_button_redirects_to_delete_confirmation(self):
        self.get('/')
        # Create a new puzzle
        self.click_btn('btnNewPuzzle')
        self.click_xpath("//a[text()='DONE']")  # DONE btn on edit_puzzle page
        self.assert_current_url('/')
        self.assert_xpath_items("//div[contains(@class,'badge badge')]", 1)
        # Click on delete puzzle icon in new puzzle badge
        self.click_xpath("//a[@title='Delete']") # DELETE icon on dashboard page
        # Delete puzzle page
        puzzle_id = WordPuzzle.objects.all()[0].id
        self.assert_current_url('/delete_puzzle_confirm/' + str(puzzle_id) + '/')
        self.assert_xpath_text("//h2", "Delete Puzzle #" + str(puzzle_id))
        # Cancel redirects back to Dashboard
        self.click_xpath("//a[text()='CANCEL']")
        self.assert_current_url('/')
        # Make sure the puzzle still exists
        self.assert_xpath_items("//div[contains(@class,'badge badge')]", 1)
        badge_header =  "Puzzle #" + str(puzzle_id) + ": 0 Cryptic Clues [0 points]"
        self.assert_xpath_text("//div[contains(@class,'badge badge')]/a", badge_header)

    def test_Delete_Puzzle_button_deletes_puzzle_after_confirmation(self):
        self.get('/')
        self.click_btn('btnNewPuzzle')
        self.click_xpath("//a[text()='DONE']")  # DONE btn on edit_puzzle page
        self.click_xpath("//a[@title='Delete']") # DELETE icon on dashboard page
        puzzle_id = WordPuzzle.objects.all()[0].id
        self.click_xpath("//a[text()='DELETE']")
        # Make sure the puzzle does not exist
        self.assert_xpath_items("//div[contains(@class,'badge badge')]", 0)
