import time
from unittest.case import skip

from testing.data_setup_utils import create_user, create_published_puzzle, create_session
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class PuzzleScoresTests(BaseSeleniumTestCase):

    DONE_BTN = "//div//i[contains(@class,'fa-circle-xmark')]"
    PUZZLE_TIMELOG = "//div[@id='timelog']"
    NO_PUZZLES_NOTE = "//div[contains(@class,'note-text')][2]"
    SCORE_LIST_BADGE = "//div[contains(@class,'list-badge')]"
    SOLVER_NAME = "//div[contains(@class,'list-badge')]/div[1]/span"
    SCORE = "//div[contains(@class,'list-badge')]/div[2]/span"
    COUNTS = "//div[contains(@class,'list-badge')]/div/div"
    STATUS_ICON = "//div[contains(@class,'list-badge')]/div[2]/i"
    target_page = "/puzzle_score/"

    def setUp(self):
        self.user1 = create_user()
        self.auto_login_user(self.user1)
        self.user2 = create_user(username="user2", email="abc@xyz.com")
        self.user3 = create_user(username="user3", email="xyx@abc.com")
        self.user4 = create_user(username="Thiscanbeavery Longnamefortest", email='test@gmail.com')
        self.puzzle = create_published_puzzle(editor=self.user2, clues_pts=[5, 2, 3, 1, 2])

    def test_page_title_and_close_btn(self):
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.assert_page_title("Puzzle Session Scores")
        self.assert_subtitle(str(self.puzzle))
        timelog = "Posted by " + str(self.puzzle.editor) + " on " + self.utc_to_local(self.puzzle.shared_at)
        self.assert_text_equals(self.PUZZLE_TIMELOG, timelog)
        self.assert_text_equals(self.NO_PUZZLES_NOTE, "No sessions found for this puzzle.")
        self.do_click(self.DONE_BTN)
        self.assert_current_url("/puzzles_list")

    def test_all_session_scores_are_displayed(self):
        session1 = create_session(self.puzzle, self.user4, 3, 1, 6)
        session2 = create_session(self.puzzle, self.user3, 5, 0, 13)
        session3 = create_session(self.puzzle, self.user1, 0, 0, 0)
        self.get(self.target_page + str(self.puzzle.id) + '/')
        self.assert_not_exists(self.NO_PUZZLES_NOTE)
        ordered_sessions = [session2, session1, session3]
        self.assert_item_count(self.SCORE_LIST_BADGE, 3)
        for index, session in enumerate(ordered_sessions):
            solver_name = "ME" if session.solver == self.user1 else str(session.solver)
            self.assert_text_equals(self.SOLVER_NAME, solver_name, index)
            self.assert_text_equals(self.SCORE, str(session.score), index)
            counts_text = str(session.solved) + " solved | " + str(session.revealed) + " revealed"
            self.assert_text_equals(self.COUNTS, counts_text, index)
            fa_icon = "fa-circle-check" if session.finished_at is not None else "fa-circle-minus"
            self.assert_attribute_contains(self.STATUS_ICON, 'class', fa_icon, index)

