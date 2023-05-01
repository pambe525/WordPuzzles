from selenium.webdriver.support.wait import WebDriverWait

from puzzles.models import WordPuzzle
from testing.data_setup_utils import create_draft_puzzle, create_published_puzzle, create_user
from testing.selenium_tests.selenium_helper_mixin import BaseSeleniumTestCase
from selenium.webdriver.support import expected_conditions as EC

class PreviewPuzzleTests(BaseSeleniumTestCase):

    def setUp(self):
        self.user = create_user()
        self.auto_login_user(self.user)
        self.other_user = create_user(username="other_user")

    def test_draft_puzzle_editor_can_preview_with_no_desc_and_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Publish")
        self.assert_text_equals("//h4", str(puzzle))
        self.assert_not_exists("//h6[@id='id-posted-by']")  # No Posted by (since it is draft)
        self.assert_not_exists("//h6[@id='id-desc']")       # No description
        self.assert_not_exists("//a[text()='PUBLISH']")     # No Publish button
        self.assert_not_exists("//a[text()='UNPUBLISH']")   # No Unpublish button
        self.assert_not_exists("//a[text()='SOLVE NOW']")   # No Solve button
        self.assert_text_equals("//div[contains(@class,'notetext')]", "No clues exist.")
        self.assert_item_count("//div[contains(@class,'notetext')]", 1)
        self.do_click("//a[text()='BACK']")
        self.assert_current_url("/")

    def test_draft_puzzle_editor_can_preview_puzzle_with_desc_and_clue(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description of clue")
        puzzle.add_clue({'answer': "WORD-A", 'clue_text': "Some clue", 'points': 2})
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Publish")
        self.assert_text_equals("//h4", str(puzzle))
        self.assert_not_exists("//h6[@id='id-posted-by']")  # No Posted by (since it is draft)
        self.assert_text_equals("//h6[@id='id-desc']", "Description: " + puzzle.desc)
        self.verify_button_states_for_editor_mode("DRAFT")
        self.assert_not_exists("//div[contains(text, 'No clues exist')]")
        self.do_click("//a[text()='BACK']")
        self.assert_current_url("/")

    def test_draft_puzzle_editor_can_publish_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_contains("//div[contains(@class,'notetext')][1]", "NOTE: Publish your puzzle only")
        self.do_click("//a[text()='PUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertTrue(updated_puzzle.is_published())
        self.assert_current_url('/')

    def test_draft_puzzle_preview_shows_each_clue_with_answer_and_parsing(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[2, 1, 3, 4], has_parsing=True)
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//div/div/div//h5", "Clues")
        self.assert_text_equals("//table/thead/tr", "# Description Pts")
        self.assert_not_exists("//div[contains(text(),'Click on a clue below')]")
        for index, clue in enumerate(puzzle.get_clues()):
            tr_xpath = "//table/tbody/tr/"
            self.assert_text_equals(tr_xpath+"td[1]", "", index)
            self.assert_text_equals(tr_xpath+"td[2]", str(clue.clue_num) + ".", index)
            self.assert_text_equals(tr_xpath+"td[3]/div[1]", clue.get_decorated_clue_text(), index)
            self.assert_text_equals(tr_xpath+"td[4]", str(clue.points), index)
            self.assert_text_equals(tr_xpath+"td[3]/div[2]", "["+clue.parsing+"]", index)
            self.assert_value_equals(tr_xpath+"td[3]/input", clue.answer, index)

    def test_draft_puzzle_preview_clues_are_not_clickable(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[2, 1, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        for index, clue in enumerate(puzzle.get_clues()):
            tr_xpath = "//table/tbody/tr/"
            element = self.get_element(tr_xpath+"td[3]", index)
            self.assertIsNone(element.get_attribute('onclick'))

    def test_draft_puzzle_preview_shows_error_for_non_editor(self):
        puzzle = create_draft_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')  # Current user is NOT editor
        self.assert_text_equals("//div[@id='errMsg']", "This operation is not permitted since you are not the editor.")

    def test_published_puzzle_editor_preview_shows_posted_by(self):
        puzzle = create_published_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Unpublish")
        self.assert_text_equals("//h4", str(puzzle))
        posted_by_str = 'Posted by: ' + str(self.user) + ' on ' + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_text_equals("//h6[@id='id-posted-by']", posted_by_str)
        self.assert_not_exists("//a[text()='PUBLISH']")

    def test_published_puzzle_editor_can_unpublish_puzzle(self):
        puzzle = create_published_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_contains("//div[contains(@class,'notetext')][1]", "NOTE: Unpublish your puzzle")
        self.do_click("//a[text()='UNPUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)
        self.assert_current_url('/')

    def test_published_puzzle_can_be_viewed_by_non_editor(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Description", clues_pts=[2, 2, 3],
                                         has_parsing=True)
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Solve")
        self.assert_text_equals("//h4", str(puzzle))
        posted_by_str = 'Posted by: ' + str(self.other_user) + ' on ' + puzzle.shared_at.strftime(
            '%b %d, %Y') + ' (GMT)'
        self.assert_text_equals("//h6[@id='id-posted-by']", posted_by_str)
        self.verify_button_states_for_non_editor_mode()

    def test_published_puzzle_preview_by_non_editor_hides_points_and_answers(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_not_exists("//div[contains(text(),'Click on a clue below')]")
        for index, clue in enumerate(puzzle.get_clues()):
            tr_xpath = "//table/tbody/tr/"
            self.assert_text_equals(tr_xpath+"td[1]", "", index)
            self.assert_text_equals(tr_xpath+"td[2]", str(clue.clue_num) + ".", index)
            self.assert_text_equals(tr_xpath+"td[3]/div[1]", clue.get_decorated_clue_text(), index)
            self.assert_exists(tr_xpath+"td[4]/i[@class='fa fa-eye-slash']")
            self.assert_not_exists(tr_xpath+"td[3]/div[2]")
            self.assert_not_exists(tr_xpath+"td[3]/input")

    def test_published_puzzle_preview_clues_are_not_clickable_by_non_editor(self):
        puzzle = create_published_puzzle(editor=self.other_user, clues_pts=[2, 1, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        for index, clue in enumerate(puzzle.get_clues()):
            tr_xpath = "//table/tbody/tr/"
            element = self.get_element(tr_xpath+"td[3]", index)
            self.assertIsNone(element.get_attribute('onclick'))

    def test_solve_button_starts_solve_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//a[text()='SOLVE NOW']")
        self.assert_text_equals("//h2", "Solve Puzzle")
        self.verify_button_states_for_solve_mode()

    #==================================================================================================================
    # HELPER METHODS
    def verify_button_states_for_solve_mode(self):
        self.assert_not_exists("//a[text()='PUBLISH']")    # No PUBLISH button
        self.assert_not_exists("//a[text()='UNPUBLISH']")  # No UNPUBLISH button
        self.assert_not_exists("//a[text()='SOLVE NOW']")  # No SOLVE NOW button
        self.assert_is_not_displayed("//a[text()='BACK']") # No BACK button
        self.assert_is_displayed("//a[@id='id-finish-later-btn']")  # Only FINISH LATER button

    def verify_button_states_for_editor_mode(self, mode):
        if mode == 'DRAFT':
            self.assert_exists("//a[text()='PUBLISH']")        # PUBLISH button
            self.assert_not_exists("//a[text()='UNPUBLISH']")  # No UNPUBLISH button
        else:
            self.assert_not_exists("//a[text()='PUBLISH']")    # No PUBLISH button
            self.assert_exists("//a[text()='UNPUBLISH']")      # UNPUBLISH button
        self.assert_not_exists("//a[text()='SOLVE NOW']")      # No SOLVE NOW button
        self.assert_exists("//a[text()='BACK']")               # BACK button
        self.assert_not_exists("//a[@id='id-finish-later-btn']")  # No FINISH LATER button

    def verify_button_states_for_non_editor_mode(self):
        self.assert_not_exists("//a[text()='PUBLISH']")        # No PUBLISH button
        self.assert_not_exists("//a[text()='UNPUBLISH']")      # No UNPUBLISH button
        self.assert_exists("//a[text()='SOLVE NOW']")          # SOLVE NOW button
        self.assert_exists("//a[text()='BACK']")               # BACK button
        self.assert_not_exists("//a[@id='id-finish-later-btn']")  # No FINISH LATER button