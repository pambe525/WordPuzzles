from django.contrib.auth.models import User

from testing.django_unit_tests.unit_test_helpers import create_published_puzzle, get_full_clue_desc
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class SolvePuzzleTests(SeleniumTestCase):
    password = 'secretkey'

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.other_user = User.objects.create_user(username="other_user", password=self.password)
        self.login_user(username=self.user.username, password=self.password)

    def test_Page_title_and_basic_info(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[2, 1, 3, 4])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.assert_xpath_text("//div/h2", 'Solve Puzzle')
        post_on = "Posted by: " + str(self.other_user) + " on " + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_xpath_text("//div/h6[1]", post_on)
        self.assert_xpath_text("//div/h6[2]", "Description: " + puzzle.desc)
        self.assert_xpath_text("//div/div/div//h5", "Clues")
        self.assert_xpath_items("//div//button[contains(@id,'clue-btn-')]", 4)

    def test_Clue_button_details(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[2, 1, 3, 4])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        for index, clue in enumerate(puzzle.get_clues()):
            clue_btn = self.get_xpath("//div/button[@id='clue-btn-" + str(index + 1) + "']")[0]
            self.assertEqual(clue_btn.text, str(clue.clue_num))
            tooltip = clue.get_decorated_clue_text() + " [" + str(clue.points) + " pts]"
            self.assertEqual(clue_btn.get_attribute('title'), tooltip)

    def test_First_clue_is_shown_in_clue_box_and_first_clue_btn_is_activated(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[3, 1, 2, 4])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        first_clue = puzzle.get_clues()[0]
        self.assert_xpath_text("//span[@id='id-clue']", get_full_clue_desc(first_clue))
        self.assert_xpath_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")

    def test_Clicking_on_a_clue_button_activates_it_and_shows_clue_text_in_clue_box(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3, 4, 5])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//div/button[@id='clue-btn-4']")
        fourth_clue = puzzle.get_clues()[3]
        self.assert_xpath_text("//span[@id='id-clue']", get_full_clue_desc(fourth_clue))
        self.assert_xpath_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")
        self.assert_xpath_not_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")

    def test_Clicking_on_right_caret_advances_to_next_clue(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3, 4, 5])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//div/button[@id='id-right-caret']")
        next_clue = puzzle.get_clues()[1]
        self.assert_xpath_text("//span[@id='id-clue']", get_full_clue_desc(next_clue))
        self.assert_xpath_exists("//button[@id='clue-btn-2'][contains(@class,'active')]")
        self.assert_xpath_not_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")

    def test_Clicking_on_right_caret_on_last_clue_advances_to_first_clue(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3, 4])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.click_btn("clue-btn-4")
        self.click_xpath("//div/button[@id='id-right-caret']")
        next_clue = puzzle.get_clues()[0]
        self.assert_xpath_text("//span[@id='id-clue']", get_full_clue_desc(next_clue))
        self.assert_xpath_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")
        self.assert_xpath_not_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")

    def test_Clicking_on_left_caret_advances_to_previous_clue(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[2, 1, 3, 4, 5])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.click_btn("clue-btn-4")   # Click on 4th clue btn
        self.click_xpath("//div/button[@id='id-left-caret']")
        prev_clue = puzzle.get_clues()[2]  # 3rd clue
        self.assert_xpath_text("//span[@id='id-clue']", get_full_clue_desc(prev_clue))
        self.assert_xpath_exists("//button[@id='clue-btn-3'][contains(@class,'active')]")
        self.assert_xpath_not_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")

    def test_Clicking_on_left_caret_on_first_clue_advances_to_last_clue(self):
        puzzle = create_published_puzzle(user=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3, 4])
        self.get('/solve_puzzle/' + str(puzzle.id) + '/')
        self.click_xpath("//div/button[@id='id-left-caret']")
        next_clue = puzzle.get_clues()[3]
        self.assert_xpath_text("//span[@id='id-clue']", get_full_clue_desc(next_clue))
        self.assert_xpath_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")
        self.assert_xpath_not_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")