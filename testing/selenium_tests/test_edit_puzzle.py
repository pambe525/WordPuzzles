from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from puzzles.models import WordPuzzle

from testing.selenium_tests.helper_mixin import HelperMixin


class EditPuzzleTests(StaticLiveServerTestCase, HelperMixin):
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

    def test_puzzle_edit_page_with_new_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_xpath_exists("//a[text()='DONE']")
        self.assert_xpath_exists("//button[text()='SAVE']")
        self.assert_xpath_exists("//button[text()='PREVIEW']")
        self.assert_xpath_exists("//button[text()='ADD CLUE']")
        #self.assert_xpath_text("//select[@id='id_type']", 'Cryptic Clues')
        self.assert_xpath_text("//input[@id='id_title']", '')
        self.assert_xpath_text("//textarea[@id='id_desc']", '')

    def test_puzzle_edit_page_saves_edited_new_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_selected_text("//select[@id='id_type']", 'Cryptic Clues')
        self.set_input_xpath("//input[@id='id_title']", 'A short title')
        self.set_input_xpath("//textarea[@id='id_desc']",  'Some instructions')
        self.click_xpath("//button[text()='SAVE']")
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_value("//input[@id='id_title']", 'A short title')
        self.assert_xpath_value("//textarea[@id='id_desc']", 'Some instructions')

    def test_puzzle_edit_page_loads_existing_puzzle(self):
        puzzle_data = {'editor': self.user, 'type':0, 'title': "A short tile", 'desc':'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_selected_text("//select[@id='id_type']", 'Non-cryptic Clues')
        self.set_input_xpath("//input[@id='id_title']", 'A short title')
        self.set_input_xpath("//textarea[@id='id_desc']",  'Instructions')
