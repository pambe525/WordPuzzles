import time
from unittest.case import skip

from puzzles.models import PuzzleSession, Clue
from testing.data_setup_utils import create_published_puzzle, create_session, create_user
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


# ======================================================================================================================
# HELPER FUNCTIONS FOR SolveSession Test Cases cast as a derived class (of SeleneiumTestCase
# Test cases for Solve Session should derive from this class.
class SolveSessionTestCaseHelper(BaseSeleniumTestCase):
    MODAL_DIALOG = "//div[@id='id-modal-answer-box']"
    ANSWER_INPUT = "//div[@id='id-modal-answer-box']//div[@id='id-answer']/input"
    FINISH_LATER_BTN = "//a[@id='id-finish-later-btn']"
    COMPLETED = "//div[@id='id-completed']"
    REVEAL_BTN = "//div[@class='modal-footer']/button[@id='id-reveal-btn']"
    SUBMIT_BTN = "//div[@class='modal-footer']/button[@id='id-submit-btn']"
    CLEAR_BTN = "//div[@class='modal-footer']/button[@id='id-clear-btn']"
    ERR_MSG = "//div[@class='modal-body']//div[@id='id-err-msg']"
    SCORES = "//a[text()='SCORES']"
    CLUE_TEXT = "//div[@id='id-clue-text']"
    MODAL_TITLE = "//h4[@class='modal-title']"

    def set_answer_input(self, input_text):
        answer_input = self.get_element(self.ANSWER_INPUT)
        answer_input.click()
        answer_input.send_keys(input_text)

    @staticmethod
    def get_table_row_xpath(row_num):
        return "//table/tbody/tr[" + str(row_num) + "]/"

    @staticmethod
    def get_state_of_clue(clue, session):
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        clue_state = "UNSOLVED"
        if clue.clue_num in solved_clues:
            clue_state = 'SOLVED'
        elif clue.clue_num in revealed_clues:
            clue_state = 'REVEALED'
        return clue_state

    def get_active_element(self):
        return self.selenium.switch_to.active_element

    def click_on_clue(self, clue_num):
        tr_xpath = self.get_table_row_xpath(clue_num)
        self.do_click(tr_xpath + "td[3]")

    def verify_clue_state_icon(self, clue, clue_state):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        if clue_state == 'SOLVED':
            self.assert_exists(tr_xpath + "td[1]/i[@class='fa fa-check-circle text-success']")
        elif clue_state == 'REVEALED':
            self.assert_exists(tr_xpath + "td[1]/i[@class='fa fa-eye']")
        else:
            self.assert_not_exists(tr_xpath + "td[1]/i[@class='fa fa-check-circle text-success']")
            self.assert_not_exists(tr_xpath + "td[1]/i[@class='fa fa-eye']")
            self.assert_text_equals(tr_xpath + "td[1]", "")

    def verify_clue_points_by_state(self, clue, clue_state):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        if clue_state == 'SOLVED':
            self.assert_not_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
            self.assert_text_equals(tr_xpath + "td[4]", str(clue.points))
        elif clue_state == 'REVEALED':
            self.assert_not_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
            self.assert_text_equals(tr_xpath + "td[4]", '0')
        else:
            self.assert_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
            self.assert_text_equals(tr_xpath + "td[4]", "")

    def verify_clue_text_color_by_state(self, clue, clue_state):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        if clue_state == 'SOLVED' or clue_state == 'REVEALED':
            self.assert_exists(tr_xpath + "td[3]/div[1][contains(@class,'text-secondary')]")
        else:
            self.assert_not_exists(tr_xpath + "td[3]/div[1][contains(@class,'text-secondary')]")

    def verify_clue_has_no_answer_and_parsing_shown(self, clue):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        self.assert_not_exists(tr_xpath + "td[3]/input")
        self.assert_not_exists(tr_xpath + "td[3]/div[2]")

    def verify_clue_has_answer_and_parsing_shown(self, clue):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        self.assert_exists(tr_xpath + "td[3]/input")
        self.assert_exists(tr_xpath + "td[3]/div[2]")

    def verify_score(self, points):
        self.assert_text_equals("//div[@id='id-score']", "Score: " + str(points) + " pts")

    def verify_progress_bars(self, solved_percent, revealed_percent):
        solved_bar = self.get_element("//div[@id='id-num-solved']")
        revealed_bar = self.get_element("//div[@id='id-num-revealed']")
        self.assertEqual(solved_bar.get_attribute('style'), 'width: ' + str(solved_percent) + '%;')
        self.assertEqual(revealed_bar.get_attribute('style'), 'width: ' + str(revealed_percent) + '%;')

    def verify_timer(self, timer_string):
        self.assert_text_equals("//div[@id='id-timer']", timer_string)


class SolveSessionTests(SolveSessionTestCaseHelper):
    target_page = "/solve_session/"
    DONE_BTN = "//div//i[contains(@class,'fa-circle-xmark')]"
    PUZZLE_TIMELOG = "//div[@id='timelog']"
    PUZZLE_DESC = "//span[contains(@class,'pre-line')]"
    START_SESSION_BTN = "//button[@id='startSessionBtn']"
    DESC_HIDE_TOGGLE = "//a[contains(@class,'icon-btn')]"
    DESC_PANEL = "//div[@id='desc-panel']"
    SESSION_PANEL = "//div[@id='session-panel']"
    SESSION_STATUS = "//div[@id='session-panel']/div/div[1]"
    SESSION_SCORE = "//div[@id='session-panel']/div/div[2]"
    CLUES_LIST = "//div[@id='clues-list']"
    CLUE_NUM_CELL = "(//tr//td[contains(@class,'clue-num')])"
    CLUE_TEXT_CELL = "(//tr//td/a[contains(@class,'clue-text')])"
    ANSWER_CELL = "(//tr//td/div[contains(@class,'answer')])"
    POINTS_CELL = "(//tr//td[contains(@class,'points')])"
    ANSWER_DIALOG = "//dialog[@id='answer-dialog']"
    ANSWER_DIALOG_TITLE = "//dialog[@id='answer-dialog']/div"
    ANSWER_DIALOG_CLUE = "//dialog[@id='answer-dialog']//div[@id='clue-text']"
    ANSWER_DIALOG_INPUT = "//dialog[@id='answer-dialog']//input[@id='answer']"
    ANSWER_DIALOG_MSG = "//dialog[@id='answer-dialog']//div[@id='err-msg']"
    ANSYWER_DIALOG_CANCEL = "//dialog[@id='answer-dialog']//button[@id='btnClose']"
    ANSWER_DIALOG_SUBMIT = "//dialog[@id='answer-dialog']//button[@id='btnSubmit']"

    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user", email="abc@cde.com")
        self.puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[5, 2, 3, 1, 2], desc="some description")
        # self.session = create_session(solver=self.user, puzzle=self.puzzle, solved_clues='1,4',
        #                               revealed_clues='5', elapsed_secs=300)
        self.clues = self.puzzle.get_clues()

    def test_no_existing_solver_session_gives_option_to_start_solve_session(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.assert_page_title("Solve Session")
        self.assert_subtitle(str(self.puzzle))
        self.assert_exists(self.DONE_BTN)
        timelog = "Posted by " + str(self.puzzle.editor) + " on " + self.utc_to_local(self.puzzle.shared_at)
        self.assert_text_equals(self.PUZZLE_TIMELOG, timelog)
        self.assert_text_equals(self.PUZZLE_DESC, self.puzzle.desc)
        self.assert_exists(self.START_SESSION_BTN)
        self.do_click(self.DONE_BTN)
        self.assert_current_url("/puzzles_list")

    def test_description_panel_can_be_hidden_with_a_toggle(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.assert_is_displayed(self.DESC_PANEL)
        self.do_click(self.DESC_HIDE_TOGGLE)
        self.assert_is_not_displayed(self.DESC_PANEL)
        self.do_click(self.DESC_HIDE_TOGGLE)
        self.assert_is_displayed(self.DESC_PANEL)

    def test_start_session_button_initiates_session_and_shows_clues(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.assert_not_exists(self.SESSION_PANEL)
        self.assert_not_exists(self.CLUES_LIST)
        self.do_click(self.START_SESSION_BTN)
        self.assert_not_exists(self.START_SESSION_BTN)
        self.assert_is_not_displayed(self.DESC_PANEL)
        self.assert_is_displayed(self.SESSION_PANEL)
        self.assert_text_equals(self.SESSION_STATUS, "Session Status: In Progress")
        self.assert_text_equals(self.SESSION_SCORE, "My Score: 0")
        self.assert_is_displayed(self.CLUES_LIST)

    def test_clue_details_in_list(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.do_click(self.START_SESSION_BTN)
        self.assert_item_count(self.CLUE_NUM_CELL, 5)
        clues = Clue.objects.filter(puzzle=self.puzzle)
        for index in range(0, len(clues)):
            self.assert_text_equals(self.CLUE_NUM_CELL, str(clues[index].clue_num) + '.', index)
            self.assert_text_equals(self.CLUE_TEXT_CELL, str(clues[index].get_decorated_clue_text()), index)
            self.assert_text_equals(self.POINTS_CELL, str(clues[index].points), index)

    def test_clicking_on_a_clue_shows_modal_dialog(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=self.puzzle)
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT_CELL)
        self.assert_is_displayed(self.ANSWER_DIALOG)
        self.assert_text_equals(self.ANSWER_DIALOG_TITLE, "Solve Clue")
        self.assert_text_equals(self.ANSWER_DIALOG_CLUE, "1. " + clues[0].get_decorated_clue_text())
        self.do_click(self.ANSYWER_DIALOG_CANCEL)
        self.assert_is_not_displayed(self.ANSWER_DIALOG)

    def test_submitting_non_conforming_answers_shows_error_message(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=self.puzzle)
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT_CELL)
        # Check non-alpha characters in input
        self.set_input_text(self.ANSWER_DIALOG_INPUT, "word-1#")
        msg = "Answer can only contain alphabets, hyphen and/or spaces."
        self.do_click(self.ANSWER_DIALOG_SUBMIT)
        self.assert_text_equals(self.ANSWER_DIALOG_MSG, msg)
        # Check input answer length matches specified length in clue
        self.set_input_text(self.ANSWER_DIALOG_INPUT, "word a")
        msg = "Answer does not match specified length in clue."
        self.do_click(self.ANSWER_DIALOG_SUBMIT)
        self.assert_text_equals(self.ANSWER_DIALOG_MSG, msg)

    def test_submitting_conforming_but_wrong_answer_shows_error_message(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=self.puzzle)
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT_CELL)
        # Check input answer length matches specified length in clue
        self.set_input_text(self.ANSWER_DIALOG_INPUT, "word-b")
        msg = "Answer is incorrect."
        self.do_click(self.ANSWER_DIALOG_SUBMIT)
        self.assert_text_equals(self.ANSWER_DIALOG_MSG, msg)

        # self.verify_score(6)
        # self.verify_progress_bars(40, 20)
        # self.assert_is_displayed(self.FINISH_LATER_BTN)
        #self.assert_is_not_displayed(self.COMPLETED)

    # def test_clues_list_contains_clue_state_num_description_and_points(self):
    #     for clue in self.clues:
    #         tr_xpath = self.get_table_row_xpath(clue.clue_num)
    #         clue_state = self.get_state_of_clue(clue, self.session)
    #         self.verify_clue_state_icon(clue, clue_state)
    #         self.assert_text_equals(tr_xpath + "td[2]", str(clue.clue_num) + ".")
    #         self.assert_text_equals(tr_xpath + "td[3]/div[1]", clue.get_decorated_clue_text())
    #         self.verify_clue_text_color_by_state(clue, clue_state)
    #         self.verify_clue_points_by_state(clue, clue_state)
    #         self.verify_clue_has_no_answer_and_parsing_shown(clue)
    #
    # def test_clicking_on_a_solved_clue_toggles_answer_and_parsing(self):
    #     self.click_on_clue(1)  # Click first clue (SOLVED)
    #     self.verify_clue_has_answer_and_parsing_shown(self.clues[0])
    #     self.click_on_clue(1)  # Click first clue again
    #     self.verify_clue_has_no_answer_and_parsing_shown(self.clues[0])
    #
    # def test_clicking_on_a_revealed_clue_toggles_answer_and_parsing(self):
    #     self.click_on_clue(5)  # Click fifth clue (REVEALED)
    #     self.verify_clue_has_answer_and_parsing_shown(self.clues[4])
    #     self.click_on_clue(5)  # Click fifth clue again
    #     self.verify_clue_has_no_answer_and_parsing_shown(self.clues[4])
    #
    # def test_clicking_on_unsolved_clue_shows_modal_answer_box(self):
    #     self.assert_is_not_displayed(self.MODAL_DIALOG)
    #     self.click_on_clue(2)  # Click 2nd clue (UNSOLVED)
    #     self.wait_until_visible(self.MODAL_DIALOG)
    #     self.assert_is_displayed(self.MODAL_DIALOG)
    #     # Verify Answer box contents
    #     self.assert_text_equals(self.MODAL_TITLE, "Clue #" + str(self.clues[1].clue_num))
    #     self.assert_text_equals(self.CLUE_TEXT, self.clues[1].get_decorated_clue_text())
    #     self.assert_attribute_equals(self.ANSWER_INPUT, "")
    #     self.assert_text_equals(self.ERR_MSG, "")
    #
    # def test_correct_answer_submit_sets_solved_state_and_saves_timer(self):
    #     self.click_on_clue(2)  # Click on 2nd clue
    #     self.set_answer_input(self.clues[1].answer.lower())
    #     time.sleep(1)
    #     self.do_click(self.SUBMIT_BTN)
    #     self.verify_timer("00:05:01s")  # Timer snapshot saved when answer is submited
    #     self.wait_until_invisible(self.MODAL_DIALOG)
    #     self.verify_clue_state_icon(self.clues[1], 'SOLVED')
    #     self.verify_clue_text_color_by_state(self.clues[1], 'SOLVED')
    #     self.verify_clue_points_by_state(self.clues[1], 'SOLVED')
    #     self.verify_clue_has_answer_and_parsing_shown(self.clues[1])
    #     self.verify_score(8)
    #     self.verify_progress_bars(60, 20)
    #     self.assert_is_not_displayed(self.COMPLETED)
    #     saved_secs = PuzzleSession.objects.get(puzzle=self.puzzle, solver=self.user).elapsed_seconds
    #     self.assertEqual(saved_secs, 301)
    #
    # def test_reveal_answer_sets_revealed_state_and_saves_timer(self):
    #     self.click_on_clue(2)  # Click on 2nd clue
    #     time.sleep(1)
    #     self.do_click(self.REVEAL_BTN)  # Reveal 2nd clue
    #     self.verify_timer("00:05:01s")  # Timer snapshot saved when answer is submited
    #     self.wait_until_invisible(self.MODAL_DIALOG)
    #     self.verify_clue_state_icon(self.clues[1], 'REVEALED')
    #     self.verify_clue_text_color_by_state(self.clues[1], 'REVEALED')
    #     self.verify_clue_points_by_state(self.clues[1], 'REVEALED')
    #     self.verify_clue_has_answer_and_parsing_shown(self.clues[1])
    #     self.verify_score(6)
    #     self.verify_progress_bars(40, 40)
    #     self.assert_is_not_displayed(self.COMPLETED)
    #     saved_secs = PuzzleSession.objects.get(puzzle=self.puzzle, solver=self.user).elapsed_seconds
    #     self.assertEqual(saved_secs, 301)
    #
    # def test_incorrect_answer_submit_sets_incorrect_state(self):
    #     self.click_on_clue(2)  # Click on 2nd clue
    #     self.set_answer_input("WORD-X")  # Wrong answer
    #     self.do_click(self.SUBMIT_BTN)
    #     self.assert_is_displayed(self.MODAL_DIALOG)
    #     time.sleep(1)
    #     self.assert_text_equals(self.ERR_MSG, "Incorrect answer")
    #     self.verify_score(6)
    #     self.verify_progress_bars(40, 20)
    #     self.assert_is_not_displayed(self.COMPLETED)
    #     # Clear btn clears incorrect answer state
    #     self.do_click(self.CLEAR_BTN)
    #     self.assert_is_not_displayed(self.ERR_MSG)
    #     answer_input = self.get_element(self.ANSWER_INPUT)
    #     self.assertEqual(answer_input.get_attribute('value'), "")
    #     self.assertEqual(answer_input, self.get_active_element())  # Has focus


@skip
class SessionTimerTests(SolveSessionTestCaseHelper):
    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user")
        self.puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[3, 2])
        self.session = create_session(solver=self.user, puzzle=self.puzzle, solved_clues='1', elapsed_secs=300)
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')

    def test_session_timer_is_initialized_from_exisitng_session_and_advances(self):
        self.verify_timer("00:05:00s")
        time.sleep(2)
        self.verify_timer("00:05:02s")

    def test_session_timer_is_stopped_and_saved_on_page_unload(self):
        self.verify_timer("00:05:00s")
        time.sleep(2)
        # FINISH LATER button unloads page and saves timer @ 00:05:02s
        self.do_click(self.FINISH_LATER_BTN)
        time.sleep(2)
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')
        # Saved value should be relaoded
        self.verify_timer("00:05:02s")
        time.sleep(2)
        self.verify_timer("00:05:04s")

    def test_completing_puzzle_updates_status_saves_and_freezes_timer(self):
        # Wait before completing puzzle so timer advances (Clue #2 unsolved)
        time.sleep(2)
        self.click_on_clue(2)
        self.wait_until_visible(self.MODAL_DIALOG)
        self.do_click(self.REVEAL_BTN)
        # Puzzle completed! Below time wait should not advance timer
        time.sleep(3)
        self.verify_timer("00:05:02s")
        self.assert_is_displayed(self.COMPLETED)
        self.assert_is_not_displayed(self.FINISH_LATER_BTN)
        # Page reload should retrieve last saved timer setting
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')
        self.verify_timer("00:05:02s")
        time.sleep(3)
        self.verify_timer("00:05:02s")

    def test_completing_puzzle_shows_scores_button(self):
        self.click_on_clue(2)
        self.wait_until_visible(self.MODAL_DIALOG)
        self.do_click(self.REVEAL_BTN)
        self.wait_until_visible(self.SCORES)
        self.assert_is_displayed(self.SCORES)
        self.do_click(self.SCORES)
        self.assert_current_url('/puzzle_score/' + str(self.puzzle.id) + '/')
