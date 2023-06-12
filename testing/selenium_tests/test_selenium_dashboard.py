from django.contrib.auth.models import User

from puzzles.models import WordPuzzle
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class DashboardTests(BaseSeleniumTestCase):
    password = 'secretkey'
    target_page = "/"

    PAGE_TITLE = "//div[@class='page-title']"
    NOTIFICATIONS_SECTION = "//div[contains(@class,'boxed-panel')]/div[@class='subtitle']"
    NOTICE_TEXT = "//div[contains(@class,'boxed-panel')]/div[contains(@class,'note-text')]"
    DRAFT_PUZZLES_COUNT = "//div[contains(@class,'boxed-panel')]/div[contains(@class,'note-text')]//a"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)
        self.set_mobile_size(True)

    def test_redirect_to_login_if_user_is_not_authenticated(self):
        self.logout_user()
        self.get(self.target_page)
        self.assert_current_url('/login?next=/')

    def test_Dashboard_has_notifications_section(self):
        self.get('/')
        self.assert_text_equals(self.PAGE_TITLE, "Dashboard")
        self.assert_text_equals(self.NOTIFICATIONS_SECTION, "Notifications")
        self.assert_text_equals(self.NOTICE_TEXT, "No notifications to report")

    def test_Dashboard_has_draft_puzzles_notification_with_link(self):
        WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
        self.get('/')
        self.assert_text_equals(self.NOTICE_TEXT, "You have 1 draft puzzle(s) to complete")
        self.do_click(self.DRAFT_PUZZLES_COUNT)
        self.assert_current_url('/my_puzzles')

# class DraftPuzzlesTests(BaseSeleniumTestCase):
#     password = 'secretkey'
#
#     def setUp(self):
#         self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
#         self.auto_login_user(self.user)
#
#     def test_New_Puzzle_button_creates_puzzle_and_loads_edit_puzzle_page(self):
#         self.get('/')
#         self.do_click("//a[@id='btnNewPuzzle']")
#         # Creates puzzle and redirects to edit puzzle page
#         puzzle_id = WordPuzzle.objects.all()[0].id
#         self.assert_current_url('/edit_puzzle/' + str(puzzle_id) + '/')
#         self.assert_text_equals("//h2", "Edit Puzzle #" + str(puzzle_id))
#
#     def test_Dashboard_displays_users_draft_puzzle_badge_with_details(self):
#         puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
#         self.get('/')
#         self.assert_item_count("//div[contains(@class,'badge badge')]", 1)
#         badge_header = "Puzzle #" + str(puzzle.id) + ": 0 Non-cryptic Clues [0 pts]"
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/a", badge_header)
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/div[1]", puzzle.desc)
#         last_edited_str = 'Last edited: ' + puzzle.modified_at.strftime('%b %d, %Y %I:%M %p') + ' (GMT)'
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/div[2]", last_edited_str)
#
#     def test_Puzzle_badge_header_link_redirects_to_edit_puzzle_page(self):
#         puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
#         self.get('/')
#         self.do_click("//div[contains(@class,'badge badge')]/a")  # Puzzle title as link
#         self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')
#         self.assert_text_equals("//h2", "Edit Puzzle #" + str(puzzle.id))
#
#     def test_Preview_Puzzle_button_is_not_visible_if_draft_puzzle_has_no_clues(self):
#         WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
#         self.get('/')
#         self.assert_not_exists("//a[@title='Preview & Publish']")
#
#     def test_Preview_Puzzle_button_redirects_to_preview_page_if_draft_puzzle_has_clues(self):
#         puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
#         puzzle.add_clue({'answer': "WORDLE", 'clue_text': "Clue for word", 'points': 1})
#         self.get('/')
#         self.do_click("//a[@title='PREVIEW & PUBLISH']")
#         self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + '/')
#
#
# class RecentPuzzlesTests(BaseSeleniumTestCase):
#     password = 'secretkey'
#
#     def setUp(self):
#         self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
#         self.auto_login_user(self.user)
#
#     def test_recent_puzzles_section_offers_button_to_all_puzzles_page(self):
#         self.get('/')
#         self.assert_exists("//div/a[text()='SHOW ALL PUZZLES']")
#
#     def test_recent_puzzles_show_title_desc_and_posted_by_with_date(self):
#         other_user = User.objects.create_user(username="other_user", password="secretkey")
#         puzzle = create_published_puzzle(editor=other_user, desc="Puzzle description")
#         self.get('/')
#         badge_header = "Puzzle #" + str(puzzle.id) + ": 1 Non-cryptic Clues [1 pts]"
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/a[1]", badge_header)
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/div[1]", puzzle.desc)
#         posted_by_str = 'Posted by: ' + str(puzzle.editor) + ' on ' + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/div[2]", posted_by_str)
#
#     def test_recent_puzzles_shows_rounded_badge_for_session_count(self):
#         user2 = create_user(username="user2")
#         user3 = create_user(username="user3")
#         puzzle1 = create_published_puzzle(editor=user2, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
#         puzzle2 = create_published_puzzle(editor=user3, desc="Daily Puzzle 2", clues_pts=[1, 1])
#         create_session(solver=self.user, puzzle=puzzle2)
#         create_session(solver=user2, puzzle=puzzle2)
#         self.get('/')
#         self.assert_text_equals("//div/div/div[contains(@class,'rounded-circle')]", '0', 0)
#         self.assert_text_equals("//div/div/div[contains(@class,'rounded-circle')]", '2', 1)
#         self.assert_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")
#
#     def test_recent_puzzle_shows_no_flag_if_current_user_session_has_no_session(self):
#         other_user = create_user(username="other_user")
#         puzzle = create_published_puzzle(editor=self.user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
#         create_session(solver=other_user, puzzle=puzzle)
#         self.get('/')
#         self.assert_not_exists("//div/div/div/i[contains(@class,'fa-flag')]")
#         self.assert_text_equals("//div/div/div[contains(@class,'rounded-circle')]", '1')
#
#     def test_recent_puzzle_shows_red_flag_if_current_user_session_has_incomplete_session(self):
#         other_user = create_user(username="other_user")
#         puzzle = create_published_puzzle(editor=other_user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
#         create_session(solver=self.user, puzzle=puzzle)
#         self.get('/')
#         self.assert_exists("//div/div/div/i[contains(@class,'fa-flag text-danger')]")
#         self.assert_text_equals("//div/div/div[contains(@class,'rounded-circle')]", '1')
#
#     def test_recent_puzzle_shows_green_flag_if_current_user_session_has_complete_session(self):
#         other_user = create_user(username="other_user")
#         puzzle = create_published_puzzle(editor=other_user, desc="Daily Puzzle 1", clues_pts=[1, 2, 2])
#         create_session(solver=self.user, puzzle=puzzle, solved_clues='1,2,3')
#         self.get('/')
#         self.assert_exists("//div/div/div/i[contains(@class,'fa-flag text-success')]")
#         self.assert_text_equals("//div/div/div[contains(@class,'rounded-circle')]", '1')
#
#     def test_shows_ME_for_posted_by_if_editor_is_current_user(self):
#         puzzle = create_published_puzzle(editor=self.user, desc="Puzzle description")
#         self.get('/')
#         badge_header = "Puzzle #" + str(puzzle.id) + ": 1 Non-cryptic Clues [1 pts]"
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/a[1]", badge_header)
#         posted_by_str = 'Posted by: ME on ' + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
#         self.assert_text_equals("//div[contains(@class,'badge badge')]/div[2]", posted_by_str)
#
#     def test_puzzle_title_links_to_preview_page_if_editor_is_current_user(self):
#         puzzle = create_published_puzzle(editor=self.user)
#         self.get('/')
#         self.assert_not_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")
#         view_icon_btn = self.get_element("//a[@title='VIEW']/i[contains(@class,'fa-eye')]")
#         view_icon_btn.click()
#         self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")
#
#     def test_puzzle_title_links_to_solve_puzzle_page_if_user_is_not_editor(self):
#         other_user = User.objects.create_user(username="other_user")
#         puzzle = create_published_puzzle(editor=other_user)
#         self.get('/')
#         self.assert_not_exists("//a[@title='SCORES']/i[contains(@class,'fa-crown')]")
#         solve_icon_btn = self.get_element("//a[@title='SOLVE']/i[contains(@class,'fa-hourglass-2')]")
#         solve_icon_btn.click()
#         self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")
#
#     def test_all_Puzzles_button_links_to_all_puzzles_page(self):
#         self.get('/')
#         self.do_click("//a[text()='SHOW ALL PUZZLES']")
#         self.assert_current_url("/puzzles_list")
#         self.assert_text_equals("//div/h2", 'All Published Puzzles')
