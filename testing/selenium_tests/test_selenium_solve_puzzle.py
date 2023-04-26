import time

from puzzles.models import PuzzleSession
from testing.data_setup_utils import create_published_puzzle, create_session, create_user
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


# ======================================================================================================================
# HELPER FUNCTIONS FOR SolveSession Test Cases cast as a derived class (of SeleneiumTestCase
# Test cases for Solve Session should derive from this class.
class SolveSessionTestCaseHelper(SeleniumTestCase):
    
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
        self.wait_until_visible(self.MODAL_DIALOG)
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
    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user")
        self.puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[5, 2, 3, 1, 2], has_parsing=True)
        self.session = create_session(solver=self.user, puzzle=self.puzzle, solved_clues='1,4',
                                      revealed_clues='5', elapsed_secs=300)
        self.clues = self.puzzle.get_clues()
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')

    def test_loads_existing_session_state(self):
        self.assert_text_equals("//h2", "Solve Puzzle")
        self.assert_exists("//div[contains(text(),'Click on a clue below')]")
        self.verify_score(6)
        self.verify_progress_bars(40, 20)
        self.assert_is_displayed(self.FINISH_LATER_BTN)
        self.assert_is_not_displayed(self.COMPLETED)

    def test_clues_list_contains_clue_state_num_description_and_points(self):
        for clue in self.clues:
            tr_xpath = self.get_table_row_xpath(clue.clue_num)
            clue_state = self.get_state_of_clue(clue, self.session)
            self.verify_clue_state_icon(clue, clue_state)
            self.assert_text_equals(tr_xpath + "td[2]", str(clue.clue_num) + ".")
            self.assert_text_equals(tr_xpath + "td[3]/div[1]", clue.get_decorated_clue_text())
            self.verify_clue_text_color_by_state(clue, clue_state)
            self.verify_clue_points_by_state(clue, clue_state)
            self.verify_clue_has_no_answer_and_parsing_shown(clue)

    def test_clicking_on_a_solved_clue_toggles_answer_and_parsing(self):
        self.click_on_clue(1)  # Click first clue (SOLVED)
        self.verify_clue_has_answer_and_parsing_shown(self.clues[0])
        self.click_on_clue(1)  # Click first clue again
        self.verify_clue_has_no_answer_and_parsing_shown(self.clues[0])

    def test_clicking_on_a_revealed_clue_toggles_answer_and_parsing(self):
        self.click_on_clue(5)  # Click fifth clue (REVEALED)
        self.verify_clue_has_answer_and_parsing_shown(self.clues[4])
        self.click_on_clue(5)  # Click fifth clue again
        self.verify_clue_has_no_answer_and_parsing_shown(self.clues[4])

    def test_clicking_on_unsolved_clue_shows_modal_answer_box(self):
        self.assert_is_not_displayed(self.MODAL_DIALOG)
        self.click_on_clue(2)  # Click 2nd clue (UNSOLVED)
        self.wait_until_visible(self.MODAL_DIALOG)
        self.assert_is_displayed(self.MODAL_DIALOG)
        # Verify Answer box contents
        self.assert_text_equals(self.MODAL_TITLE, "Clue #" + str(self.clues[1].clue_num))
        self.assert_text_equals(self.CLUE_TEXT, self.clues[1].get_decorated_clue_text())
        self.assert_value_equals(self.ANSWER_INPUT, "")
        self.assert_text_equals(self.ERR_MSG, "")

    def test_correct_answer_submit_sets_solved_state_and_saves_timer(self):
        self.click_on_clue(2)  # Click on 2nd clue
        self.set_answer_input(self.clues[1].answer.lower())
        time.sleep(1)
        self.do_click(self.SUBMIT_BTN)
        self.verify_timer("00:05:01s")  # Timer snapshot saved when answer is submited
        self.wait_until_invisible(self.MODAL_DIALOG)
        self.verify_clue_state_icon(self.clues[1], 'SOLVED')
        self.verify_clue_text_color_by_state(self.clues[1], 'SOLVED')
        self.verify_clue_points_by_state(self.clues[1], 'SOLVED')
        self.verify_clue_has_answer_and_parsing_shown(self.clues[1])
        self.verify_score(8)
        self.verify_progress_bars(60, 20)
        self.assert_is_not_displayed(self.COMPLETED)
        saved_secs = PuzzleSession.objects.get(puzzle=self.puzzle, solver=self.user).elapsed_seconds
        self.assertEqual(saved_secs, 301)

    def test_reveal_answer_sets_revealed_state_and_saves_timer(self):
        self.click_on_clue(2)  # Click on 2nd clue
        time.sleep(1)
        self.do_click(self.REVEAL_BTN)  # Reveal 2nd clue
        self.verify_timer("00:05:01s")  # Timer snapshot saved when answer is submited
        self.wait_until_invisible(self.MODAL_DIALOG)
        self.verify_clue_state_icon(self.clues[1], 'REVEALED')
        self.verify_clue_text_color_by_state(self.clues[1], 'REVEALED')
        self.verify_clue_points_by_state(self.clues[1], 'REVEALED')
        self.verify_clue_has_answer_and_parsing_shown(self.clues[1])
        self.verify_score(6)
        self.verify_progress_bars(40, 40)
        self.assert_is_not_displayed(self.COMPLETED)
        saved_secs = PuzzleSession.objects.get(puzzle=self.puzzle, solver=self.user).elapsed_seconds
        self.assertEqual(saved_secs, 301)

    def test_incorrect_answer_submit_sets_incorrect_state(self):
        self.click_on_clue(2)  # Click on 2nd clue
        self.set_answer_input("WORD-X")  # Wrong answer
        self.do_click(self.SUBMIT_BTN)
        self.assert_is_displayed(self.MODAL_DIALOG)
        time.sleep(1)
        self.assert_text_equals(self.ERR_MSG, "Incorrect answer")
        self.verify_score(6)
        self.verify_progress_bars(40, 20)
        self.assert_is_not_displayed(self.COMPLETED)
        # Clear btn clears incorrect answer state
        self.do_click(self.CLEAR_BTN)
        self.assert_is_not_displayed(self.ERR_MSG)
        answer_input = self.get_element(self.ANSWER_INPUT)
        self.assertEqual(answer_input.get_attribute('value'), "")
        self.assertEqual(answer_input, self.get_active_element())  # Has focus


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
