import time

from django.contrib.auth.models import User

from puzzles.models import SolverSession
from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class PuzzlesListTests(BaseSeleniumTestCase):
    password = 'secretkey'
    target_page = '/puzzles_list'
    NO_PUZZLES = "//div[@class='note-text']"
    LIST_ITEM = "//div[contains(@class,'list-badge')]"
    LIST_ITEM_TITLE = "//div[contains(@class,'list-badge')]//a"
    LIST_ITEM_DESC = "//div[contains(@class,'list-badge')]/div/div[1]"
    LIST_ITEM_TIMESTAMP = "//div[contains(@class,'list-badge')]/div/div[2]"
    LIST_ITEM_STATUS_ICON = "//div[contains(@class,'list-badge')]/div[contains(@class,'icon-group')]//i[1]"
    LIST_ITEM_SCORES_LINK = "//div[contains(@class,'list-badge')]/div[contains(@class,'icon-group')]//a/i[1]"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)
        self.other_user = User.objects.create_user(username='other_user')

    def test_Page_title_and_empty_list(self):
        self.get(self.target_page)
        self.assert_page_title("Published Puzzles")
        self.assert_text_equals(self.NO_PUZZLES, "No published puzzles.")
        # self.assert_exists("//select[1]")
        # self.assert_attribute_equals("//select[1]", "shared_at")
        # self.assert_exists("//select[2]")
        # self.assert_attribute_equals("//select[2]", '-')

    def test_each_published_puzzle_detail_is_listed(self):
        create_draft_puzzle(editor=self.user)
        puzzle = create_published_puzzle(editor=self.other_user, desc="puzzle desc")
        self.get(self.target_page)
        self.assert_item_count(self.LIST_ITEM, 1)
        self.assert_text_equals(self.LIST_ITEM_TITLE, str(puzzle))
        self.assert_text_equals(self.LIST_ITEM_DESC, puzzle.desc)
        posted_on = "Posted by " + str(self.other_user) + " on " + self.utc_to_local(puzzle.shared_at)
        self.assert_text_equals(self.LIST_ITEM_TIMESTAMP, posted_on)

    def test_time_stamp_has_ME_and_links_to_edit_page_if_editor_is_current_user(self):
        puzzle = create_published_puzzle(editor=self.user, type=0, desc="Puzzle description", clues_pts=[1])
        self.get(self.target_page)
        posted_on = "Posted by ME on " + self.utc_to_local(puzzle.shared_at)
        self.assert_text_equals(self.LIST_ITEM_TIMESTAMP, posted_on)
        self.do_click(self.LIST_ITEM_TITLE)
        self.assert_current_url("/edit_puzzle/" + str(puzzle.id) + "/")

    def test_puzzle_title_links_to_solve_page_if_editor_is_not_current_user(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2])
        self.get(self.target_page)
        self.do_click(self.LIST_ITEM_TITLE)
        self.assert_current_url("/puzzle_session/" + str(puzzle.id) + "/")

    def test_puzzle_badge_has_status_icon_for_current_user_solver_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3])
        # No icon if no puzzle user session exists
        self.get(self.target_page)
        self.assert_not_exists(self.LIST_ITEM_STATUS_ICON)
        # Incomplete icon for incomplete user session
        session = SolverSession.new(puzzle, self.user)  # Incomplete session
        self.get(self.target_page)
        self.assert_attribute_contains(self.LIST_ITEM_STATUS_ICON, 'class', 'fa-circle-minus')
        self.assert_attribute_equals(self.LIST_ITEM_STATUS_ICON, 'title', 'Incomplete')
        # Completed icon for completed session
        clues = puzzle.get_clues()
        session.set_solved_clue(clues[0])
        session.set_solved_clue(clues[1])
        self.get(self.target_page)
        self.assert_attribute_contains(self.LIST_ITEM_STATUS_ICON, 'class', 'fa-circle-check')
        self.assert_attribute_equals(self.LIST_ITEM_STATUS_ICON, 'title', 'Completed')

    def test_puzzle_badge_has_link_to_scores_as_appropriate(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 3])
        self.get(self.target_page)
        # By default no link if no session exists
        self.assert_not_exists(self.LIST_ITEM_SCORES_LINK)
        # No link if only current user session exists
        session = SolverSession.new(puzzle, self.user)
        self.get(self.target_page)
        self.assert_not_exists(self.LIST_ITEM_SCORES_LINK)
        # Link to score exists if at least one other user session exists
        user3 = User.objects.create_user(username='user3', email="xyz@abc.com")
        session2 = SolverSession.new(puzzle, user3)
        self.get(self.target_page)
        self.assert_exists(self.LIST_ITEM_SCORES_LINK)
        self.do_click(self.LIST_ITEM_SCORES_LINK)
        self.assert_current_url("/puzzle_score/"+str(puzzle.id)+"/")



    # def test_sort_form_reflects_get_parameters_in_url(self):
    #     self.get('/puzzles_list?sort_by=total_points&order=')
    #     self.assert_text_equals("//div/h2", 'All Published Puzzles')
    #     self.assert_attribute_equals("//select[1]", "total_points")
    #     self.assert_attribute_equals("//select[2]", '')
    #
    # def test_selecting_sort_by_description_submits_form_with_correct_url(self):
    #     self.get('/puzzles_list')
    #     self.select_by_text("//select[1]", "Description")
    #     self.assert_current_url("/puzzles_list?sort_by=desc&order=-")
    #     self.assert_text_equals("//div/h2", 'All Published Puzzles')
    #     self.assert_attribute_equals("//select[1]", "desc")
    #     self.assert_attribute_equals("//select[2]", '-')
    #
    # def test_selecting_sort_by_editor_submits_form_with_correct_url(self):
    #     self.get('/puzzles_list')
    #     self.select_by_text("//select[1]", "Editor")
    #     self.select_by_text("//select[2]", "Ascending")
    #     self.assert_current_url("/puzzles_list?sort_by=editor__username&order=")
    #     self.assert_text_equals("//div/h2", 'All Published Puzzles')
    #     self.assert_attribute_equals("//select[1]", "editor__username")
    #     self.assert_attribute_equals("//select[2]", '')
    #
    # def test_selecting_sort_by_size_submits_form_with_correct_url(self):
    #     self.get('/puzzles_list')
    #     self.select_by_text("//select[1]", "No. of Clues")
    #     self.assert_current_url("/puzzles_list?sort_by=size&order=-")
    #     self.assert_attribute_equals("//select[1]", "size")
    #     self.assert_attribute_equals("//select[2]", '-')
    #
    # def test_selecting_sort_by_id_submits_form_with_correct_url(self):
    #     self.get('/puzzles_list')
    #     self.select_by_text("//select[1]", "Puzzle #")
    #     self.assert_current_url("/puzzles_list?sort_by=id&order=-")
    #     self.assert_attribute_equals("//select[1]", "id")
    #     self.assert_attribute_equals("//select[2]", '-')
    #
    # def test_selecting_sort_by_type_submits_form_with_correct_url(self):
    #     self.get('/puzzles_list')
    #     self.select_by_text("//select[1]", "Puzzle Type")
    #     self.assert_current_url("/puzzles_list?sort_by=type&order=-")
    #     self.assert_attribute_equals("//select[1]", "type")
    #     self.assert_attribute_equals("//select[2]", '-')
    #
    # def test_selecting_sort_by_total_points_submits_form_with_correct_url(self):
    #     self.get('/puzzles_list')
    #     self.select_by_text("//select[1]", "Total Points")
    #     self.assert_current_url("/puzzles_list?sort_by=total_points&order=-")
    #     self.assert_attribute_equals("//select[1]", "total_points")
    #     self.assert_attribute_equals("//select[2]", '-')
    #
    # def test_puzzles_shows_rounded_badge_containing_session_count(self):
    #     user2 = create_user(username="user2")
    #     user3 = create_user(username="user3")
    #     puzzle1 = create_published_puzzle(editor=user2, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
    #     puzzle2 = create_published_puzzle(editor=user3, desc="Daily Puzzle 2", clues_pts=[1, 1])
    #     create_session(solver=self.user, puzzle=puzzle2)
    #     create_session(solver=user2, puzzle=puzzle2)
    #     self.get('/puzzles_list')
    #     self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '0')
    #     self.assert_text_equals("//tr[2]/td[2]/div/div[contains(@class,'rounded-circle')]", '2')
    #     self.assert_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")
    #
    # def test_puzzle_shows_no_flag_if_current_user_session_has_no_session(self):
    #     other_user = create_user(username="other_user")
    #     puzzle = create_published_puzzle(editor=self.user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
    #     create_session(solver=other_user, puzzle=puzzle)
    #     self.get('/puzzles_list')
    #     self.assert_not_exists("//tr[1]/td[2]/div/div/i[contains(@class,'fa-flag')]")
    #     self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '1')
    #
    # def test_puzzle_shows_red_flag_if_current_user_session_has_incomplete_session(self):
    #     other_user = create_user(username="other_user")
    #     puzzle = create_published_puzzle(editor=other_user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
    #     create_session(solver=self.user, puzzle=puzzle)
    #     self.get('/puzzles_list')
    #     self.assert_exists("//tr[1]/td[2]/div/div/i[contains(@class,'fa-flag text-danger')]")
    #     self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '1')
    #
    # def test_puzzle_shows_green_flag_if_current_user_session_has_complete_session(self):
    #     other_user = create_user(username="other_user")
    #     puzzle = create_published_puzzle(editor=other_user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
    #     create_session(solver=self.user, puzzle=puzzle, solved_clues='1,2,3')
    #     self.get('/puzzles_list')
    #     self.assert_exists("//tr[1]/td[2]/div/div/i[contains(@class,'fa-flag text-success')]")
    #     self.assert_text_equals("//tr[1]/td[2]/div/div[contains(@class,'rounded-circle')]", '1')
