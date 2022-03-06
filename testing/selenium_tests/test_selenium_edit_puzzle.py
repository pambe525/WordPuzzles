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

    def test_ADD_CLUE_saves_new_clue_and_redirects_to_puzzle_page(self):
        puzzle_data = {'editor': self.user}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/new_clue/' + str(puzzle.id) + '/')
        self.set_input_xpath("//input[@id='id_answer']", 'MY WORD')
        self.set_input_xpath("//textarea[@id='id_clue_text']", 'Clue for my word')
        self.set_input_xpath("//textarea[@id='id_parsing']", 'Parsing for clue')
        self.click_xpath("//button[text()='SAVE']")
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)

    def test_EDIT_CLUE_redirects_to_edit_clue_page_and_loads_existing_data(self):
        puzzle_data = {'editor': self.user, 'type': 0}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        clue = puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': 'Parsing for clue', 'points': 1})
        self.get('/edit_clue/' + str(puzzle.id) + '/1/')
        self.assert_current_url("/edit_clue/" + str(puzzle.id) + '/1/')
        self.assert_xpath_text("//h3", "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assert_xpath_value("//input[@id='id_answer']",'SECRET')
        self.assert_xpath_value("//textarea[@id='id_clue_text']",'some clue')
        self.assert_xpath_value("//textarea[@id='id_parsing']",'Parsing for clue')
        self.assert_selected_text("//select[@id='id_points']", '1')

    def test_EDIT_CLUE_saves_changes_to_exisitng_clue_and_redirects_to_puzzle_page(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue = puzzle.add_clue({'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': 'Parsing for clue', 'points': 1})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[@href='/edit_clue/"+str(puzzle.id)+"/1/']")
        self.set_input_xpath("//input[@id='id_answer']",' KEY')
        self.set_input_xpath("//textarea[@id='id_clue_text']",'changed clue')
        self.set_input_xpath("//textarea[@id='id_parsing']",'Parsing for clue1')
        self.click_xpath("//button[text()='SAVE']")
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        self.assertEqual(clues[0].answer, 'KEY')
        self.assertEqual(clues[0].clue_text, 'changed clue')
        self.assertEqual(clues[0].parsing, 'Parsing for clue1')
        self.assertEqual(clues[0].points, 1)

    def test_EDIT_PUZZLE_page_lists_all_the_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        clue1 = puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
        clue2 = puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue 2', 'parsing': 'p2', 'points': 2})
        clue3 = puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue 3', 'parsing': 'p3', 'points': 3})
        clue4 = puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue 4', 'parsing': 'p4', 'points': 4})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=puzzle)
        self.assert_xpath_text("//div[contains(text(),'Clues [')]", 'Clues [10 points]')
        answers = self.get_xpath("//div/b")
        clue_nums = self.get_xpath("(//tr/td[1][contains(@class,'text-center')])")
        for index in range(0, len(clues)):
            self.assertEqual(clue_nums[index].text, str(clues[index].clue_num) + '.')
            href = '/edit_clue/' + str(puzzle.id) + '/' + str(clues[index].clue_num) + '/'
            self.assert_xpath_text("//div[@class='text-wrap']/a[@href='"+href+"']", clues[index].clue_text + ' (5)')
            self.assertEqual(answers[index].text, '['+clues[index].answer+']')
            self.assert_xpath_text("//div/span[@title='"+clues[index].parsing+"']", clues[index].parsing)

    def test_Delete_Clue_button_redirects_to_delete_confirmation(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        clue = puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[@href='/delete_clue_confirm/"+str(puzzle.id)+"/1/']")
        self.assert_current_url("/delete_clue_confirm/"+str(puzzle.id)+"/1/")
        self.assert_xpath_text("//h2", "Delete Clue 1 for Puzzle #" + str(puzzle.id))
        self.assert_xpath_contains("//div/div/form/div", "This clue will be permanently deleted.")
        # Cancel redirects back to Dashboard
        self.click_xpath("//a[text()='CANCEL']")
        self.assert_current_url("/edit_puzzle/"+str(puzzle.id)+"/")
        # Make sure the clue still exists
        self.assertEqual(len(Clue.objects.all()), 1)

    def test_Delete_Clue_button_deletes_clue_after_confirmation_and_adjusts_clue_nums(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=1)
        clue1 = puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        clue2 = puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue text 2', 'parsing': 'p2', 'points': 2})
        clue3 = puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue text 3', 'parsing': 'p3', 'points': 3})
        clue4 = puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue text 4', 'parsing': 'p4', 'points': 4})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[@href='/delete_clue_confirm/"+str(puzzle.id)+"/2/']") # Delete clue number 2
        self.click_xpath("//button[text()='DELETE']")
        self.assert_current_url("/edit_puzzle/"+str(puzzle.id)+"/")
        # Veriy remaining clues
        self.assertEqual(len(Clue.objects.filter(puzzle=puzzle, points=2)), 0)
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        clues = Clue.objects.filter(puzzle=puzzle)
        self.assertEqual(len(clues), 3)
        self.assertEqual(puzzle.size, 3)
        self.assertEqual(puzzle.total_points, 8)
        self.assertEqual(clues[0].clue_num, 1)
        self.assertEqual(clues[0].answer, 'WORD1')
        self.assertEqual(clues[1].clue_num, 2)
        self.assertEqual(clues[1].answer, 'WORD3')
        self.assertEqual(clues[2].clue_num, 3)
        self.assertEqual(clues[2].answer, 'WORD4')






