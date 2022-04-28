from puzzles.models import WordPuzzle
from testing.data_setup_utils import create_draft_puzzle, get_full_clue_desc, create_published_puzzle, create_user
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class PreviewPuzzleTests(SeleniumTestCase):

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
        self.assert_text_contains("//div[contains(@class,'notetext')][2]", "NOTE: Publish your puzzle only")
        self.do_click("//a[text()='PUBLISH']")
        updated_puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertTrue(updated_puzzle.is_published())
        self.assert_current_url('/')

    def test_shows_clue_button_for_each_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[2, 1, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//div/div/div//h5", "Clues")
        self.assert_item_count("//div//button[contains(@id,'clue-btn-')]", 4)

    def test_clue_button_details(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[2, 1, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        for index, clue in enumerate(puzzle.get_clues()):
            clue_btn = self.get_element("//div/button[@id='clue-btn-" + str(index + 1) + "']")
            self.assertEqual(clue_btn.text, str(clue.clue_num))
            tooltip = clue.get_decorated_clue_text() + " [" + str(clue.points) + " pts]"
            self.assertEqual(clue_btn.get_attribute('title'), tooltip)

    def test_first_clue_is_shown_in_clue_box_and_first_clue_btn_is_activated(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[3, 1, 2, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        first_clue = puzzle.get_clues()[0]
        self.verify_clue_is_active(first_clue)

    def test_clicking_on_a_clue_button_activates_it_and_shows_clue_text_in_clue_box(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4, 5])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//div/button[@id='clue-btn-4']")
        fourth_clue = puzzle.get_clues()[3]
        self.verify_clue_is_active(fourth_clue)

    def test_clicking_on_right_caret_advances_to_next_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4, 5])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//div/button[@id='id-right-caret']")
        next_clue = puzzle.get_clues()[1]
        self.verify_clue_is_active(next_clue)

    def test_clicking_on_right_caret_on_last_clue_advances_to_first_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//button[@id='clue-btn-4']")
        self.do_click("//div/button[@id='id-right-caret']")
        next_clue = puzzle.get_clues()[0]
        self.verify_clue_is_active(next_clue)

    def test_clicking_on_left_caret_advances_to_previous_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[2, 1, 3, 4, 5])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//button[@id='clue-btn-4']")  # Click on 4th clue btn
        self.do_click("//div/button[@id='id-left-caret']")
        prev_clue = puzzle.get_clues()[2]  # 3rd clue
        self.verify_clue_is_active(prev_clue)

    def test_clicking_on_left_caret_on_first_clue_advances_to_last_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, desc="Puzzle description", clues_pts=[1, 2, 3, 4])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//div/button[@id='id-left-caret']")
        next_clue = puzzle.get_clues()[3]
        self.verify_clue_is_active(next_clue)

    def test_draft_puzzle_editor_can_preview_answer_and_parsing_for_each_clue(self):
        puzzle = create_draft_puzzle(editor=self.user, clues_pts=[1, 2, 3, 4], has_parsing=True)
        clues = puzzle.get_clues()
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Publish")
        self.do_click("//button[@id='clue-btn-3']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n', "")
        self.assertEqual(answer, clues[2].answer)
        self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clues[2].parsing)
        self.do_click("//div/button[@id='id-right-caret']")
        answer = self.get_element("//div[@id='id-answer']").text.replace('\n', "")
        self.assertEqual(answer, clues[3].answer)
        self.assert_text_equals("//div[@id='id-parsing']", "Parsing: " + clues[3].parsing)
        self.assert_not_exists("//div[@id='id-answer-icons']")
        self.assert_not_exists("//div[@id='id-answer-btns']")

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
        self.assert_text_contains("//div[contains(@class,'notetext')][2]", "NOTE: Unpublish your puzzle")
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
        self.assert_not_exists("//div[@id='id-answer-icons']")
        self.assert_not_exists("//div[@id='id-answer-btns']")

    def test_published_puzzle_preview_by_non_editor_hides_answers(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[2, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.assert_text_equals("//h2", "Preview Puzzle & Solve")
        self.assert_is_not_displayed("//div[@id='id-answer']")
        self.assert_is_not_displayed("//div[@id='id-parsing']")

    def test_solve_button_starts_solve_session(self):
        puzzle = create_published_puzzle(editor=self.other_user, desc="Puzzle description", clues_pts=[1, 2, 3])
        self.get('/preview_puzzle/' + str(puzzle.id) + '/')
        self.do_click("//a[text()='SOLVE NOW']")
        self.assert_text_equals("//h2", "Solve Puzzle")
        self.verify_button_states_for_solve_mode()

    #==================================================================================================================
    # HELPER METHODS
    def verify_clue_is_active(self, clue):
        btn_id = 'clue-btn-' + str(clue.clue_num)
        self.assert_text_equals("//div[@id='id-clue']", get_full_clue_desc(clue))
        self.assert_exists("//button[@id='"+btn_id+"'][contains(@class,'active')]")
        btns = self.selenium.find_elements_by_xpath("//button[starts-with(@id,'clue-btn-')][contains(@class,'active')]")
        self.assertEqual(len(btns), 1)  # Only 1 clue btn is active

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