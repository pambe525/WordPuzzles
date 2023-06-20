from django.contrib.auth.models import User

from puzzles.models import WordPuzzle, Clue
from testing.data_setup_utils import add_clue
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class EditPuzzleTests(BaseSeleniumTestCase):
    reset_sequences = True
    user = None
    password = 'secret_key'
    target_page = "/edit_puzzle/"
    PUZZLE_DESC = "//div[contains(@class,'boxed-panel')]//span[contains(@class,'note-text')]"
    PUZZLE_TIMELOG = "//div[@id='timeLog']"
    DONE_BTN = "//div//i[contains(@class,'fa-circle-xmark')]"
    EDIT_DESC_BTN = "//button[@id='btnEditDesc']"
    ADD_CLUES_BTN = "//div//a[text()='Add Clues']"
    MODAL_DIALOG_DESC = "//dialog[@id='edit-desc-dialog']"
    DESC_TEXT_AREA = "//dialog//textarea[@id='id_desc']"
    CLOSE_BTN = "//dialog//button[@id='btnClose']"
    MODAL_DIALOG_SAVE = "//dialog//button[@type='submit']"
    CLUE_NUM_CELL = "(//tr//td[contains(@class,'clue-num')])"
    CLUE_TEXT_CELL = "(//tr//td/a[contains(@class,'clue-text')])"
    ANSWER_CELL = "(//tr//td/div[contains(@class,'answer')])"
    POINTS_CELL = "(//tr//td[contains(@class,'points')])"
    DELETE_BTN_CELL = "//tr//td/a[contains(@class,'delete-btn')]"
    CONFIRM_DIALOG = "//dialog[@id='confirm-dialog']"
    CONFIRM_DIALOG_SUBTITLE = "//dialog[@id='confirm-dialog']/div[@class='subtitle']"
    CONFIRM_DIALOG_MSG = "//dialog[@id='confirm-dialog']//div[contains(@class,'confirm-dialog-message')]"
    CONFIRM_DIALOG_CLOSE_BTN = "//dialog[@id='confirm-dialog']//button[@id='btnClose']"
    CONFIRM_DIALOG_SUBMIT_BTN = "//dialog[@id='confirm-dialog']//button[@type='submit']"

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)

    def test_loads_puzzle_with_existing_desc_and_done_btn(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some Instructions")
        self.get(self.target_page + str(puzzle.id) + '/')
        self.assert_page_title("Edit Puzzle")
        self.assert_subtitle(str(puzzle))
        self.assert_text_contains(self.PUZZLE_TIMELOG, 'Created by me on')
        self.assert_text_equals(self.PUZZLE_DESC, 'Some Instructions')
        self.do_click(self.DONE_BTN)
        self.assert_current_url('/')

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

    def test_clues_list_details(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        add_clue(puzzle, {'answer': 'word one', 'clue_text': 'Clue 1 (4,3)', 'points': 1})
        add_clue(puzzle, {'answer': 'word two', 'clue_text': 'Clue 2 (4,3)', 'points': 1})
        add_clue(puzzle, {'answer': 'word three', 'clue_text': 'Clue 3 (4,5)', 'points': 1})
        add_clue(puzzle, {'answer': 'word four', 'clue_text': 'Clue 4 (4,4)', 'points': 1})
        self.get(self.target_page + str(puzzle.id) + '/')
        self.assert_subtitle(str(puzzle))
        clues = Clue.objects.filter(puzzle=puzzle)
        for index in range(0, len(clues)):
            self.assert_text_equals(self.CLUE_NUM_CELL, str(clues[index].clue_num) + '.', index)
            self.assert_text_equals(self.CLUE_TEXT_CELL, str(clues[index].clue_text), index)
            self.assert_text_equals(self.ANSWER_CELL, "Answer: " + str(clues[index].answer).upper(), index)
            self.assert_text_equals(self.POINTS_CELL, str(clues[index].points), index)
            self.assert_exists(self.DELETE_BTN_CELL)

    def test_list_clue_text_appends_answer_length_if_not_specified(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        add_clue(puzzle, {'answer': 'word one', 'clue_text': 'Clue 1', 'points': 1})
        self.get(self.target_page + str(puzzle.id) + '/')
        clue = Clue.objects.filter(puzzle=puzzle)[0]
        self.assert_text_equals(self.CLUE_TEXT_CELL, str(clue.clue_text) + " (4,3)")

    def test_clue_text_links_to_edit_clue_page(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        add_clue(puzzle, {'answer': 'word one', 'clue_text': 'Clue 1', 'points': 1})
        add_clue(puzzle, {'answer': 'word two', 'clue_text': 'Clue 2', 'points': 1})
        self.get(self.target_page + str(puzzle.id) + '/')
        self.do_click(self.CLUE_TEXT_CELL, 1)
        self.assert_current_url("/edit_clue/1/2/")

    def test_clue_delete_btn_pops_up_confirmation_dialog(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        add_clue(puzzle, {'answer': 'word one', 'clue_text': 'Clue 1', 'points': 1})
        self.get(self.target_page + str(puzzle.id) + '/')
        self.do_click(self.DELETE_BTN_CELL)
        self.assertTrue(self.modal_dialog_open("confirm-dialog"))
        # Validate confirm dialog contents
        self.assert_text_equals(self.CONFIRM_DIALOG_SUBTITLE, "Delete Clue #1 for Puzzle 1")
        self.assert_text_contains(self.CONFIRM_DIALOG_MSG, "This clue will be permanently")
        self.assert_text_equals(self.CONFIRM_DIALOG_CLOSE_BTN, "Cancel")
        self.do_click(self.CONFIRM_DIALOG_CLOSE_BTN)
        self.assertFalse(self.modal_dialog_open("confirm-dialog"))
        self.assert_current_url(self.target_page + str(puzzle.id) + "/")

    def test_clue_delete_confirm_deletes_clue_and_updates_clues_list(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        add_clue(puzzle, {'answer': 'word one', 'clue_text': 'Clue one', 'points': 1})
        add_clue(puzzle, {'answer': 'word two', 'clue_text': 'Clue two', 'points': 1})
        self.get(self.target_page + str(puzzle.id) + '/')
        self.assert_item_count(self.CLUE_TEXT_CELL, 2)
        self.do_click(self.DELETE_BTN_CELL, 1)
        self.assertTrue(self.modal_dialog_open("confirm-dialog"))
        self.do_click(self.CONFIRM_DIALOG_SUBMIT_BTN)
        self.assertFalse(self.modal_dialog_open("confirm-dialog"))
        self.assert_current_url(self.target_page + str(puzzle.id) + "/")
        self.assert_item_count(self.CLUE_TEXT_CELL, 1)


class AddCluesTests(BaseSeleniumTestCase):
    reset_sequences = True
    user = None
    password = 'secret_key'
    target_page = "/add_clues/"
    CLUES_LABEL = "//form//label[@for='id_clues']"
    CLUES_TEXTAREA = "//form//textarea[@id='id_clues']"
    ANSWERS_LABEL = "//form//label[@for='id_answers']"
    ANSWERS_TEXTAREA = "//form//textarea[@id='id_answers']"
    CANCEL_BTN = "//a[text()='Cancel']"
    SUBMIT_BTN = "//button[text()='Submit']"
    CLUES_ERROR_LIST = "//form/ul[@class='errorlist'][0]/li"
    ANSWERS_ERROR_LIST = "//form/ul[@class='errorlist'][1]/li"
    CLUE_TEXT_CELL = "(//tr//td/a[contains(@class,'clue-text')])"

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

    def test_incorrect_input_displays_form_errors(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.get(self.target_page + str(puzzle.id) + '/')
        clues_input = "1. clue one\n2 clue two"
        answers_input = "1. answer\n3.missing two"
        self.set_input_text(self.CLUES_TEXTAREA, clues_input)
        self.set_input_text(self.ANSWERS_TEXTAREA, answers_input)
        self.do_click(self.SUBMIT_BTN)
        self.assert_text_equals(self.ANSWERS_ERROR_LIST, '#3 has no matching cross-entry.')

    def test_correct_input_submits_clues_and_updates_clues_list(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.get(self.target_page + str(puzzle.id) + '/')
        clues_input = "1. clue one\n2 clue two"
        answers_input = "1. answer\n2.answer two"
        self.set_input_text(self.CLUES_TEXTAREA, clues_input)
        self.set_input_text(self.ANSWERS_TEXTAREA, answers_input)
        self.do_click(self.SUBMIT_BTN)
        self.assert_current_url("/edit_puzzle/1/")
        self.assert_item_count(self.CLUE_TEXT_CELL, 2)


class EditClueTests(BaseSeleniumTestCase):
    password = 'secret_key'
    target_page = "/edit_clue/"
    CLUE_TEXT_FIELD = "//form//textarea[@id='id_clue_text']"
    ANSWER_FIELD = "//form//input[@id='id_answer']"
    PARSING_FIELD = "//form//textarea[@id='id_parsing']"
    POINTS_FIELD = "//form//select[@id='id_points']"
    CANCEL_BTN = "//a[@id='btnCancel']"
    SUBMIT_BTN = "//button[@id='btnSubmit']"
    LIST_CLUE_TEXT_CELL = "(//tr//td/a[contains(@class,'clue-text')])"
    LIST_ANSWER_CELL = "(//tr//td/div[contains(@class,'answer')])"
    ERROR_LIST = "//form//ul[@class='errorlist']/li"

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)
        puzzle_data = {'editor': self.user, 'type': 0, 'desc': 'Instructions'}
        self.puzzle = WordPuzzle.objects.create(**puzzle_data)
        self.clue = add_clue(self.puzzle, {'answer': 'word one', 'clue_text': 'Clue one', 'points': 1})

    def test_form_is_loaded_with_clue_data_and_can_be_canceled(self):
        url = self.target_page + str(self.puzzle.id) + '/' + str(self.clue.clue_num) + "/"
        self.get(url)
        title_string = "Edit Clue #" + str(self.clue.clue_num) + " for Puzzle " + str(self.puzzle.id)
        self.assert_page_title(title_string)
        self.assert_text_equals(self.CLUE_TEXT_FIELD, self.clue.clue_text)
        self.assert_attribute_equals(self.ANSWER_FIELD, 'value', self.clue.answer)
        self.assert_text_equals(self.PARSING_FIELD, '')
        self.assert_selected_text(self.POINTS_FIELD, str(self.clue.points))
        self.do_click(self.CANCEL_BTN)
        self.assert_current_url("/edit_puzzle/" + str(self.puzzle.id) + "/")
        self.assert_item_count(self.LIST_CLUE_TEXT_CELL, 1)

    def test_form_submitted_with_invalid_input_shows_error(self):
        url = self.target_page + str(self.puzzle.id) + '/' + str(self.clue.clue_num) + "/"
        self.get(url)
        self.set_input_text(self.ANSWER_FIELD, 'bad_answer')
        self.do_click(self.SUBMIT_BTN)
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        self.assert_current_url(url)
        self.assert_text_equals(self.ERROR_LIST, "Answer cannot contain non-alphabet characters")

    def test_form_submitted_with_valid_input_updates_clue(self):
        url = self.target_page + str(self.puzzle.id) + '/' + str(self.clue.clue_num) + "/"
        self.get(url)
        self.set_input_text(self.CLUE_TEXT_FIELD, 'Modified clue text')
        self.set_input_text(self.ANSWER_FIELD, 'good answer')  # answer updated
        self.do_click(self.SUBMIT_BTN)
        clues = Clue.objects.all()
        self.assertEqual(len(clues), 1)
        self.assert_current_url('/edit_puzzle/' + str(self.puzzle.id) + "/")
        self.assert_text_equals(self.LIST_CLUE_TEXT_CELL, 'Modified clue text (4,6)')
        self.assert_text_equals(self.LIST_ANSWER_CELL, 'Answer: GOOD ANSWER')
