from django.contrib.auth.models import User
from django.utils.timezone import now

from puzzles.models import WordPuzzle
from testing.django_unit_tests.unit_test_helpers import create_published_puzzle
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class SolvePuzzleTests(SeleniumTestCase):
    password = 'secretkey'

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.other_user = User.objects.create_user(username="other_user", password=self.password)
        self.login_user(username=self.user.username, password=self.password)

    def test_Page_title_and_basic_info(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[2,1,3,4])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//div/h2", 'Solve Puzzle')
        post_on = "Posted by: " + str(self.other_user) + " on " + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_xpath_text("//div/h6[1]", post_on)
        self.assert_xpath_text("//div/h6[2]", "Description: " + puzzle.desc)
        self.assert_xpath_text("//div/div/div//h5", "Clues: [0 points earned of 10]")
        self.assert_xpath_items("//div//", 4)
