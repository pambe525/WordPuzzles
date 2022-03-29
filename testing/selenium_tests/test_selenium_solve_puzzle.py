from django.contrib.auth.models import User
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase

from testing.django_unit_tests.unit_test_helpers import create_published_puzzle, create_session, get_full_clue_desc


class SolvePuzzleTests(SeleniumTestCase):
    user = None
    password = 'secret_key'

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.login_user(username=self.user.username, password=self.password)
        self.other_user = User.objects.create_user(username="other_user", password=self.password)

    def test_Displays_loaded_session_state(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[5, 2, 3, 1, 2])
        session = create_session(solver=self.user, puzzle=puzzle, solved_clues='1,4', revealed_clues='5',
                                 elapsed_secs=5000)
        clues = puzzle.get_clues()
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Solve Puzzle")
        self.verify_all_clue_btns_states(session)
        self.verify_answer_state_for_clue(clues[0], session)     # SOLVED clue #1
        self.verify_answer_state_for_clue(clues[4], session)     # REVEALED clue #5
        self.verify_answer_state_for_clue(clues[1], session)     # UNSOLVED clue #2
        self.verify_score(session)
        self.verify_progress_bars(46, 15)
        self.verify_timer("01:23:20s")

    ##==============================================================================================================
    # HELPER FUNCTIONS
    #
    def verify_all_clue_btns_states(self, session):
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        for index, clue in enumerate(session.puzzle.get_clues()):
            clue_btn = self.get_element("//div/button[@id='clue-btn-" + str(index + 1) + "']")
            if clue.clue_num in solved_clues: self.verify_clue_btn_has_state(clue_btn, 'solved')
            elif clue.clue_num in revealed_clues: self.verify_clue_btn_has_state(clue_btn, 'revealed')
            else: self.verify_clue_btn_has_state(clue_btn, 'unsolved')

    def verify_answer_state_for_clue(self, clue, session):
        self.do_click("//div/button[@id='clue-btn-" + str(clue.clue_num) + "']")    # Click on Clue btn
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(clue))   # Check clue text
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        if clue.clue_num in solved_clues: self.verify_answer_state_as_solved(clue)
        elif clue.clue_num in revealed_clues: self.verify_answer_state_as_revealed(clue)
        else: self.verify_answer_state_as_unsolved()

    def verify_answer_state_as_solved(self, clue):
        self.assert_is_displayed("//div[@id='id-check-icon']")
        self.assert_text_equals("//div[@id='id-answer-msg']", "[" + str(clue.points) + " pts]")
        self.assert_is_not_displayed("//div[@id='id-eye-icon']")
        self.assert_is_not_displayed("//div[@id='id-wrong-icon']")
        self.assert_is_not_displayed("//div[@id='id-answer-btns']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n',"")
        self.assertEqual(answer, clue.answer)
        if clue.parsing: self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clue.parsing)
        else: self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_answer_state_as_revealed(self, clue):
        self.assert_is_not_displayed("//div[@id='id-check-icon']")
        self.assert_text_equals("//div[@id='id-answer-msg']", "[0 pts]")
        self.assert_is_displayed("//div[@id='id-eye-icon']")
        self.assert_is_not_displayed("//div[@id='id-answer-btns']")
        self.assert_is_not_displayed("//div[@id='id-wrong-icon']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n',"")
        self.assertEqual(answer, clue.answer)
        if clue.parsing: self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clue.parsing)
        else: self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_answer_state_as_unsolved(self):
        self.assert_is_not_displayed("//div[@id='id-answer-icons']//*")
        self.assert_is_displayed("//div[@id='id-answer-btns']")
        self.assert_is_displayed("//button[@id='id-submit-btn']")
        self.assert_is_displayed("//button[@id='id-clear-btn']")
        self.assert_is_displayed("//button[@id='id-reveal-btn']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n',"")
        self.assertEqual(answer, "")
        self.assert_is_not_displayed("//div[@id='id-parsing']")

    def verify_clue_btn_has_state(self, clue_btn, state):
        class_dict = {'solved': 'btn-success', 'unsolved': 'btn-light', 'revealed': 'btn-secondary'}
        for state_key in class_dict:
            if state == state_key:
                self.assertIn(class_dict[state_key], clue_btn.get_attribute('class'))
            else:
                self.assertNotIn(class_dict[state_key], clue_btn.get_attribute('class'))

    def verify_score(self, session):
        self.assert_text_equals("//div[@id='id-score']", "Score: " + str(session.get_solved_points()) + " pts")

    def verify_progress_bars(self, solved_percent, revealed_percent):
        solved_bar = self.get_element("//div[@id='id-solved-pts']")
        revealed_bar = self.get_element("//div[@id='id-revealed-pts']")
        self.assertEqual(solved_bar.get_attribute('style'), 'width: ' + str(solved_percent) + '%;' )
        self.assertEqual(revealed_bar.get_attribute('style'), 'width: ' + str(revealed_percent) + '%;' )

    def verify_timer(self, timer_string):
        self.assert_text_equals("//div[@id='id-timer']", timer_string)

