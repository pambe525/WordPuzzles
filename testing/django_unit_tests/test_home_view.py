from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now

from puzzles.models import WordPuzzle
from testing.data_setup_utils import create_published_puzzle, create_session, create_draft_puzzle


class DashboardViewTests(TestCase):
    target_page = "/"

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey")
        self.client.force_login(self.user)

    def test_renders_dashboard_page_if_user_is_authenticated(self):
        response = self.client.get(self.target_page)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "home.html")
        self.assertContains(response, "Dashboard")

    def test_redirects_to_login_page_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(self.target_page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/")

    def test_GET_has_draft_puzzles_filtered_for_current_user(self):
        user2 = User.objects.create_user("testuser2")
        WordPuzzle.objects.create(editor=self.user)
        WordPuzzle.objects.create(editor=user2)
        WordPuzzle.objects.create(editor=self.user)
        response = self.client.get("/")
        self.assertEqual(len(response.context['draft_puzzles']), 2)

    def test_draft_puzzle_details_in_response_context(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Daily puzzle")
        response = self.client.get(self.target_page)
        draft_puzzle = response.context['draft_puzzles'][0]
        self.assertEqual(draft_puzzle['id'], puzzle.id)
        self.assertEqual(draft_puzzle['title'], str(puzzle))
        self.assertEqual(draft_puzzle['type'], puzzle.type)
        self.assertEqual(draft_puzzle['desc'], puzzle.desc)
        self.assertEqual(draft_puzzle['type_text'], "Cryptic Clues")  # Default
        self.assertEqual(draft_puzzle['utc_modified_at'], str(puzzle.modified_at.strftime("%Y-%m-%d %H:%M:%SZ")))

    def test_draft_puzzles_exclude_published_puzzles_and_are_sorted_last_modified_first(self):
        puzzle1 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
        puzzle2 = WordPuzzle.objects.create(editor=self.user)
        puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
        puzzle1.type = 0
        puzzle1.save()  # Change Puzzle 1 so it becomes last modified
        puzzle2.shared_at = now()  # PUBLISHED
        puzzle2.save()
        response = self.client.get(self.target_page)
        self.assertEqual(len(response.context['draft_puzzles']), 2)
        self.assertEqual(response.context['draft_puzzles'][0]['title'], str(puzzle1))
        self.assertEqual(response.context['draft_puzzles'][1]['title'], str(puzzle3))

    def test_response_has_new_puzzle_form(self):
        response = self.client.get(self.target_page)
        self.assertEqual(2, len(response.context['form'].fields))
        self.assertEqual(1, response.context['form']['type'].value())
        self.assertIsNone(response.context['form']['desc'].value())

    def test_notices_section_has_at_least_three_items_by_default(self):
        response = self.client.get(self.target_page)
        notifications = response.context['notifications']
        self.assertEqual(3, len(notifications))
        self.assertIn("See <b>What's New</b> in the", notifications[0])
        self.assertIn("Create a New Puzzle", notifications[1])
        self.assertIn("Set your first & last name in", notifications[2])

    def test_has_notice_on_puzzles_list_if_unattempted_published_puzzles_exist(self):
        user2 = User.objects.create(username="user2", email="abc@cde.com")
        user3 = User.objects.create(username="user3", email="cde@abc.com")
        puzzle = create_published_puzzle(editor=user2, clues_pts=[1, 1, 1, 1, 1])
        create_session(puzzle, user3, 3, 1, 5)    # other user's session
        response = self.client.get(self.target_page)
        notifications = response.context['notifications']
        self.assertEqual(4, len(notifications))
        self.assertIn("Pick a puzzle to solve in", notifications[3])

    def test_no_notice_on_puzzles_list_if_no_unattempted_published_puzzles_exist(self):
        user2 = User.objects.create(username="user2", email="abc@cde.com")
        user3 = User.objects.create(username="user3", email="cde@abc.com")
        puzzle1 = create_draft_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        puzzle2 = create_published_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        puzzle3 = create_published_puzzle(editor=user2, clues_pts=[1, 1, 1, 1, 1])
        create_session(puzzle2, user2, 3, 1, 5)      # puzzle2 created by user - exclude
        create_session(puzzle3, self.user, 3, 2, 15)  # puzzle3 has user session - exclude
        # No unattempted other's published puzzles by current user
        response = self.client.get(self.target_page)
        notifications = response.context['notifications']
        self.assertEqual(3, len(notifications))
        # Create another puzzle by other user with a session by another user => 1 unattempted puzzle
        puzzle4 = create_published_puzzle(editor=user3, clues_pts=[1, 1, 1, 1, 1])
        create_session(puzzle4, user2, 2, 0, 7)      # puzzle4 has no user session - include
        response = self.client.get(self.target_page)
        notifications = response.context['notifications']
        self.assertEqual(4, len(notifications))
        self.assertIn("Pick a puzzle to solve in", notifications[3])

    def test_has_no_set_name_notice_if_name_is_already_set(self):
        self.user.first_name = "Joe"
        self.user.last_name = "Smith"
        self.user.save()
        response = self.client.get(self.target_page)
        notifications = response.context['notifications']
        self.assertEqual(2, len(notifications))

    def test_has_notice_if_user_has_in_progress_published_puzzles(self):
        user2 = User.objects.create(username="user2", email="abc@cde.com")
        user3 = User.objects.create(username="user3", email="cde@abc.com")
        puzzle1 = create_draft_puzzle(editor=self.user, clues_pts=[1, 1, 1, 1, 1])
        puzzle2 = create_published_puzzle(editor=self.user, clues_pts=[1, 2, 1, 1, 1])
        puzzle3 = create_published_puzzle(editor=user2, clues_pts=[1, 3, 1, 1, 1])
        puzzle4 = create_published_puzzle(editor=user3, clues_pts=[1, 1, 1, 1, 1])
        create_session(puzzle2, user2, 2, 1, 5)      # puzzle2 created by user - exclude
        create_session(puzzle3, self.user, 3, 1, 5)  # puzzle3 has user session - include
        create_session(puzzle4, self.user, 2, 3, 10) # puzzle4 is finished - exclude
        response = self.client.get(self.target_page)
        notifications = response.context['notifications']
        self.assertEqual(4, len(notifications))
        self.assertIn("You have 1", notifications[3])
