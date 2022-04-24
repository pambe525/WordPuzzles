from django.contrib.auth.models import User

from puzzles.models import WordPuzzle
from testing.data_setup_utils import create_draft_puzzle, get_full_clue_desc, create_published_puzzle
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class PreviewPuzzleTests(SeleniumTestCase):
    user = None
    password = 'secret_key'

    def setUp(self):
        self.user = User.objects.create_user(username="test_user", email="user@test.com", password=self.password)
        self.auto_login_user(self.user)
        self.other_user = User.objects.create_user(username="other_user", password=self.password)

    def test_Draft_puzzle_editor_can_preview_with_no_desc_and_no_clues(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Publish")
        self.assert_text_equals("//h4", str(puzzle))
        self.assert_not_exists("//h6[@id='id-posted-by']")              # No Posted by (since it is draft)
        self.assert_not_exists("//h6[@id='id-desc']")                   # No description
        self.assert_not_exists("//a[text()='PUBLISH']")                 # No Publish button
        self.assert_not_exists("//a[text()='UNPUBLISH']")               # No Unpublish button
        self.assert_not_exists("//a[text()='SOLVE NOW']")               # No Solve button
        self.assert_text_equals("//div[contains(@class,'notetext')]", "No clues exist.")
        self.assert_item_count("//div[contains(@class,'notetext')]", 1)
        self.do_click("//a[text()='DONE']")
        self.assert_current_url("/")

    def test_Draft_puzzle_editor_can_preview_puzzle_with_desc_and_clue(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Some description of clue")
        puzzle.add_clue({'answer': "WORD-A", 'clue_text': "Some clue", 'points': 2})
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Publish")
        self.assert_text_equals("//h4", str(puzzle))
        self.assert_not_exists("//h6[@id='id-posted-by']")              # No Posted by (since it is draft)
        self.assert_text_equals("//h6[@id='id-desc']", "Description: " + puzzle.desc)
        self.assert_exists("//a[text()='PUBLISH']")                     # Publish button
        self.assert_not_exists("//a[text()='UNPUBLISH']")               # No Unpublish button
        self.assert_not_exists("//a[text()='SOLVE NOW']")               # No Solve button
        self.assert_not_exists("//div[contains(text, 'No clues exist')]")
        self.do_click("//a[text()='DONE']")
        self.assert_current_url("/")

    def test_Draft_puzzle_editor_can_publish_puzzle(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle.add_clue({'answer': 'WORD1', 'clue_text': 'Clue text 1', 'parsing': 'p1', 'points': 1})
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_contains("//div[contains(@class,'notetext')][2]", "NOTE: Publish your puzzle only")
        self.do_click("//a[text()='PUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertTrue(updated_puzzle.is_published())
        self.assert_current_url('/')

    def test_Shows_clue_button_for_each_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[2, 1, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//div/div/div//h5", "Clues")
        self.assert_item_count("//div//button[contains(@id,'clue-btn-')]", 4)

    def test_Clue_button_details(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[2, 1, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        for index, clue in enumerate(puzzle.get_clues()):
            clue_btn = self.get_element("//div/button[@id='clue-btn-" + str(index + 1) + "']")
            self.assertEqual(clue_btn.text, str(clue.clue_num))
            tooltip = clue.get_decorated_clue_text() + " [" + str(clue.points) + " pts]"
            self.assertEqual(clue_btn.get_attribute('title'), tooltip)

    def test_First_clue_is_shown_in_clue_box_and_first_clue_btn_is_activated(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[3, 1, 2, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        first_clue = puzzle.get_clues()[0]
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(first_clue))    # clue text
        self.assert_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")        # clue btn is active

    def test_Clicking_on_a_clue_button_activates_it_and_shows_clue_text_in_clue_box(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4, 5])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//div/button[@id='clue-btn-4']")
        fourth_clue = puzzle.get_clues()[3]
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(fourth_clue))
        self.assert_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")
        self.assert_not_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")

    def test_Clicking_on_right_caret_advances_to_next_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4, 5])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//div/button[@id='id-right-caret']")
        next_clue = puzzle.get_clues()[1]
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(next_clue))
        self.assert_exists("//button[@id='clue-btn-2'][contains(@class,'active')]")
        self.assert_not_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")

    def test_Clicking_on_right_caret_on_last_clue_advances_to_first_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//button[@id='clue-btn-4']")
        self.do_click("//div/button[@id='id-right-caret']")
        next_clue = puzzle.get_clues()[0]
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(next_clue))
        self.assert_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")
        self.assert_not_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")

    def test_Clicking_on_left_caret_advances_to_previous_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[2, 1, 3, 4, 5])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//button[@id='clue-btn-4']")   # Click on 4th clue btn
        self.do_click("//div/button[@id='id-left-caret']")
        prev_clue = puzzle.get_clues()[2]  # 3rd clue
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(prev_clue))
        self.assert_exists("//button[@id='clue-btn-3'][contains(@class,'active')]")
        self.assert_not_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")

    def test_Clicking_on_left_caret_on_first_clue_advances_to_last_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//div/button[@id='id-left-caret']")
        next_clue = puzzle.get_clues()[3]
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(next_clue))
        self.assert_exists("//button[@id='clue-btn-4'][contains(@class,'active')]")
        self.assert_not_exists("//button[@id='clue-btn-1'][contains(@class,'active')]")

    def test_Draft_puzzle_editor_can_preview_answer_and_parsing_for_each_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4], has_parsing=True)
        clues = puzzle.get_clues()
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Publish")
        self.do_click("//button[@id='clue-btn-3']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n',"")
        self.assertEqual(answer, clues[2].answer)
        self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clues[2].parsing)
        self.do_click("//div/button[@id='id-right-caret']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n',"")
        self.assertEqual(answer, clues[3].answer)
        self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clues[3].parsing)
        self.assert_not_exists("//div[@id='id-answer-icons']")
        self.assert_not_exists("//div[@id='id-answer-btns']")

    def test_Draft_puzzle_preview_shows_error_for_non_editor(self):
        puzzle = create_draft_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')   # Current user is NOT editor
        self.assert_text_equals("//div[@id='errMsg']", "This operation is not permitted since you are not the editor.")

    def test_Published_puzzle_editor_preview_shows_posted_by(self):
        puzzle = create_published_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Unpublish")
        self.assert_text_equals("//h4", str(puzzle))
        posted_by_str = 'Posted by: ' + str(self.user) + ' on ' + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_text_equals("//h6[@id='id-posted-by']", posted_by_str)
        self.assert_not_exists("//a[text()='PUBLISH']")

    def test_Published_puzzle_editor_can_unpublish_puzzle(self):
        puzzle = create_published_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_contains("//div[contains(@class,'notetext')][2]", "NOTE: Unpublish your puzzle")
        self.do_click("//a[text()='UNPUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertIsNone(updated_puzzle.shared_at)
        self.assert_current_url('/')

    def test_Published_puzzle_can_be_viewed_by_non_editor(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Description", clues_pts=[2, 2, 3], has_parsing=True)
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Solve")
        self.assert_text_equals("//h4", str(puzzle))
        posted_by_str = 'Posted by: ' + str(self.other_user) + ' on ' + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_text_equals("//h6[@id='id-posted-by']", posted_by_str)
        self.assert_not_exists("//a[text()='PUBLISH']")                 # No Publish button
        self.assert_not_exists("//a[text()='UNPUBLISH']")               # No Unpublish button
        self.assert_exists("//a[text()='SOLVE NOW']")                   # Solve button
        self.assert_not_exists("//div[@id='id-answer-icons']")
        self.assert_not_exists("//div[@id='id-answer-btns']")

    def test_Published_puzzle_preview_by_non_editor_hides_answers(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[2, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Solve")
        self.assert_is_not_displayed("//div[@id='id-answer']")
        self.assert_is_not_displayed("//div[@id='id-parsing']")

    def test_Solve_button_starts_solve_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//a[text()='SOLVE NOW']")
        self.assert_text_equals("//h2", "Solve Puzzle")
        self.assert_not_exists("//a[text()='PUBLISH']")                 # No PUBLISH button
        self.assert_not_exists("//a[text()='UNPUBLISH']")               # No UNPUBLISH button
        self.assert_not_exists("//a[text()='SOLVE NOW']")               # NO SOLVE NOW button
        self.assert_not_exists("//a[text()='DONE']")                    # No DONE button
        self.assert_exists("//a[text()='FINISH LATER']")                # Only FINISH LATER button