from django.contrib.auth.models import User
from django.utils.timezone import now

from puzzles.models import WordPuzzle
from testing.selenium_tests.selenium_helper_mixin import SeleniumTestCase


class AllPuzzlesTests(SeleniumTestCase):
    password = 'secretkey'

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password=self.password)
        self.login_user(username=self.user.username, password=self.password)

    def test_Page_title_and_sort_form(self):
        self.get('/all_puzzles')
        self.assert_xpath_text("//div/h2", 'All Published Puzzles')
        self.assert_xpath_exists("//select[1]")
        self.assert_xpath_value("//select[1]", "shared_at")
        self.assert_xpath_exists("//select[2]")
        self.assert_xpath_value("//select[2]", '-')

    def test_Each_published_puzzle_detail_is_listed(self):
        other_user = User.objects.create_user(username='testuser2')
        published_puzzle = WordPuzzle.objects.create(editor=other_user, type=1, desc="puzzle desc")
        published_puzzle.add_clue({'answer': "A WORD", 'clue_text': 'clue text for answer', 'points':3})
        published_puzzle.shared_at = now()
        published_puzzle.save()
        WordPuzzle.objects.create(editor=self.user, type=0)  # UNPUBLISHED PUZZLE
        self.get('/all_puzzles')
        self.assert_xpath_items("//table/tbody/tr", 1)
        self.assert_xpath_contains("//table/tbody/tr[1]/td[1]", str(published_puzzle))
        post_on = "Posted by: " + str(other_user) + " on " + published_puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_xpath_contains("//table/tbody/tr[1]/td[1]", post_on)
        self.assert_xpath_exists("//table/tbody/tr[1]/td[1]//a[@title='" + published_puzzle.desc + "']")

    def test_shows_ME_for_posted_by_if_editor_is_current_user(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0, desc="Puzzle description")
        puzzle.add_clue({'answer': "WORDS", 'clue_text': "Clue for word", 'points': 2})
        puzzle.shared_at = now()
        puzzle.save()
        self.get('/all_puzzles')
        post_on = "Posted by: ME on " + puzzle.shared_at.strftime('%b %d, %Y') + ' (GMT)'
        self.assert_xpath_contains("//table/tbody/tr[1]/td[1]", post_on)

    def test_Puzzle_title_links_to_preview_page_if_editor_is_current_user(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, type=0)
        puzzle.add_clue({'answer': "WORD", 'clue_text': "Clue for word", 'points': 2})
        puzzle.shared_at = now()
        puzzle.save()
        self.get('/all_puzzles')
        self.click_xpath("//table/tbody/tr[1]/td[1]/a")
        self.assert_current_url("/preview_puzzle/" + str(puzzle.id) + "/")

    def test_Sort_form_reflects_get_parameters_in_url(self):
        self.get('/all_puzzles?sort_by=total_points&order=')
        self.assert_xpath_text("//div/h2", 'All Published Puzzles')
        self.assert_xpath_value("//select[1]", "total_points")
        self.assert_xpath_value("//select[2]", '')

    def test_Selecting_sort_by_description_submits_form_with_correct_url(self):
        self.get('/all_puzzles')
        self.select_xpath_by_text("//select[1]", "Description")
        self.assert_current_url("/all_puzzles?sort_by=desc&order=-")
        self.assert_xpath_text("//div/h2", 'All Published Puzzles')
        self.assert_xpath_value("//select[1]", "desc")
        self.assert_xpath_value("//select[2]", '-')

    def test_Selecting_sort_by_editor_submits_form_with_correct_url(self):
        self.get('/all_puzzles')
        self.select_xpath_by_text("//select[1]", "Editor")
        self.select_xpath_by_text("//select[2]", "Ascending")
        self.assert_current_url("/all_puzzles?sort_by=editor__username&order=")
        self.assert_xpath_text("//div/h2", 'All Published Puzzles')
        self.assert_xpath_value("//select[1]", "editor__username")
        self.assert_xpath_value("//select[2]", '')

    def test_Selecting_sort_by_size_submits_form_with_correct_url(self):
        self.get('/all_puzzles')
        self.select_xpath_by_text("//select[1]", "No. of Clues")
        self.assert_current_url("/all_puzzles?sort_by=size&order=-")
        self.assert_xpath_value("//select[1]", "size")
        self.assert_xpath_value("//select[2]", '-')

    def test_Selecting_sort_by_id_submits_form_with_correct_url(self):
        self.get('/all_puzzles')
        self.select_xpath_by_text("//select[1]", "Puzzle #")
        self.assert_current_url("/all_puzzles?sort_by=id&order=-")
        self.assert_xpath_value("//select[1]", "id")
        self.assert_xpath_value("//select[2]", '-')

    def test_Selecting_sort_by_type_submits_form_with_correct_url(self):
        self.get('/all_puzzles')
        self.select_xpath_by_text("//select[1]", "Puzzle Type")
        self.assert_current_url("/all_puzzles?sort_by=type&order=-")
        self.assert_xpath_value("//select[1]", "type")
        self.assert_xpath_value("//select[2]", '-')

    def test_Selecting_sort_by_total_points_submits_form_with_correct_url(self):
        self.get('/all_puzzles')
        self.select_xpath_by_text("//select[1]", "Total Points")
        self.assert_current_url("/all_puzzles?sort_by=total_points&order=-")
        self.assert_xpath_value("//select[1]", "total_points")
        self.assert_xpath_value("//select[2]", '-')