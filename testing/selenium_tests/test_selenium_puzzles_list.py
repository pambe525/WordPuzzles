import time
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils.timezone import now

from puzzles.models import SolverSession
from testing.data_setup_utils import create_published_puzzle, create_draft_puzzle, create_session
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class PuzzlesListTests(BaseSeleniumTestCase):
    password = 'secretkey'
    target_page = '/puzzles_list'
    NO_PUZZLES = "//div[@class='note-text']"
    FORM_SELECT = "//form/select"
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
        self.assert_text_equals(self.NO_PUZZLES, "No puzzles meet show filter criteria.")
        self.assert_exists(self.FORM_SELECT)
        self.assert_attribute_equals(self.FORM_SELECT, 'value', "all")

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
        self.assert_current_url("/puzzle_score/" + str(puzzle.id) + "/")

    def test_list_form_selection_change_changes_get_url(self):
        self.get(self.target_page + '?show=me_editor')
        self.assert_attribute_equals(self.FORM_SELECT, 'value', 'me_editor')
        self.select_by_text(self.FORM_SELECT, "Unfinished puzzles")
        self.assert_current_url(self.target_page + "?show=unfinished")

    def test_list_is_filtered_by_selection(self):
        user2 = User.objects.create(username="user2", email="xyx@uv.com")
        user3 = User.objects.create(username="user3", email="abc@uv.com")
        puzzle1 = create_published_puzzle(self.user, clues_pts=[1, 2, 1, 1, 1], posted_on=now() - timedelta(days=2))
        puzzle2 = create_published_puzzle(user2, clues_pts=[1, 1, 3, 1, 1], posted_on=now() - timedelta(days=5))
        puzzle3 = create_published_puzzle(user2, clues_pts=[1, 2, 1, 1, 1], posted_on=now() - timedelta(days=3))
        puzzle4 = create_published_puzzle(user2, clues_pts=[1, 1, 1, 2, 1], posted_on=now() - timedelta(days=1))
        create_session(puzzle2, self.user, 3, 2, 12)
        create_session(puzzle3, self.user, 3, 1, 10)
        create_session(puzzle4, user3, 2, 1, 8)
        self.get(self.target_page)  # Default os all puzzles
        self.assert_item_count(self.LIST_ITEM, 4)
        self.select_by_text(self.FORM_SELECT, "Unfinished puzzles")
        self.assert_item_count(self.LIST_ITEM, 1)
