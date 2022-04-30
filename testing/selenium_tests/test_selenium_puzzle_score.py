from testing.data_setup_utils import create_user, create_published_puzzle, create_session
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class PuzzleScoreTests(SeleniumTestCase):
    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user")
        self.puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[5, 2, 3, 1, 2])
        self.session = create_session(solver=self.user, puzzle=self.puzzle, solved_clues='1,4',
                                      revealed_clues='5', elapsed_secs=300)
        self.clues = self.puzzle.get_clues()
        self.get('/puzzle_score/' + str(self.puzzle.id) + '/')

    def test_page_title_and_headers(self):
        self.assert_text_equals("//h2", "Scores for Puzzle #" + str(self.puzzle.id))