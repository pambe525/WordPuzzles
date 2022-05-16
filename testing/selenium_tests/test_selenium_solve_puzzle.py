import json
import time

from selenium.webdriver.support.wait import WebDriverWait

from puzzles.models import WordPuzzle, PuzzleSession
from testing.data_setup_utils import create_published_puzzle, create_session, get_full_clue_desc, create_user
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase
from selenium.webdriver.support import expected_conditions as EC


# ======================================================================================================================
# HELPER FUNCTIONS FOR SolveSession Test Cases cast as a derived class (of SeleneiumTestCase
# Test cases for Solve Session should derive from this class.
class SolveSessionTestCaseHelper(SeleniumTestCase):

    def set_answer_input(self, input_text):
        self.wait_until_visible("//div[@id='id-modal-answer-box']")
        answer_input = self.get_element("//div[@id='id-answer']/input")
        answer_input.click()
        answer_input.send_keys(input_text)

    @staticmethod
    def get_table_row_xpath(row_num):
        return "//table/tbody/tr[" + str(row_num) + "]/"

    def verify_clue_state_icon(self, clue, session):
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        if clue.clue_num in solved_clues:
            self.assert_exists(tr_xpath + "td[1]/i[@class='fa fa-check-circle text-success']")
        elif clue.clue_num in revealed_clues:
            self.assert_exists(tr_xpath + "td[1]/i[@class='fa fa-eye']")
        else:
            self.assert_not_exists(tr_xpath + "td[1]/i[@class='fa fa-check-circle text-success']")
            self.assert_not_exists(tr_xpath + "td[1]/i[@class='fa fa-eye']")
            self.assert_text_equals(tr_xpath + "td[1]", "")

    def verify_clue_points_by_state(self, clue, session):
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        if clue.clue_num in solved_clues:
            self.assert_not_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
            self.assert_text_equals(tr_xpath + "td[4]", str(clue.points))
        elif clue.clue_num in revealed_clues:
            self.assert_not_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
            self.assert_text_equals(tr_xpath + "td[4]", '0')
        else:
            self.assert_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
            self.assert_text_equals(tr_xpath + "td[4]", "")

    def verify_clue_text_color_by_state(self, clue, session):
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        if clue.clue_num in solved_clues or clue.clue_num in revealed_clues:
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





    #def verify_all_clue_points_by_state(self, session):
        # solved_clues = session.get_solved_clue_nums()
        # revealed_clues = session.get_revealed_clue_nums()
        # for index, clue in enumerate(session.puzzle.get_clues()):
        #     if clue.clue_num in solved_clues:
        #         self.verify_clue_as_solved(clue)
        #     elif clue.clue_num in revealed_clues:
        #         self.verify_clue_as_revealed(clue)
        #     else:
        #         self.verify_clue_as_unsolved(clue)

    def verify_clue_shows_answer(self, clue):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        self.assert_not_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
        self.assert_text_equals(tr_xpath + "td[3]/div[2]", "[" + clue.parsing + "]")
        self.assert_value_equals(tr_xpath + "td[3]/input", clue.answer)

    def verify_clue_as_solved(self, clue):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        self.assert_exists(tr_xpath + "td[1]/i[@class='fa fa-check-circle text-success']")
        self.verify_clue_shows_answer(clue)
        self.assert_text_equals(tr_xpath + "td[4]", str(clue.points))

    def verify_clue_as_revealed(self, clue):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        self.assert_exists(tr_xpath + "td[1]/i[@class='fa fa-eye']")
        self.verify_clue_shows_answer(clue)
        self.assert_text_equals(tr_xpath + "td[4]", '0')

    def verify_clue_as_unsolved(self, clue):
        tr_xpath = self.get_table_row_xpath(clue.clue_num)
        self.assert_not_exists(tr_xpath + "td[1]/i[@class='fa fa-circle-check']")
        self.assert_text_equals(tr_xpath + "td[2]", str(clue.clue_num) + ".")
        self.assert_text_equals(tr_xpath + "td[3]/div[1]", clue.get_decorated_clue_text())
        self.assert_exists(tr_xpath + "td[4]/i[@class='fa fa-eye-slash']")
        self.assert_not_exists(tr_xpath + "td[3]/div[2]")
        self.assert_not_exists(tr_xpath + "td[3]/input")

    def verify_answer_state_for_clue(self, clue, state):
        self.do_click("//div/button[@id='clue-btn-" + str(clue.clue_num) + "']")  # Click on Clue btn
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(clue))  # Check clue text
        if state == 'solved':
            self.verify_answer_state_as_solved(clue)
        elif state == 'revealed':
            self.verify_answer_state_as_revealed(clue)
        else:
            self.verify_answer_state_as_unsolved()

    def verify_answer_state_as_solved(self, clue):
        self.assert_is_displayed("//div[@id='id-check-icon']")
        self.assert_text_equals("//div[@id='id-answer-msg']", "[" + str(clue.points) + " pts]")
        self.assert_is_not_displayed("//div[@id='id-eye-icon']")
        self.assert_is_not_displayed("//div[@id='id-wrong-icon']")
        self.assert_is_not_displayed("//div[@id='id-answer-btns']")
        answer = self.get_element("//div[@id='id-answer']/input").get_attribute('value')
        self.assertEqual(answer, clue.answer)
        if clue.parsing:
            self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clue.parsing)
        else:
            self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_answer_state_as_revealed(self, clue):
        self.assert_is_not_displayed("//div[@id='id-check-icon']")
        self.assert_text_equals("//div[@id='id-answer-msg']", "[0 pts]")
        self.assert_is_displayed("//div[@id='id-eye-icon']")
        self.assert_is_not_displayed("//div[@id='id-answer-btns']")
        self.assert_is_not_displayed("//div[@id='id-wrong-icon']")
        answer = self.get_element("//div[@id='id-answer']/input").get_attribute('value')
        self.assertEqual(answer, clue.answer)
        if clue.parsing:
            self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clue.parsing)
        else:
            self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_answer_state_as_unsolved(self):
        self.assert_is_not_displayed("//div[@id='id-answer-icons']//*")
        self.assert_is_displayed("//div[@id='id-answer-btns']")
        self.assert_is_displayed("//button[@id='id-submit-btn']")
        self.assert_is_displayed("//button[@id='id-clear-btn']")
        self.assert_is_displayed("//button[@id='id-reveal-btn']")
        answer = self.get_element("//div[@id='id-answer']/input").get_attribute('value')
        self.assertEqual(answer, "")
        self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_answer_state_as_incorrect(self):
        self.assert_is_not_displayed("//div[@id='id-answer-icons']//*")
        self.assert_is_displayed("//div[@id='id-answer-btns']")
        self.assert_text_equals("//div[@id='id-answer-msg']", "Incorrect")
        self.assert_is_displayed("//div[@id='id-wrong-icon']")
        self.assert_is_displayed("//button[@id='id-submit-btn']")
        self.assert_is_displayed("//button[@id='id-clear-btn']")
        self.assert_is_displayed("//button[@id='id-reveal-btn']")
        self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_clue_details(self, clue_num, state):
        clue_btn = self.get_element("//button[@id='clue-btn-" + str(clue_num) + "']")
        class_dict = {'solved': 'btn-success', 'unsolved': 'btn-light', 'revealed': 'btn-secondary'}
        for state_key in class_dict:
            if state == state_key:
                self.assertIn(class_dict[state_key], clue_btn.get_attribute('class'))
            else:
                self.assertNotIn(class_dict[state_key], clue_btn.get_attribute('class'))

    def verify_score(self, points):
        self.assert_text_equals("//div[@id='id-score']", "Score: " + str(points) + " pts")

    def verify_progress_bars(self, solved_percent, revealed_percent):
        solved_bar = self.get_element("//div[@id='id-num-solved']")
        revealed_bar = self.get_element("//div[@id='id-num-revealed']")
        self.assertEqual(solved_bar.get_attribute('style'), 'width: ' + str(solved_percent) + '%;')
        self.assertEqual(revealed_bar.get_attribute('style'), 'width: ' + str(revealed_percent) + '%;')

    def verify_timer(self, timer_string):
        self.assert_text_equals("//div[@id='id-timer']", timer_string)

    def get_active_element(self):
        return self.selenium.switch_to.active_element

    def verify_answer_input_has_focus(self):
        answer_input = self.get_element("//div[@id='id-answer']/input")
        self.assertEqual(answer_input, self.get_active_element())  # Has focus

    def verify_answer_input_empty(self):
        answer_input = self.get_element("//div[@id='id-answer']/input")
        self.assertEqual('', answer_input.get_attribute('value'))


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
        self.assert_is_displayed("//a[@id='id-finish-later-btn']")
        self.assert_is_not_displayed("//div[@id='id-completed']")

    def test_clues_list_contains_clue_state_num_description_and_points(self):
        for clue in self.session.puzzle.get_clues():
            tr_xpath = self.get_table_row_xpath(clue.clue_num)
            self.verify_clue_state_icon(clue, self.session)
            self.assert_text_equals(tr_xpath + "td[2]", str(clue.clue_num) + ".")
            self.assert_text_equals(tr_xpath + "td[3]/div[1]", clue.get_decorated_clue_text())
            self.verify_clue_text_color_by_state(clue, self.session)
            self.verify_clue_points_by_state(clue, self.session)
            self.verify_clue_has_no_answer_and_parsing_shown(clue)

    def test_clicking_on_a_solved_clue_toggles_answer_and_parsing(self):
        tr_xpath = self.get_table_row_xpath(1)
        clues = self.session.puzzle.get_clues()
        clue1_cell = self.get_element(tr_xpath + "td[3]")
        clue1_cell.click()  # Click first clue (SOLVED)
        self.verify_clue_has_answer_and_parsing_shown(clues[0])
        clue1_cell.click()  # Click first clue again
        self.verify_clue_has_no_answer_and_parsing_shown(clues[0])

    def test_clicking_on_a_revealed_clue_toggles_answer_and_parsing(self):
        tr_xpath = self.get_table_row_xpath(5)
        clues = self.session.puzzle.get_clues()
        clue5_cell = self.get_element(tr_xpath + "td[3]")
        clue5_cell.click()  # Click first clue (REVEALED)
        self.verify_clue_has_answer_and_parsing_shown(clues[4])
        clue5_cell.click()  # Click first clue again
        self.verify_clue_has_no_answer_and_parsing_shown(clues[4])

    def test_clicking_on_unsolved_clue_shows_modal_answer_box(self):
        tr_xpath = self.get_table_row_xpath(2)
        clues = self.session.puzzle.get_clues()
        clue2_cell = self.get_element(tr_xpath + "td[3]")
        self.assert_is_not_displayed("//div[@id='id-modal-answer-box']")
        clue2_cell.click()  # Click second clue (UNSOLVED)
        self.wait_until_visible("//div[@id='id-modal-answer-box']")
        self.assert_is_displayed("//div[@id='id-modal-answer-box']")
        # Verify Answer box contents
        self.assert_text_equals("//h4[@class='modal-title']", "Clue #"+str(clues[1].clue_num))
        self.assert_text_equals("//div[@id='id-clue-text']", clues[1].get_decorated_clue_text())
        self.assert_value_equals("//div[@id='id-answer']/input","")
        self.assert_text_equals("//div[@id='id-err-msg']", "")

    def test_correct_answer_submit_sets_solved_state_and_saves_timer(self):
        tr_xpath = self.get_table_row_xpath(2)
        self.do_click(tr_xpath + "td[3]")  # Click on 2nd clue
        self.set_answer_input(self.clues[1].answer)
        time.sleep(1)
        self.do_click("//button[@id='id-submit-btn']")
        self.verify_timer("00:05:01s")  # Timer snapshot saved when answer is submited
        self.wait_until_invisible("//button[@id='id-submit-btn']")
        self.verify_clue_details(2, "solved")
        self.verify_answer_state_as_solved(self.clues[1])
        self.verify_score(8)
        self.verify_progress_bars(60, 20)
        self.assert_is_not_displayed("//div[@id='id-completed']")
        saved_secs = PuzzleSession.objects.get(puzzle=self.puzzle, solver=self.user).elapsed_seconds
        self.assertEqual(saved_secs, 301)




    def test_reveal_answer_submit_sets_revealed_state_and_saves_timer(self):
        self.do_click("//button[@id='clue-btn-2']")  # Click on 2nd clue btn
        time.sleep(1)
        self.do_click("//button[@id='id-reveal-btn']")  # Reveal first clue (default)
        self.verify_timer("00:05:01s")  # Timer snapshot saved when answer is submited
        self.wait_until_invisible("//button[@id='id-reveal-btn']")
        self.verify_clue_details(2, "revealed")
        self.verify_answer_state_as_revealed(self.clues[1])
        self.verify_score(6)
        self.verify_progress_bars(40, 40)
        self.assert_is_not_displayed("//div[@id='id-completed']")
        saved_secs = PuzzleSession.objects.get(puzzle=self.puzzle, solver=self.user).elapsed_seconds
        self.assertEqual(saved_secs, 301)

    def test_incorrect_answer_submit_sets_incorrect_state(self):
        self.do_click("//button[@id='clue-btn-2']")  # Click on 2nd clue btn
        self.set_answer_input("WORD-X")  # Wrong answer
        self.do_click("//button[@id='id-submit-btn']")
        self.verify_clue_details(2, "unsolved")
        self.verify_answer_state_as_incorrect()
        self.verify_score(6)
        self.verify_progress_bars(40, 20)
        self.assert_is_not_displayed("//div[@id='id-completed']")
        # Clear btn clears incorrect answer state
        self.do_click("//button[@id='id-clear-btn']")
        self.assert_is_not_displayed("//div[@id='id-wrong-icon']")
        self.assert_is_not_displayed("//div[@id='id-answer-msg']")
        answer = self.get_element("//div[@id='id-answer']/input").get_attribute('value')
        self.assertEqual(answer, "")


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
        self.do_click("//a[@id='id-finish-later-btn']")
        time.sleep(2)
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')
        # Saved value should be relaoded
        self.verify_timer("00:05:02s")
        time.sleep(2)
        self.verify_timer("00:05:04s")

    def test_completing_puzzle_updates_status_saves_and_freezes_timer(self):
        # Wait before completing puzzle so timer advances (Clue #2 unsolved)
        time.sleep(2)
        self.do_click("//button[@id='clue-btn-2']")
        self.do_click("//button[@id='id-reveal-btn']")
        # Puzzle completed! Below time wait should not advance timer
        time.sleep(3)
        self.verify_timer("00:05:02s")
        self.assert_is_displayed("//div[@id='id-completed']")
        self.assert_is_not_displayed("//a[@id='id-finish-later-btn']")
        # Page reload should retrieve last saved timer setting
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')
        self.verify_timer("00:05:02s")
        time.sleep(3)
        self.verify_timer("00:05:02s")

    def test_completing_puzzle_shows_scores_button(self):
        self.do_click("//button[@id='clue-btn-2']")
        self.do_click("//button[@id='id-reveal-btn']")
        self.assert_is_displayed("//a[text()='SCORES']")
        self.do_click("//a[text()='SCORES']")
        self.assert_current_url('/puzzle_score/' + str(self.puzzle.id) + '/')


class AnswerGridEditingTests(SolveSessionTestCaseHelper):
    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user")
        self.puzzle = WordPuzzle.objects.create(editor=self.other_user)
        self.puzzle.add_clue({'answer': 'HYPHEN-AT-D WORD', 'clue_text': 'Clue for complex answer', 'points': 2})
        self.puzzle.add_clue({'answer': 'SINGLEWORD', 'clue_text': 'Clue for single word', 'points': 1})
        self.puzzle.publish()
        create_session(solver=self.user, puzzle=self.puzzle)  # All clues UNSOLVED
        self.get('/solve_puzzle/' + str(self.puzzle.id) + '/')

    def test_answer_input_properties_and_input(self):
        answer_input = self.get_element("//div[@id='id-answer']/input")
        self.assertFalse(answer_input.get_attribute('readonly'))
        focus_element = self.selenium.switch_to.active_element
        self.assertEqual(focus_element, answer_input)

    def test_clearing_grid_and_backspace(self):
        self.set_answer_input("HYPHENATION")
        self.get_element("//button[text()='CLEAR']").click()  # Click CLEAR btn
        self.verify_answer_input_empty()
        self.verify_answer_input_has_focus()
