from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from puzzles.models import WordPuzzle, Clue
from testing.selenium_tests.selenium_helper_mixin import HelperMixin


class EditPuzzleTests(StaticLiveServerTestCase, HelperMixin):
    user = None
    password = 'secret_key'

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
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.login_user(username=self.user.username, password=self.password)

    def test_New_Puzzle_creates_puzzle_and_loads_edit_page(self):
        self.get('/new_puzzle')
        puzzle = WordPuzzle.objects.all()[0]
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_selected_text("//select[@id='id_type']", 'Cryptic Clues')
        self.assert_xpath_text("//textarea[@id='id_desc']", '')
        self.assert_xpath_exists("//a[text()='DONE']")
        self.assert_xpath_exists("//button[text()='SAVE']")
        self.assert_xpath_exists("//a[text()='ADD CLUE']")
        self.assert_xpath_exists("//div[text()='Clues [0 points]']")
        self.assert_xpath_exists("//div[text()='No clues exist. Use ADD CLUE to create clues.']")

    def test_Edit_Puzzle_loads_page_with_existing_data(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some Instructions")
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Edit Puzzle #" + str(puzzle.id))
        self.assert_selected_text("//select[@id='id_type']", 'Non-cryptic Clues')
        self.assert_xpath_text("//textarea[@id='id_desc']", 'Some Instructions')
        self.assert_xpath_exists("//a[text()='DONE']")
        self.assert_xpath_exists("//button[text()='SAVE']")
        self.assert_xpath_exists("//a[text()='ADD CLUE']")
        self.assert_xpath_exists("//div[text()='Clues [0 points]']")
        self.assert_xpath_exists("//div[text()='No clues exist. Use ADD CLUE to create clues.']")

    def test_Edit_Puzzle_save_button_updates_puzzle_field(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.set_input_xpath("//textarea[@id='id_desc']", 'New instructions')
        self.click_xpath("//button[text()='SAVE']")
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_value("//textarea[@id='id_desc']", 'New instructions')
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEquals(updated_puzzle.desc, "New instructions")

    def test_Add_Clue_button_redirects_to_edit_clue_page_with_new_clue_num(self):
        puzzle_data = {'editor': self.user, 'type': 0, 'desc': 'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[text()='ADD CLUE']")
        self.assert_current_url("/new_clue/" + str(puzzle.id) + '/')
        self.assert_xpath_text("//h3", "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assert_xpath_value("//input[@id='id_answer']", '')
        self.assert_xpath_value("//textarea[@id='id_clue_text']", '')
        self.assert_xpath_value("//textarea[@id='id_parsing']", '')
        self.assert_selected_text("//select[@id='id_points']", '1')

    def test_Add_Clue_page_CANCEL_button_redirects_to_edit_puzzle_page(self):
        puzzle_data = {'editor': self.user, 'type': 0, 'desc': 'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/new_clue/' + str(puzzle.id) + '/')
        self.click_xpath("//a[text()='CANCEL']")
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 0)  # No clues created

    def test_Add_Clue_page_save_button_with_blank_form_does_nothing(self):
        puzzle_data = {'editor': self.user, 'type': 0, 'desc': 'Instructions'}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.get('/new_clue/' + str(puzzle.id) + '/')
        self.click_xpath("//button[text()='SAVE']")
        self.assert_current_url('/new_clue/' + str(puzzle.id) + '/')
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 0)  # No clues created

    def test_Add_Clue_saves_new_clue_and_redirects_to_puzzle_page(self):
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

    def test_Edit_Clue_redirects_to_edit_clue_page_and_loads_existing_data(self):
        puzzle_data = {'editor': self.user, 'type': 0}
        puzzle = WordPuzzle.objects.create(**puzzle_data)
        puzzle.add_clue(
            {'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': 'Parsing for clue', 'points': 1})
        self.get('/edit_clue/' + str(puzzle.id) + '/1/')
        self.assert_current_url("/edit_clue/" + str(puzzle.id) + '/1/')
        self.assert_xpath_text("//h3", "Edit Clue 1 for Puzzle #" + str(puzzle.id))
        self.assert_xpath_value("//input[@id='id_answer']", 'SECRET')
        self.assert_xpath_value("//textarea[@id='id_clue_text']", 'some clue')
        self.assert_xpath_value("//textarea[@id='id_parsing']", 'Parsing for clue')
        self.assert_selected_text("//select[@id='id_points']", '1')

    def test_Edit_Clue_saves_changes_to_existing_clue_and_redirects_to_puzzle_page(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue(
            {'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': 'Parsing for clue', 'points': 1})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[@href='/edit_clue/" + str(puzzle.id) + "/1/']")
        self.set_input_xpath("//input[@id='id_answer']", ' KEY')
        self.set_input_xpath("//textarea[@id='id_clue_text']", 'changed clue')
        self.set_input_xpath("//textarea[@id='id_parsing']", 'Parsing for clue1')
        self.click_xpath("//button[text()='SAVE']")
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        self.assertEqual(clues[0].answer, 'KEY')
        self.assertEqual(clues[0].clue_text, 'changed clue')
        self.assertEqual(clues[0].parsing, 'Parsing for clue1')
        self.assertEqual(clues[0].points, 1)

    def test_Edit_Puzzle_page_lists_all_the_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
        puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue 2', 'parsing': 'p2', 'points': 2})
        puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue 3', 'parsing': 'p3', 'points': 3})
        puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue 4', 'parsing': 'p4', 'points': 4})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=puzzle)
        self.assert_xpath_text("//div[contains(text(),'Clues [')]", 'Clues [10 points]')
        answers = self.get_xpath("//div/b")
        clue_nums = self.get_xpath("(//tr/td[1][contains(@class,'text-center')])")
        for index in range(0, len(clues)):
            self.assertEqual(clue_nums[index].text, str(clues[index].clue_num) + '.')
            href = '/edit_clue/' + str(puzzle.id) + '/' + str(clues[index].clue_num) + '/'
            self.assert_xpath_text("//div[@class='text-wrap']/a[@href='" + href + "']", clues[index].clue_text + ' (5)')
            self.assertEqual(answers[index].text, '[' + clues[index].answer + ']')
            self.assert_xpath_text("//div/span[@title='" + clues[index].parsing + "']", clues[index].parsing)

    def test_Delete_Clue_button_redirects_to_delete_confirmation(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[@href='/delete_clue_confirm/" + str(puzzle.id) + "/1/']")
        self.assert_current_url("/delete_clue_confirm/" + str(puzzle.id) + "/1/")
        self.assert_xpath_text("//h2", "Delete Clue 1 for Puzzle #" + str(puzzle.id))
        self.assert_xpath_contains("//div/div/form/div", "This clue will be permanently deleted.")
        # Cancel redirects back to Dashboard
        self.click_xpath("//a[text()='CANCEL']")
        self.assert_current_url("/edit_puzzle/" + str(puzzle.id) + "/")
        # Make sure the clue still exists
        self.assertEqual(len(Clue.objects.all()), 1)

    def test_Delete_Clue_button_deletes_clue_after_confirmation_and_adjusts_clue_nums(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=1)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue text 2', 'parsing': 'p2', 'points': 2})
        puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue text 3', 'parsing': 'p3', 'points': 3})
        puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue text 4', 'parsing': 'p4', 'points': 4})
        self.get('/edit_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[@href='/delete_clue_confirm/" + str(puzzle.id) + "/2/']")  # Delete clue number 2
        self.click_xpath("//button[text()='DELETE']")
        self.assert_current_url("/edit_puzzle/" + str(puzzle.id) + "/")
        # Verify remaining clues
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

    def test_Preview_Puzzle_page_with_no_desc_and_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Preview Puzzle #" + str(puzzle.id))
        self.assert_xpath_exists("//a[text()='DONE']")
        self.assert_xpath_not_exists("//a[text()='PUBLISH']")    # No Publish button
        self.assert_xpath_not_exists("//a[text()='UNPUBLISH']")  # No Unpublish button
        self.assert_xpath_exists("//input[@type='checkbox']")
        self.assert_xpath_text("//label", "Show answers")
        self.assert_xpath_text("//h5", str(puzzle))
        self.assert_xpath_exists("//h6[text()='Posted by: test_user']")
        self.assert_xpath_not_exists("//h6[contains(text, 'Description')]")  # No description
        self.assert_xpath_text("//div[contains(@class,'notetext')]", "No clues exist.")

    def test_Preview_Puzzle_page_with_desc_and_clue(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//h2", "Preview Puzzle #" + str(puzzle.id))
        self.assert_xpath_exists("//a[text()='DONE']")
        self.assert_xpath_exists("//a[text()='PUBLISH']")        # Publish button
        self.assert_xpath_not_exists("//a[text()='UNPUBLISH']")  # No Unpublish button
        self.assert_xpath_text("//h5", str(puzzle))
        self.assert_xpath_exists("//h6[text()='Description: Some description']")  # No description
        self.assert_xpath_not_exists("//div[text()='No clues exist.']")

    def test_Preview_Puzzle_page_publish_button_publishes_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//a[text()='PUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNotNone(updated_puzzle.shared_at)
        self.assert_current_url('/')

    def test_Preview_Puzzle_page_unpublish_button_unpublishes_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        self.get('/publish_puzzle/' + str(puzzle.id) + '/')
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_not_exists("//a[text()='PUBLISH']")
        self.click_xpath("//a[text()='UNPUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)
        self.assert_current_url('/')

        #TODO: Add test to exclude Preview for Published editing permission in django unit tests