from django.contrib.auth.models import User

from puzzles.models import WordPuzzle
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class EditPuzzleTests(BaseSeleniumTestCase):
    reset_sequences = True
    user = None
    password = 'secret_key'
    target_page = "/edit_puzzle/"
    PUZZLE_DESC = "(//span[@class='note-text'])[1]"
    PUZZLE_TIMELOG = "//div[@id='timeLog']"
    DONE_BTN = "(//a[@role='button'])[1]"
    EDIT_DESC_BTN = "//button[@id='btnEditDesc']"
    ADD_CLUES_BTN = "//div//a[text()='Add Clues']"
    MODAL_DIALOG_DESC = "//dialog[@id='edit-desc-dialog']"
    DESC_TEXT_AREA = "//dialog//textarea[@id='id_desc']"
    CLOSE_BTN = "//dialog//button[@id='btnClose']"
    MODAL_DIALOG_SAVE = "//dialog//button[@type='submit']"

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)

    def test_loads_puzzle_with_existing_desc_and_done_btn(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some Instructions")
        self.get(self.target_page + str(puzzle.id) + '/')
        self.assert_page_title("Edit Puzzle")
        self.assert_subtitle("Puzzle 1: Non-cryptic Clues")
        self.assert_text_contains(self.PUZZLE_TIMELOG, 'Created by me on')
        self.assert_text_equals(self.PUZZLE_DESC, 'Some Instructions')
        self.assert_text_equals(self.DONE_BTN, "Done")
        # Done btn redirects to My Puzzles page
        self.do_click(self.DONE_BTN)
        self.assert_current_url("/my_puzzles")

    def test_clicking_Edit_desc_btn_shows_modal_dialog_with_cancel(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Some Instructions")
        self.get(self.target_page + str(puzzle.id) + '/')
        self.do_click(self.EDIT_DESC_BTN)
        self.assert_is_displayed(self.MODAL_DIALOG_DESC)
        self.set_input_text(self.DESC_TEXT_AREA, "New instruction")
        self.do_click(self.CLOSE_BTN)
        self.assert_current_url(self.target_page + str(puzzle.id) + '/')
        self.assert_is_not_displayed(self.MODAL_DIALOG_DESC)
        self.assert_text_equals(self.PUZZLE_DESC, "Some Instructions")

    def test_Edit_Desc_modal_dialog_Save_btn_saves_changes(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Initial desc")
        self.get(self.target_page + str(puzzle.id) + '/')
        self.do_click(self.EDIT_DESC_BTN)
        self.set_input_text(self.DESC_TEXT_AREA, "New desc")
        self.do_click(self.MODAL_DIALOG_SAVE)
        self.assert_is_not_displayed(self.MODAL_DIALOG_DESC)
        self.assert_current_url(self.target_page + str(puzzle.id) + '/')
        self.assert_text_equals(self.PUZZLE_DESC, "New desc")
        # Ensure desc is saved when puzzle is reloaded
        self.get(self.target_page + str(puzzle.id) + '/')
        self.assert_text_equals(self.PUZZLE_DESC, "New desc")

    def test_Add_Clues_btn_redirects_to_add_clues_page(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.get(self.target_page + str(puzzle.id) + '/')
        self.do_click(self.ADD_CLUES_BTN)
        self.assert_current_url("/add_clues/" + str(puzzle.id) + '/')
        self.assert_page_title("Add Clues & Answers")
        self.assert_subtitle(str(puzzle))


#     def test_Edit_Puzzle_page_lists_all_the_clues(self):
#         puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
#         puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
#         puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue 2', 'parsing': 'p2', 'points': 2})
#         puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue 3', 'parsing': 'p3', 'points': 3})
#         puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue 4', 'parsing': 'p4', 'points': 4})
#         self.get('/edit_puzzle/' + str(puzzle.id) + '/')
#         clues = Clue.objects.filter(puzzle=puzzle)
#         self.assert_text_equals("//div[contains(text(),'Clues [')]", 'Clues [10 points]')
#         for index in range(0, len(clues)):
#             answer = self.get_element("//div/b", index)
#             clue_num = self.get_element("(//tr/td[1][contains(@class,'text-center')])", index)
#             self.assertEqual(clue_num.text, str(clues[index].clue_num) + '.')
#             href = '/edit_clue/' + str(puzzle.id) + '/' + str(clues[index].clue_num) + '/'
#             self.assert_text_equals("//div[@class='text-wrap']/a[@href='" + href + "']",
#                                     clues[index].clue_text + ' (5)')
#             self.assertEqual(answer.text, '[' + clues[index].answer + ']')
#             self.assert_text_equals("//div/span[@title='" + clues[index].parsing + "']", clues[index].parsing)
#

class AddCluesTests(BaseSeleniumTestCase):
    reset_sequences = True
    user = None
    password = 'secret_key'
    target_page = "/add_clues/"
    CLUES_LABEL = "//form//label[@for='id_clues']"
    CLUES_TEXTAREA = "//form//textarea[@name='clues']"
    ANSWERS_LABEL = "//form//label[@for='id_answers']"
    ANSWERS_TEXTAREA = "//form//textarea[@name='answers']"
    CANCEL_BTN = "//a[text()='Cancel']"
    SUBMIT_BTN = "//button[text()='Submit']"
    ERROR_LIST = ""

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)

    def test_page_has_form_widgets(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.get(self.target_page + str(puzzle.id) + '/')
        self.assert_page_title("Add Clues & Answers")
        self.assert_subtitle(str(puzzle))
        self.assert_text_equals(self.CLUES_LABEL, "Clues:")
        self.assert_text_equals(self.ANSWERS_LABEL, "Answers:")
        self.assert_is_displayed(self.CLUES_TEXTAREA)
        self.assert_is_displayed(self.ANSWERS_TEXTAREA)
        self.assert_is_displayed(self.CANCEL_BTN)
        self.assert_is_displayed(self.SUBMIT_BTN)
        self.do_click(self.CANCEL_BTN)
        self.assert_current_url("/edit_puzzle/" + str(puzzle.id) + '/')

# class EditClueTests(BaseSeleniumTestCase):
#     password = 'secret_key'
#
#     def setUp(self):
#         self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
#         self.auto_login_user(self.user)
#         puzzle_data = {'editor': self.user, 'type': 0, 'desc': 'Instructions'}
#         self.puzzle = WordPuzzle.objects.create(**puzzle_data)
#
#     def test_Add_Clue_button_redirects_to_edit_clue_page_with_new_clue_num(self):
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[text()='ADD CLUE']")
#         self.assert_current_url("/new_clue/" + str(self.puzzle.id) + '/')
#         self.assert_text_equals("//h3", "Edit Clue 1 for Puzzle #" + str(self.puzzle.id))
#         self.assert_attribute_equals("//input[@id='id_answer']", '')
#         self.assert_attribute_equals("//textarea[@id='id_clue_text']", '')
#         self.assert_attribute_equals("//textarea[@id='id_parsing']", '')
#         self.assert_selected_text("//select[@id='id_points']", '1')
#
#     def test_Add_Clue_page_CANCEL_button_redirects_to_edit_puzzle_page(self):
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[text()='ADD CLUE']")
#         self.do_click("//a[text()='CANCEL']")
#         self.assert_current_url('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         clues = Clue.objects.all()
#         self.assertEqual(len(clues), 0)  # No clues created
#
#     def test_Add_Clue_page_save_button_with_blank_form_does_nothing(self):
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[text()='ADD CLUE']")
#         self.do_click("//button[text()='SAVE']")
#         self.assert_current_url('/new_clue/' + str(self.puzzle.id) + '/')
#         clues = Clue.objects.all()
#         self.assertEqual(len(clues), 0)  # No clues created
#
#     def test_Add_Clue_saves_new_clue_and_redirects_to_puzzle_page(self):
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[text()='ADD CLUE']")
#         self.set_input_text("//input[@id='id_answer']", 'MY WORD')
#         self.set_input_text("//textarea[@id='id_clue_text']", 'Clue for my word')
#         self.set_input_text("//textarea[@id='id_parsing']", 'Parsing for clue')
#         self.do_click("//button[text()='SAVE']")
#         self.assert_current_url('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         clues = Clue.objects.all()
#         self.assertEqual(len(clues), 1)
#
#     def test_Edit_Clue_redirects_to_edit_clue_page_and_loads_existing_data(self):
#         self.puzzle.add_clue(
#             {'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': 'Parsing for clue', 'points': 1})
#         self.get('/edit_clue/' + str(self.puzzle.id) + '/1/')
#         self.assert_current_url("/edit_clue/" + str(self.puzzle.id) + '/1/')
#         self.assert_text_equals("//h3", "Edit Clue 1 for Puzzle #" + str(self.puzzle.id))
#         self.assert_attribute_equals("//input[@id='id_answer']", 'SECRET')
#         self.assert_attribute_equals("//textarea[@id='id_clue_text']", 'some clue')
#         self.assert_attribute_equals("//textarea[@id='id_parsing']", 'Parsing for clue')
#         self.assert_selected_text("//select[@id='id_points']", '1')
#
#     def test_Edit_Clue_saves_changes_to_existing_clue_and_redirects_to_puzzle_page(self):
#         self.puzzle.add_clue(
#             {'answer': 'SECRET', 'clue_text': 'some clue', 'parsing': 'Parsing for clue', 'points': 1})
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[@href='/edit_clue/" + str(self.puzzle.id) + "/1/']")
#         self.set_input_text("//input[@id='id_answer']", ' KEY')
#         self.set_input_text("//textarea[@id='id_clue_text']", 'changed clue')
#         self.set_input_text("//textarea[@id='id_parsing']", 'Parsing for clue1')
#         self.do_click("//button[text()='SAVE']")
#         clues = Clue.objects.all()
#         self.assertEqual(len(clues), 1)
#         self.assertEqual(clues[0].answer, 'KEY')
#         self.assertEqual(clues[0].clue_text, 'changed clue')
#         self.assertEqual(clues[0].parsing, 'Parsing for clue1')
#         self.assertEqual(clues[0].points, 1)
#
#
# class DeletePuzzleTests(BaseSeleniumTestCase):
#     password = 'secret_key'
#
#     def setUp(self):
#         self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
#         self.auto_login_user(self.user)
#         self.puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
#
#     def test_Delete_Clue_button_redirects_to_delete_confirmation(self):
#         self.puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[@href='/delete_clue_confirm/" + str(self.puzzle.id) + "/1/']")
#         self.assert_current_url("/delete_clue_confirm/" + str(self.puzzle.id) + "/1/")
#         self.assert_text_equals("//h2", "Delete Clue 1 for Puzzle #" + str(self.puzzle.id))
#         self.assert_text_contains("//div/div/form/div", "This clue will be permanently deleted.")
#
#     def test_Delete_Clue_cancel_redirects_to_Edit_Puzzle_page(self):
#         self.puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue 1', 'parsing': 'p1', 'points': 1})
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[@href='/delete_clue_confirm/" + str(self.puzzle.id) + "/1/']")
#         self.do_click("//a[text()='CANCEL']")
#         self.assert_current_url("/edit_puzzle/" + str(self.puzzle.id) + "/")
#         # Make sure the clue still exists
#         self.assertEqual(len(Clue.objects.all()), 1)
#
#     def test_Delete_Clue_button_deletes_clue_after_confirmation_and_adjusts_clue_nums(self):
#         self.puzzle.type = 1
#         self.puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
#         self.puzzle.add_clue({'answer': 'WORD2', 'clue_text': 'Clue text 2', 'parsing': 'p2', 'points': 2})
#         self.puzzle.add_clue({'answer': 'WORD3', 'clue_text': 'Clue text 3', 'parsing': 'p3', 'points': 3})
#         self.puzzle.add_clue({'answer': 'WORD4', 'clue_text': 'Clue text 4', 'parsing': 'p4', 'points': 4})
#         self.get('/edit_puzzle/' + str(self.puzzle.id) + '/')
#         self.do_click("//a[@href='/delete_clue_confirm/" + str(self.puzzle.id) + "/2/']")  # Delete clue number 2
#         self.do_click("//button[text()='DELETE']")
#         self.assert_current_url("/edit_puzzle/" + str(self.puzzle.id) + "/")
#         # Verify remaining clues
#         self.assertEqual(len(Clue.objects.filter(puzzle=self.puzzle, points=2)), 0)
#         puzzle = WordPuzzle.objects.get(id=self.puzzle.id)
#         clues = Clue.objects.filter(puzzle=self.puzzle)
#         self.assertEqual(len(clues), 3)
#         self.assertEqual(puzzle.size, 3)
#         self.assertEqual(puzzle.total_points, 8)
#         self.assertEqual(clues[0].clue_num, 1)
#         self.assertEqual(clues[0].answer, 'WORD1')
#         self.assertEqual(clues[1].clue_num, 2)
#         self.assertEqual(clues[1].answer, 'WORD3')
#         self.assertEqual(clues[2].clue_num, 3)
#         self.assertEqual(clues[2].answer, 'WORD4')
