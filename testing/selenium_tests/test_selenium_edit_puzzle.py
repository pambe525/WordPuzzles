from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.common.by import By
from puzzles.models import WordPuzzle, Clue

from testing.selenium_tests.selenium_helper_mixin import HelperMixin


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
        self.assert_xpath_exists("//a[text()='PREVIEW']")
        self.assert_xpath_exists("//a[text()='ADD CLUE']")
        self.assert_selected_text("//select[@id='id_type']", 'Cryptic Clues')
        self.assert_xpath_text("//textarea[@id='id_desc']", '')

    def test_puzzle_edit_page_saves_edited_new_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_selected_text("//select[@id='id_type']", 'Cryptic Clues')
        self.set_input_xpath("//textarea[@id='id_desc']",  'Some instructions')
        self.click_xpath("//button[text()='SAVE']")
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_value("//textarea[@id='id_desc']", 'Some instructions')

    def test_puzzle_edit_page_loads_existing_puzzle(self):
        puzzle_data = {'editor': self.user, 'type':0, 'desc':'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_selected_text("//select[@id='id_type']", 'Non-cryptic Clues')
        self.set_input_xpath("//textarea[@id='id_desc']",  'Instructions')
        # Check Clues headers - no existing clues
        self.assert_xpath_exists("//div[text()='Clues [0 points]']")

    def test_ADD_CLUE_redirects_to_edit_clue_page(self):
        puzzle_data = {'editor': self.user, 'type':0, 'desc':'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[text()='ADD CLUE']")
        self.assert_current_url("/new_clue/" + str(puzzle.id) + '/')
        self.assert_xpath_text("//h3", "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assert_xpath_value("//input[@id='id_answer']",'')
        self.assert_xpath_value("//textarea[@id='id_clue_text']",'')
        self.assert_xpath_value("//textarea[@id='id_parsing']",'')
        self.assert_selected_text("//select[@id='id_points']", '1')

    def test_ADD_CLUE_page_CANCEL_button_redirects_to_edit_puzzle_page(self):
        puzzle_data = {'editor': self.user, 'type':0, 'desc':'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/new_clue/' + str(puzzle.id) + '/')
        self.click_xpath("//a[text()='CANCEL']")
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 0)   # No clues created

    def test_ADD_CLUE_page_SAVE_button_with_blank_form_does_nothing(self):
        puzzle_data = {'editor': self.user, 'type':0, 'desc':'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/new_clue/' + str(puzzle.id) + '/')
        self.click_xpath("//button[text()='SAVE']")
        self.assert_current_url('/new_clue/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 0)   # No clues created
