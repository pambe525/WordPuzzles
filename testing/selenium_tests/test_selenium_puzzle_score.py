import time

from testing.data_setup_utils import create_user, create_published_puzzle, create_session
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class PuzzleScoreTests(SeleniumTestCase):
    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.user2 = create_user(username="user_2")
        self.user3 = create_user(username="user_3")
        self.puzzle = create_published_puzzle(editor=self.user, clues_pts=[5, 2, 3, 1, 2])
        self.get('/puzzle_score/' + str(self.puzzle.id) + '/')

    def test_page_title_and_headers(self):
        self.assert_text_equals("//h2", "Scores for Puzzle #" + str(self.puzzle.id))
        self.assert_text_equals("//h4", str(self.puzzle))
        posted_by_str = 'Posted by: ' + str(self.puzzle.editor) + ' on ' + self.puzzle.shared_at.strftime(
            '%b %d, %Y') + ' (GMT)'
        self.assert_text_equals("//h6[@id='id-posted-by']", posted_by_str)
        self.assert_text_equals("//div[contains(@class,'notetext')]", "No sessions found for this puzzle.")

    def test_shows_scores_in_a_table(self):
        session1 = create_session(solver=self.user2, puzzle=self.puzzle, solved_clues='1,4', revealed_clues='5',
                                  elapsed_secs=200)
        session2 = create_session(solver=self.user3, puzzle=self.puzzle, solved_clues='2,5', elapsed_secs=300)
        self.get('/puzzle_score/' + str(self.puzzle.id) + '/')
        sessions = [session1, session2]
        elapsed_time = ["0:03:20s", "0:05:00s"]
        perc_solved = ['width: 40%;', 'width: 40%;']
        perc_revealed = ['width: 20%;', 'width: 0%;']
        self.assert_not_exists("//div[contains(@class,'notetext')]")
        self.assert_text_equals("//table/thead/tr", "Puzzler Progress Score Time")
        for index, session in enumerate(sessions):
            self.assert_text_equals("//table/tbody/tr/td[1]", str(session.solver), index=index)
            self.assert_text_equals("//table/tbody/tr/td[3]", str(session.score), index=index)
            solved_width = self.get_element("//div[@title='Solved']", index=index).get_attribute('style')
            revealed_width = self.get_element("//div[@title='Revealed']", index=index).get_attribute('style')
            self.assertEqual(solved_width, perc_solved[index])
            self.assertEqual(revealed_width, perc_revealed[index])
            self.assert_text_equals("//table/tbody/tr/td[4]", elapsed_time[index], index=index)

    def test_shows_back_button_to_go_back(self):
        self.assert_exists("//a[text()='BACK']")
        self.do_click("//a[text()='BACK']")
        self.assert_current_url("/")
