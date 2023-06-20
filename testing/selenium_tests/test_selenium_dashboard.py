from datetime import timedelta

from django.contrib.auth.models import User

from puzzles.models import WordPuzzle
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase


class DashboardTests(BaseSeleniumTestCase):
    password = 'secretkey'
    target_page = "/"
    SECTION_NOTICE_TEXT = "//div[contains(@class,'boxed-panel')]/div[contains(@class,'note-text')]"
    CREATE_PUZZLE_BTN = "//button[@id='btnCreatePuzzle']"
    NEW_PUZZLE_DIALOG = "//dialog[@id='new-puzzle-dialog']"
    DIALOG_SUBTITLE = "//dialog[@id='new-puzzle-dialog']/div[@class='subtitle']"
    DIALOG_FORM = "//dialog[@id='new-puzzle-dialog']/form"
    DIALOG_SUBMIT_BTN = "//dialog[@id='new-puzzle-dialog']//button[@type='submit']"
    DIALOG_CLOSE_BTN = "//dialog[@id='new-puzzle-dialog']//button[@id='btnClose']"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)
        self.set_mobile_size(True)

    def test_notifications_section_without_notificatons(self):
        self.get(self.target_page)
        self.assert_page_title("Dashboard")
        self.assert_subtitle("My Notifications", 0)
        self.assert_text_equals(self.SECTION_NOTICE_TEXT, "No notifications to report.", 0)

    def test_draft_puzzles_section_with_no_puzzles(self):
        self.get(self.target_page)
        self.assert_subtitle("My Draft Puzzles", 1)
        self.assert_text_equals(self.SECTION_NOTICE_TEXT, "No draft puzzles.", 1)

    def test_create_puzzle_btn_shows_modal_dialog_that_can_be_canceled(self):
        self.get(self.target_page)
        self.assert_text_equals(self.CREATE_PUZZLE_BTN, "Create Puzzle")
        self.assert_is_not_displayed(self.NEW_PUZZLE_DIALOG)
        self.do_click(self.CREATE_PUZZLE_BTN)
        self.assert_is_displayed(self.NEW_PUZZLE_DIALOG)
        # Validate new puzzle dialog contents
        self.assert_text_equals(self.DIALOG_SUBTITLE, "New Puzzle")
        self.assert_exists(self.DIALOG_FORM)
        self.assert_text_equals(self.DIALOG_SUBMIT_BTN, "Create Puzzle")
        self.assert_text_equals(self.DIALOG_CLOSE_BTN, "Cancel")
        self.do_click(self.DIALOG_CLOSE_BTN)
        self.assert_is_not_displayed(self.NEW_PUZZLE_DIALOG)


class DraftPuzzlesTests(BaseSeleniumTestCase):
    password = 'secretkey'
    target_page = '/'

    NEW_PUZZLE_DIALOG = "//dialog[@id='new-puzzle-dialog']"
    TYPE_FIELD = "//dialog[@id='new-puzzle-dialog']//select[@id='id_type']"
    DESC_FIELD = "//dialog[@id='new-puzzle-dialog']//textarea[@id='id_desc']"
    CREATE_PUZZLE_BTN = "//button[@id='btnCreatePuzzle']"
    DIALOG_SUBMIT_BTN = "//dialog[@id='new-puzzle-dialog']//button[@type='submit']"
    DIALOG_CLOSE_BTN = "//dialog[@id='new-puzzle-dialog']//button[@id='btnClose']"
    DELETE_PUZZLE_ICON = "//div[contains(@class,'list-badge')]//i[@title='Delete']"
    DELETE_CONFIRM_BTN = "//button"
    LIST_BADGE = "//div[contains(@class,'list-badge')]"
    LIST_BADGE_TITLE = "//div[contains(@class,'list-badge')]/div/a[contains(@class,'bold-text')]"
    LIST_BADGE_NOTE = "//div[contains(@class,'list-badge')]//div[@class='font-xsmall']"
    LIST_BADGE_IMG = "//div[contains(@class,'list-badge')]//img"
    CONFIRM_DIALOG = "//dialog[@id='confirm-dialog']"
    CONFIRM_DIALOG_SUBTITLE = "//dialog[@id='confirm-dialog']/div[@class='subtitle']"
    CONFIRM_DIALOG_MSG = "//dialog[@id='confirm-dialog']//div[contains(@class,'confirm-dialog-message')]"
    CONFIRM_DIALOG_CLOSE_BTN = "//dialog[@id='confirm-dialog']//button[@id='btnClose']"
    CONFIRM_DIALOG_SUBMIT_BTN = "//dialog[@id='confirm-dialog']//button[@type='submit']"

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)

    def test_New_Puzzle_btn_creates_puzzle_and_redirects_to_edit_puzzle_page(self):
        self.get(self.target_page)
        self.do_click(self.CREATE_PUZZLE_BTN)
        self.set_input_text(self.DESC_FIELD, "Instructions")
        self.select_by_text(self.TYPE_FIELD, "Non-cryptic Clues")
        self.do_click(self.DIALOG_SUBMIT_BTN)
        new_puzzle = WordPuzzle.objects.all()[0]
        self.assertEqual("Instructions", new_puzzle.desc)
        self.assertEqual(0, new_puzzle.type)
        self.assert_current_url('/edit_puzzle/' + str(new_puzzle.id) + '/')
        self.assert_subtitle(str(new_puzzle))

    def test_draft_puzzles_details(self):
        puzzle1 = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle2 = WordPuzzle.objects.create(editor=self.user, type=1)
        puzzle2.modified_at = puzzle2.modified_at + timedelta(seconds=60)  # to ensure puzzle 2 is newer
        puzzle2.save()
        self.get(self.target_page)
        self.assert_item_count(self.LIST_BADGE, 2)
        badge1_title = "Puzzle " + str(puzzle1.id) + ": 0 Non-cryptic Clues [0 pts]"
        badge2_title = "Puzzle " + str(puzzle2.id) + ": 0 Cryptic Clues [0 pts]"
        self.assert_text_equals(self.LIST_BADGE_TITLE, badge2_title, 0)  # Puzzle 2 listed first
        self.assert_text_equals(self.LIST_BADGE_TITLE, badge1_title, 1)
        self.assert_attribute_contains(self.LIST_BADGE_IMG, 'src', 'non-cryptic-clues.png', 1)
        self.assert_attribute_contains(self.LIST_BADGE_IMG, 'src', 'cryptic-clues.jpg', 0)
        self.assert_attribute_contains(self.LIST_BADGE_TITLE, 'href', '/edit_puzzle/' + str(puzzle1.id) + '/', 1)
        self.assert_attribute_contains(self.LIST_BADGE_TITLE, 'href', '/edit_puzzle/' + str(puzzle2.id) + '/', 0)
        last_edited_str1 = 'Last edited on ' + self.utc_to_local(puzzle1.modified_at)
        last_edited_str2 = 'Last edited on ' + self.utc_to_local(puzzle2.modified_at)
        self.assert_text_equals(self.LIST_BADGE_NOTE, last_edited_str2, 0)
        self.assert_text_equals(self.LIST_BADGE_NOTE, last_edited_str1, 1)

    def test_badge_header_link_redirects_to_edit_puzzle_page(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
        self.get(self.target_page)
        self.do_click(self.LIST_BADGE_TITLE)  # Puzzle title as link
        self.assert_current_url('/edit_puzzle/' + str(puzzle.id) + '/')

    def test_Delete_Puzzle_button_within_badge_shows_confirm_dialog(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=1, desc="Some description")
        self.get(self.target_page)
        self.do_click(self.DELETE_PUZZLE_ICON)  # DELETE icon on puzzle badge
        self.selenium.implicitly_wait(1)
        self.assertTrue(self.modal_dialog_open("confirm-dialog"))
        # Validate confirm dialog contents
        self.assert_text_equals(self.CONFIRM_DIALOG_SUBTITLE, "Delete Puzzle 1")
        self.assert_text_contains(self.CONFIRM_DIALOG_MSG, "This puzzle and all associated")
        self.assert_text_equals(self.CONFIRM_DIALOG_CLOSE_BTN, "Cancel")
        self.do_click(self.CONFIRM_DIALOG_CLOSE_BTN)
        self.selenium.implicitly_wait(1)
        self.assertFalse(self.modal_dialog_open("confirm-dialog"))
        self.assert_current_url(self.target_page)
        self.assert_item_count(self.LIST_BADGE, 1)  # Puzzle still exists

    def test_Delete_Puzzle_button_deletes_puzzle_after_confirmation(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
        self.get(self.target_page)
        self.do_click(self.DELETE_PUZZLE_ICON)
        self.selenium.implicitly_wait(1)
        self.assertTrue(self.modal_dialog_open("confirm-dialog"))
        self.do_click(self.CONFIRM_DIALOG_SUBMIT_BTN)  # Delete button on delete confirm dialog
        self.selenium.implicitly_wait(1)
        self.assertFalse(self.modal_dialog_open("confirm-dialog"))
        self.assert_current_url(self.target_page)
        self.assert_item_count(self.LIST_BADGE, 0)  # Puzzle deleted

    # def test_Preview_Puzzle_button_is_not_visible_if_draft_puzzle_has_no_clues(self):
    #     WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
    #     self.get('/')
    #     self.assert_not_exists("//a[@title='Preview & Publish']")
    #
    # def test_Preview_Puzzle_button_redirects_to_preview_page_if_draft_puzzle_has_clues(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description")
    #     puzzle.add_clue({'answer': "WORDLE", 'clue_text': "Clue for word", 'points': 1})
    #     self.get('/')
    #     self.do_click("//a[@title='PREVIEW & PUBLISH']")
    #     self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + '/')

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
