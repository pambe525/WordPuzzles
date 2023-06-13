from unittest.case import skip

from django.contrib.auth.models import User

from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle, create_user, create_session
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


@skip
class PuzzlesListTests(BaseSeleniumTestCase):
    password = 'secretkey'

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)
        self.other_user = User.objects.create_user(username='testuser2')

    def test_Page_title_and_sort_form(self):
        self.get('/puzzles_list')
        self.assert_text_equals("//div/h2", 'All Published Puzzles')
        self.assert_exists("//select[1]")
        self.assert_attribute_equals("//select[1]", "shared_at")
        self.assert_exists("//select[2]")
        self.assert_attribute_equals("//select[2]", '-')

    def test_each_published_puzzle_detail_is_listed(self):
        create_draft_puzzle(editor=self.user)
        puzzle = create_published_puzzle(editor=self.other_user, desc="puzzle desc")
        self.get('/puzzles_list')
        self.assert_item_count("//table/tbody/tr", 1)
        self.assert_text_contains("//table/tbody/tr[1]/td[1]", str(puzzle))
        post_on = "Posted by: " + str(self.other_user) + " on " + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_text_contains("//table/tbody/tr[1]/td[1]", post_on)
        self.assert_exists("//table/tbody/tr[1]/td[1]//a[@title='" + puzzle.desc + "']")

    def test_shows_ME_for_posted_by_if_editor_is_current_user(self):
        puzzle = create_published_puzzle(editor=self.user, type=0, desc="Puzzle description")
        self.get('/puzzles_list')
        post_on = "Posted by: ME on " + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_text_contains("//table/tbody/tr[1]/td[1]", post_on)

    def test_puzzle_title_links_to_preview_page_if_editor_is_current_user(self):
        puzzle = create_published_puzzle(editor=self.user, type=0, desc="Puzzle description", clues_pts=[1])
        self.get('/puzzles_list')
        self.do_click("//table/tbody/tr[1]/td[1]/a")
        self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")

    def test_puzzle_view_icon_links_to_preview_page_if_editor_is_current_user(self):
        puzzle = create_published_puzzle(editor=self.user, type=0, desc="Puzzle description", clues_pts=[1])
        create_session(puzzle=puzzle, solver=self.user, solved_clues='1')
        self.get('/puzzles_list')
        self.assert_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")
        view_icon_btn = self.get_element("//a[@title='VIEW']/i[contains(@class,'fa-eye')]")
        view_icon_btn.click()
        self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")

    def test_puzzle_title_links_to_preview_page_if_editor_is_not_current_user(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2])
        self.get('/puzzles_list')
        self.do_click("//table/tbody/tr[1]/td[1]/a")
        self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")

    def test_puzzle_solve_icon_links_to_preview_page_if_editor_is_not_current_user(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2])
        self.get('/puzzles_list')
        self.assert_not_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")  # No users solving
        solve_icon_btn = self.get_element("//a[@title='SOLVE']/i[contains(@class,'fa-hourglass-2')]")
        solve_icon_btn.click()
        self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")

    def test_sort_form_reflects_get_parameters_in_url(self):
        self.get('/puzzles_list?sort_by=total_points&order=')
        self.assert_text_equals("//div/h2", 'All Published Puzzles')
        self.assert_attribute_equals("//select[1]", "total_points")
        self.assert_attribute_equals("//select[2]", '')

    def test_selecting_sort_by_description_submits_form_with_correct_url(self):
        self.get('/puzzles_list')
        self.select_by_text("//select[1]", "Description")
        self.assert_current_url("/puzzles_list?sort_by=desc&order=-")
        self.assert_text_equals("//div/h2", 'All Published Puzzles')
        self.assert_attribute_equals("//select[1]", "desc")
        self.assert_attribute_equals("//select[2]", '-')

    def test_selecting_sort_by_editor_submits_form_with_correct_url(self):
        self.get('/puzzles_list')
        self.select_by_text("//select[1]", "Editor")
        self.select_by_text("//select[2]", "Ascending")
        self.assert_current_url("/puzzles_list?sort_by=editor__username&order=")
        self.assert_text_equals("//div/h2", 'All Published Puzzles')
        self.assert_attribute_equals("//select[1]", "editor__username")
        self.assert_attribute_equals("//select[2]", '')

    def test_selecting_sort_by_size_submits_form_with_correct_url(self):
        self.get('/puzzles_list')
        self.select_by_text("//select[1]", "No. of Clues")
        self.assert_current_url("/puzzles_list?sort_by=size&order=-")
        self.assert_attribute_equals("//select[1]", "size")
        self.assert_attribute_equals("//select[2]", '-')

    def test_selecting_sort_by_id_submits_form_with_correct_url(self):
        self.get('/puzzles_list')
        self.select_by_text("//select[1]", "Puzzle #")
        self.assert_current_url("/puzzles_list?sort_by=id&order=-")
        self.assert_attribute_equals("//select[1]", "id")
        self.assert_attribute_equals("//select[2]", '-')

    def test_selecting_sort_by_type_submits_form_with_correct_url(self):
        self.get('/puzzles_list')
        self.select_by_text("//select[1]", "Puzzle Type")
        self.assert_current_url("/puzzles_list?sort_by=type&order=-")
        self.assert_attribute_equals("//select[1]", "type")
        self.assert_attribute_equals("//select[2]", '-')

    def test_selecting_sort_by_total_points_submits_form_with_correct_url(self):
        self.get('/puzzles_list')
        self.select_by_text("//select[1]", "Total Points")
        self.assert_current_url("/puzzles_list?sort_by=total_points&order=-")
        self.assert_attribute_equals("//select[1]", "total_points")
        self.assert_attribute_equals("//select[2]", '-')

    def test_puzzles_shows_rounded_badge_containing_session_count(self):
        user2 = create_user(username="user2")
        user3 = create_user(username="user3")
        puzzle1 = create_published_puzzle(editor=user2, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
        puzzle2 = create_published_puzzle(editor=user3, desc="Daily Puzzle 2", clues_pts=[1, 1])
        create_session(solver=self.user, puzzle=puzzle2)
        create_session(solver=user2, puzzle=puzzle2)
        self.get('/puzzles_list')
        self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '0')
        self.assert_text_equals("//tr[2]/td[2]/div/div[contains(@class,'rounded-circle')]", '2')
        self.assert_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")

    def test_puzzle_shows_no_flag_if_current_user_session_has_no_session(self):
        other_user = create_user(username="other_user")
        puzzle = create_published_puzzle(editor=self.user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
        create_session(solver=other_user, puzzle=puzzle)
        self.get('/puzzles_list')
        self.assert_not_exists("//tr[1]/td[2]/div/div/i[contains(@class,'fa-flag')]")
        self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '1')

    def test_puzzle_shows_red_flag_if_current_user_session_has_incomplete_session(self):
        other_user = create_user(username="other_user")
        puzzle = create_published_puzzle(editor=other_user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
        create_session(solver=self.user, puzzle=puzzle)
        self.get('/puzzles_list')
        self.assert_exists("//tr[1]/td[2]/div/div/i[contains(@class,'fa-flag text-danger')]")
        self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '1')

    def test_puzzle_shows_green_flag_if_current_user_session_has_complete_session(self):
        other_user = create_user(username="other_user")
        puzzle = create_published_puzzle(editor=other_user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
        create_session(solver=self.user, puzzle=puzzle, solved_clues='1,2,3')
        self.get('/puzzles_list')
        self.assert_exists("//tr[1]/td[2]/div/div/i[contains(@class,'fa-flag text-success')]")
        self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '1')