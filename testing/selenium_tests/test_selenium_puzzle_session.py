import time

from puzzles.models import Clue, SolverSession, SolvedClue
from testing.data_setup_utils import create_published_puzzle, create_user
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class PuzzleSessionTests(BaseSeleniumTestCase):
    target_page = "/puzzle_session/"

    DONE_BTN = "//div//i[contains(@class,'fa-circle-xmark')]"
    PUZZLE_TIMELOG = "//div[@id='timelog']"
    PUZZLE_DESC = "//span[contains(@class,'pre-line')]"
    START_SESSION_BTN = "//button[@id='startSessionBtn']"
    DESC_HIDE_TOGGLE = "//a[contains(@class,'icon-btn')]"
    DESC_PANEL = "//div[@id='desc-panel']"
    SESSION_PANEL = "//div[@id='session-panel']"
    SESSION_STATUS = "//div[@id='session-panel']//span[@id='session-status']"
    SESSION_SCORE = "//div[@id='session-panel']//span[@id='score']"
    SESSION_START_TIME = "//div[@id='session-panel']//span[@id='start-time']"
    SESSION_END_TIME = "//div[@id='session-panel']//span[@id='end-time']"
    SESSION_SOLVED_COUNT = "//div[@id='session-panel']//span[@id='solved-count']"
    SESSION_REVEALED_COUNT = "//div[@id='session-panel']//span[@id='revealed-count']"
    CLUES_LIST = "//div[@id='clues-list']"
    CLUE_NUM = "//tr//td[contains(@class,'clue-num')]"
    CLUE_TEXT = "//tr//td/a[contains(@class,'clue-text')]"
    CLUE_TEXT_SOLVED = "//tr//td//span[contains(@class,'clue-text')]"
    CLUE_ANSWER = "//tr//td//span[contains(@class,'answer')]"
    CLUE_REVEAL_BTN = "//tr//td/a/i[contains(@class,'fa-eye')]"
    CLUE_SOLVED_ICON = "//tr//td/i[contains(@class,'fa-check')]"
    CLUE_REVEALED_ICON = "//tr//td/i[contains(@class,'fa-eye')]"
    POINTS = "//tr//td[contains(@class,'points')]"
    ANSWER_DIALOG = "//dialog[@id='answer-dialog']"
    ANSWER_DIALOG_TITLE = "//dialog[@id='answer-dialog']/div"
    ANSWER_DIALOG_CLUE_NUM = "//dialog[@id='answer-dialog']//span[@id='clue-num']"
    ANSWER_DIALOG_CLUE_TEXT = "//dialog[@id='answer-dialog']//span[@id='clue-text']"
    ANSWER_DIALOG_INPUT = "//dialog[@id='answer-dialog']//input[@id='answer-input']"
    ANSWER_DIALOG_MSG = "//dialog[@id='answer-dialog']//div[@id='err-msg']"
    ANSWER_DIALOG_CANCEL = "//dialog[@id='answer-dialog']//button[@id='btnClose']"
    ANSWER_DIALOG_SUBMIT = "//dialog[@id='answer-dialog']//button[@id='btnSubmit']"

    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user", email="abc@cde.com")
        self.puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[5, 2, 3, 1, 2],
                                              desc="some description")
        self.clues = self.puzzle.get_clues()

    def test_no_existing_solver_session_gives_option_to_start_solve_session(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.assert_page_title("Puzzle Session")
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
        self.assert_is_not_displayed(self.DESC_PANEL)  # Desc hidden when session starts
        session = SolverSession.objects.get(puzzle=self.puzzle, solver=self.user)
        # Verify session panel
        self.assert_is_displayed(self.SESSION_PANEL)
        self.assert_text_equals(self.SESSION_STATUS, "In Progress")
        self.assert_text_equals(self.SESSION_SCORE, "My Score: 0")
        self.assert_text_equals(self.SESSION_START_TIME, self.utc_to_local(session.started_at))
        self.assert_not_exists(self.SESSION_END_TIME)
        self.assert_text_equals(self.SESSION_SOLVED_COUNT, "Solved Clues: 0")
        self.assert_text_equals(self.SESSION_REVEALED_COUNT, "Revealed Clues: 0")
        self.assert_is_displayed(self.CLUES_LIST)

    def test_clue_details_in_list(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.do_click(self.START_SESSION_BTN)
        self.assert_item_count(self.CLUE_NUM, 5)
        clues = Clue.objects.filter(puzzle=self.puzzle)
        for index in range(0, len(clues)):
            self.assert_text_equals(self.CLUE_NUM, str(clues[index].clue_num) + '.', index)
            self.assert_text_equals(self.CLUE_TEXT, str(clues[index].get_decorated_clue_text()), index)
            self.assert_text_equals(self.POINTS, str(clues[index].points), index)
            self.assert_not_exists(self.CLUE_ANSWER + "[" + str(index + 1) + "]")
            self.assert_exists(self.CLUE_REVEAL_BTN)

    def test_clicking_on_a_clue_shows_modal_dialog(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=self.puzzle)
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT)
        self.assert_is_displayed(self.ANSWER_DIALOG)
        self.assert_text_equals(self.ANSWER_DIALOG_TITLE, "Solve Clue")
        self.assert_text_equals(self.ANSWER_DIALOG_CLUE_NUM, str(clues[0].clue_num))
        self.assert_text_equals(self.ANSWER_DIALOG_CLUE_TEXT, clues[0].get_decorated_clue_text())
        self.do_click(self.ANSWER_DIALOG_CANCEL)
        self.assert_is_not_displayed(self.ANSWER_DIALOG)

    def test_submitting_non_conforming_answers_shows_error_message(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=self.puzzle)
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT)
        # Check for empty input
        self.set_input_text(self.ANSWER_DIALOG_INPUT, "  ")
        msg = "Answer cannot be empty."
        self.do_click(self.ANSWER_DIALOG_SUBMIT)
        self.assert_text_equals(self.ANSWER_DIALOG_MSG, msg)
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

    def test_conforming_but_incorrect_answer_shows_error_message(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = Clue.objects.filter(puzzle=self.puzzle)
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT)
        # Check input answer length matches specified length in clue
        self.set_input_text(self.ANSWER_DIALOG_INPUT, "word-b")
        msg = "Answer is incorrect."
        self.do_click(self.ANSWER_DIALOG_SUBMIT)
        self.assert_text_equals(self.ANSWER_DIALOG_MSG, msg)

    def test_correct_answer_closes_dialog_and_refreshes_page(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        clues = self.puzzle.get_clues()
        self.do_click(self.START_SESSION_BTN)
        self.do_click(self.CLUE_TEXT, 1)  # 2nd clue
        self.set_input_text(self.ANSWER_DIALOG_INPUT, clues[1].answer)
        self.do_click(self.ANSWER_DIALOG_SUBMIT)
        # Check if solved clue record is created
        time.sleep(0.5)
        session = SolverSession.objects.get(puzzle=self.puzzle)
        solved_clue = SolvedClue.objects.get(solver=self.user)
        self.assertEqual(solved_clue.session, session)
        self.assertEqual(solved_clue.clue.id, clues[1].id)
        self.assertFalse(solved_clue.revealed)
        self.assertRaises(Exception, self.assert_exists(self.ANSWER_DIALOG))  # Stale element due to refresh

    def test_existing_session_is_loaded_correctly(self):
        session = SolverSession.objects.create(solver=self.user, puzzle=self.puzzle)
        clues = self.puzzle.get_clues()
        session.set_solved_clue(clue=clues[0])
        session.set_solved_clue(clue=clues[2])
        session.set_revealed_clue(clue=clues[3])
        self.get(self.target_page + str(self.puzzle.id) + '/')
        # Session Panel info
        self.assert_not_exists(self.START_SESSION_BTN)
        self.assert_is_displayed(self.SESSION_PANEL)
        self.assert_text_equals(self.SESSION_STATUS, "In Progress")
        self.assert_text_equals(self.SESSION_SCORE, "My Score: 8")
        self.assert_text_equals(self.SESSION_START_TIME, self.utc_to_local(session.started_at))
        self.assert_not_exists(self.SESSION_END_TIME)
        self.assert_text_equals(self.SESSION_SOLVED_COUNT, "Solved Clues: 2")
        self.assert_text_equals(self.SESSION_REVEALED_COUNT, "Revealed Clues: 1")
        self.assert_is_displayed(self.CLUES_LIST)
        # Check solved clue 1
        self.assert_text_equals(self.CLUE_NUM, str(clues[0].clue_num) + '.', 0)
        self.assert_text_equals(self.CLUE_TEXT_SOLVED, str(clues[0].get_decorated_clue_text()), 0)
        self.assert_text_equals(self.POINTS, str(clues[0].points), 0)
        self.assert_text_equals(self.CLUE_ANSWER, "[ " + clues[0].answer + " ]")
        self.assert_exists(self.CLUE_SOLVED_ICON)
        # Check revealed clue 4
        self.assert_text_equals(self.CLUE_NUM, str(clues[3].clue_num) + '.', 3)
        self.assert_text_equals(self.CLUE_TEXT_SOLVED, str(clues[3].get_decorated_clue_text()), 2)
        self.assert_text_equals(self.POINTS, str(clues[3].points), 3)
        self.assert_text_equals(self.CLUE_ANSWER, "[ " + clues[3].answer + " ]", 2)
        self.assert_exists(self.CLUE_REVEALED_ICON)

    def test_clicking_on_reveal_btn_stores_revealed_clue(self):
        session = SolverSession.objects.create(solver=self.user, puzzle=self.puzzle)
        clues = self.puzzle.get_clues()
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.do_click(self.CLUE_REVEAL_BTN, 1)  # Clue #2
        # Check if revealed clue record is created
        time.sleep(0.4)
        session = SolverSession.objects.get(puzzle=self.puzzle)
        revealed_clue = SolvedClue.objects.get(solver=self.user)
        self.assertEqual(revealed_clue.session, session)
        self.assertEqual(revealed_clue.clue.id, clues[1].id)
        self.assertTrue(revealed_clue.revealed)
        # Check revealed clue 4
        self.assert_text_equals(self.CLUE_NUM, str(clues[1].clue_num) + '.', 1)
        self.assert_text_equals(self.CLUE_TEXT_SOLVED, str(clues[1].get_decorated_clue_text()))
        self.assert_text_equals(self.POINTS, str(clues[1].points), 1)
        self.assert_text_equals(self.CLUE_ANSWER, "[ " + clues[1].answer + " ]")
        self.assert_exists(self.CLUE_REVEALED_ICON)

    def test_completing_puzzle_session_displays_correct_session_status(self):
        session = SolverSession.objects.create(solver=self.user, puzzle=self.puzzle)
        clues = self.puzzle.get_clues()
        # Pre-solved clues
        session.set_revealed_clue(clue=clues[0])
        session.set_solved_clue(clue=clues[1])
        session.set_solved_clue(clue=clues[2])
        session.set_solved_clue(clue=clues[3])
        self.get(self.target_page + str(self.puzzle.id) + '/')
        # Reveal last clue
        self.do_click(self.CLUE_REVEAL_BTN)  # Clue #5 (only reveal btn remaining
        # Verify completed session panel
        time.sleep(2)
        updated_session = SolverSession.objects.get(solver=self.user, puzzle=self.puzzle)
        self.assert_text_equals(self.SESSION_STATUS, "Completed")
        self.assert_text_equals(self.SESSION_SCORE, "My Score: 6")
        self.assert_text_equals(self.SESSION_START_TIME, self.utc_to_local(updated_session.started_at))
        self.assert_text_equals(self.SESSION_END_TIME, self.utc_to_local(updated_session.finished_at))
        self.assert_text_equals(self.SESSION_SOLVED_COUNT, "Solved Clues: 3")
        self.assert_text_equals(self.SESSION_REVEALED_COUNT, "Revealed Clues: 2")
