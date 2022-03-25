from django.contrib.auth.models import User
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase

from testing.django_unit_tests.unit_test_helpers import create_published_puzzle, create_session


class SolvePuzzleTests(SeleniumTestCase):
    user = None
    password = 'secret_key'

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.login_user(username=self.user.username, password=self.password)
        self.other_user = User.objects.create_user(username="other_user", password=self.password)

    def test_Displays_previous_session_state(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[5, 2, 3, 1, 2])
        session = create_session(solver=self.user, puzzle=puzzle, solved_clues='1,4', revealed_clues='5')
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Solve Puzzle")
        solved_clues = session.get_solved_clue_nums()
        revealed_clues = session.get_revealed_clue_nums()
        for index, clue in enumerate(puzzle.get_clues()):
            clue_btn = self.get_element("//div/button[@id='clue-btn-" + str(index + 1) + "']")
            if clue.clue_num in solved_clues:
                self.assertIn('btn-success', clue_btn.get_attribute('class'))
            elif clue.clue_num in revealed_clues:
                self.assertIn('btn-secondary', clue_btn.get_attribute('class'))
            else:
                self.assertNotIn('btn-success', clue_btn.get_attribute('class'))
                self.assertNotIn('btn-secondary', clue_btn.get_attribute('class'))
        self.assert_text_equals("//div[@id='id-score']", "Score: 6 pts")
