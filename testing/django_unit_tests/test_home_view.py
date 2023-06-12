from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils.timezone import now

from puzzles.models import WordPuzzle
from testing.data_setup_utils import create_user


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

    def test_empty_notifications_section(self):
        response = self.client.get(self.target_page)
        self.assertTemplateUsed(response, "home.html")
        self.assertEqual(response.context['drafts_count'], 0)
        self.assertContains(response, "Notifications")
        self.assertContains(response, "No notifications to report")

    def test_notifications_with_draft_puzzle(self):
        user2 = create_user(username="user2")
        WordPuzzle.objects.create(editor=self.user, type=0)  # Draft 1
        WordPuzzle.objects.create(editor=self.user, type=1)  # Draft 2
        WordPuzzle.objects.create(editor=user2)  # Other user draft - not counted
        WordPuzzle.objects.create(editor=self.user, shared_at=now())  # Published - not counted
        response = self.client.get(self.target_page)
        self.assertEqual(response.context['drafts_count'], 2)
        self.assertNotContains(response, "No notifications to report")
        self.assertContains(response, "2 draft puzzle(s)")

    # def test_draft_puzzles_filtered_for_current_user(self):
    #     user2 = User.objects.create_user("testuser2")
    #     WordPuzzle.objects.create(editor=self.user)
    #     WordPuzzle.objects.create(editor=user2)
    #     WordPuzzle.objects.create(editor=self.user)
    #     response = self.client.get(reverse("home"))
    #     self.assertEqual(len(response.context['draft_puzzles']), 2)
    #
    # def test_draft_puzzle_details_in_response_context(self):
    #     puzzle = WordPuzzle.objects.create(editor=self.user, desc="Daily puzzle")
    #     response = self.client.get(reverse("home"))
    #     puzzle_details = response.context['draft_puzzles'][0]
    #     self.assertEqual(puzzle_details.id, puzzle.id)
    #     self.assertEqual(puzzle_details.desc, puzzle.desc)
    #     self.assertEqual(str(puzzle_details), str(puzzle))
    #     self.assertEqual(puzzle_details.size, puzzle.size)
    #     self.assertIsNotNone(puzzle_details.modified_at)
    #     self.assertIsNone(puzzle_details.shared_at)
    #
    # def test_draft_puzzles_do_not_include_published_puzzles_and_sorted_last_modified_first(self):
    #     puzzle1 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
    #     puzzle2 = WordPuzzle.objects.create(editor=self.user)
    #     puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
    #     puzzle1.type=0
    #     puzzle1.save()    # Change Puzzle 1 so it becomes last modified
    #     puzzle2.shared_at = now()   # PUBLISHED
    #     puzzle2.save()
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['draft_puzzles']), 2)
    #     self.assertEqual(response.context['draft_puzzles'][0].desc, puzzle1.desc)
    #     self.assertEqual(response.context['draft_puzzles'][1].desc, puzzle3.desc)
    #
    # def test_recently_posted_puzzles_include_only_published_puzzles_and_sorted_by_recent_first(self):
    #     WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
    #     puzzle2 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 2")
    #     puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
    #     puzzle2.shared_at = now()-timedelta(days=3)    # shared 3 days ago
    #     puzzle2.save()
    #     puzzle3.shared_at = now()-timedelta(days=2)    # shared 2 days ago
    #     puzzle3.save()
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 2)
    #     self.assertEqual(response.context['recent_puzzles'][0].desc, puzzle3.desc)
    #     self.assertEqual(response.context['recent_puzzles'][1].desc, puzzle2.desc)
    #
    # def test_recently_posted_puzzles_only_include_published_puzzles_within_last_7_days(self):
    #     puzzle1 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
    #     puzzle2 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 2")
    #     puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
    #     WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 4")
    #     puzzle2.shared_at = now()-timedelta(days=8)    # shared 8 days ago
    #     puzzle2.save()
    #     puzzle1.shared_at = now()-timedelta(days=6)    # shared 6 days ago
    #     puzzle3.shared_at = now()-timedelta(days=2)    # shared 2 days ago
    #     puzzle1.save()
    #     puzzle3.save()
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 2)
    #     self.assertEqual(response.context['recent_puzzles'][1].desc, puzzle1.desc)
    #     self.assertEqual(response.context['recent_puzzles'][0].desc, puzzle3.desc)
    #
    # def test_recently_posted_puzzles_include_count_of_sessions_and_user_session(self):
    #     user2 = create_user(username="user2")
    #     user3 = create_user(username="user3")
    #     create_published_puzzle(editor=user2, desc="Daily Puzzle 1", clues_pts=[1,2,1])
    #     puzzle2 = create_published_puzzle(editor=user3, desc="Daily Puzzle 2", clues_pts=[1,1])
    #     session1 = create_session(solver=self.user, puzzle=puzzle2)
    #     create_session(solver=user2, puzzle=puzzle2)
    #     response = self.client.get('/')
    #     self.assertEqual(response.context['recent_puzzles'][0].session_count, 0)
    #     self.assertEqual(response.context['recent_puzzles'][1].session_count, 2)
    #     self.assertIsNone(response.context['recent_puzzles'][0].user_session)
    #     self.assertEqual(response.context['recent_puzzles'][1].user_session, session1)
    #
    # def test_recent_puzzles_includes_puzzles_related_to_recent_user_sessions(self):
    #     user2 = create_user(username="user2")
    #     # Puzzles
    #     old_puzzle1 = create_published_puzzle(editor=user2, posted_on=(now()-timedelta(days=8)))
    #     old_puzzle2 = create_published_puzzle(editor=user2, posted_on=(now() - timedelta(days=25)))
    #     new_puzzle1 = create_published_puzzle(editor=user2, posted_on=(now()-timedelta(days=5)))
    #     old_puzzle3 = create_published_puzzle(editor=self.user, posted_on=(now()-timedelta(days=9)))
    #     new_puzzle2 = create_published_puzzle(editor=self.user)
    #     # Sessions
    #     new_session1 = create_session(solver=self.user, puzzle=old_puzzle2)
    #     new_session2 = create_session(solver=self.user, puzzle=new_puzzle1)
    #     new_session3 = create_session(solver=user2, puzzle=old_puzzle3)
    #     new_session4 = create_session(solver=user2, puzzle=new_puzzle2)
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 3)
    #     self.assertEqual(response.context['recent_puzzles'][0], new_puzzle2)
    #     self.assertEqual(response.context['recent_puzzles'][1], new_puzzle1)
    #     self.assertEqual(response.context['recent_puzzles'][2], old_puzzle2)
    #
    # def test_recent_puzzles_does_not_include_same_puzzle_multiple_times(self):
    #     user2 = create_user(username="user2")
    #     user3 = create_user(username='user3')
    #     user4 = create_user(username='user4')
    #     # Single puzzle, multiple sessions
    #     puzzle = create_published_puzzle(editor=self.user, clues_pts=[1,2,1,2,1])
    #     new_session1 = create_session(solver=user2, puzzle=puzzle)
    #     new_session2 = create_session(solver=user3, puzzle=puzzle)
    #     new_session3 = create_session(solver=user4, puzzle=puzzle)
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 1)
    #
    #
    # def test_recently_posted_puzzles_include_only_published_puzzles_and_sorted_by_recent_first(self):
    #     WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
    #     puzzle2 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 2")
    #     puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
    #     puzzle2.shared_at = now()-timedelta(days=3)    # shared 3 days ago
    #     puzzle2.save()
    #     puzzle3.shared_at = now()-timedelta(days=2)    # shared 2 days ago
    #     puzzle3.save()
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 2)
    #     self.assertEqual(response.context['recent_puzzles'][0].desc, puzzle3.desc)
    #     self.assertEqual(response.context['recent_puzzles'][1].desc, puzzle2.desc)
    #
    # def test_recently_posted_puzzles_only_include_published_puzzles_within_last_7_days(self):
    #     puzzle1 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
    #     puzzle2 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 2")
    #     puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
    #     WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 4")
    #     puzzle2.shared_at = now()-timedelta(days=8)    # shared 8 days ago
    #     puzzle2.save()
    #     puzzle1.shared_at = now()-timedelta(days=6)    # shared 6 days ago
    #     puzzle3.shared_at = now()-timedelta(days=2)    # shared 2 days ago
    #     puzzle1.save()
    #     puzzle3.save()
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 2)
    #     self.assertEqual(response.context['recent_puzzles'][1].desc, puzzle1.desc)
    #     self.assertEqual(response.context['recent_puzzles'][0].desc, puzzle3.desc)
    #
    # def test_recently_posted_puzzles_include_count_of_sessions_and_user_session(self):
    #     user2 = create_user(username="user2")
    #     user3 = create_user(username="user3")
    #     create_published_puzzle(editor=user2, desc="Daily Puzzle 1", clues_pts=[1,2,1])
    #     puzzle2 = create_published_puzzle(editor=user3, desc="Daily Puzzle 2", clues_pts=[1,1])
    #     session1 = create_session(solver=self.user, puzzle=puzzle2)
    #     create_session(solver=user2, puzzle=puzzle2)
    #     response = self.client.get('/')
    #     self.assertEqual(response.context['recent_puzzles'][0].session_count, 0)
    #     self.assertEqual(response.context['recent_puzzles'][1].session_count, 2)
    #     self.assertIsNone(response.context['recent_puzzles'][0].user_session)
    #     self.assertEqual(response.context['recent_puzzles'][1].user_session, session1)
    #
    # def test_recent_puzzles_includes_puzzles_related_to_recent_user_sessions(self):
    #     user2 = create_user(username="user2")
    #     # Puzzles
    #     old_puzzle1 = create_published_puzzle(editor=user2, posted_on=(now()-timedelta(days=8)))
    #     old_puzzle2 = create_published_puzzle(editor=user2, posted_on=(now() - timedelta(days=25)))
    #     new_puzzle1 = create_published_puzzle(editor=user2, posted_on=(now()-timedelta(days=5)))
    #     old_puzzle3 = create_published_puzzle(editor=self.user, posted_on=(now()-timedelta(days=9)))
    #     new_puzzle2 = create_published_puzzle(editor=self.user)
    #     # Sessions
    #     new_session1 = create_session(solver=self.user, puzzle=old_puzzle2)
    #     new_session2 = create_session(solver=self.user, puzzle=new_puzzle1)
    #     new_session3 = create_session(solver=user2, puzzle=old_puzzle3)
    #     new_session4 = create_session(solver=user2, puzzle=new_puzzle2)
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 3)
    #     self.assertEqual(response.context['recent_puzzles'][0], new_puzzle2)
    #     self.assertEqual(response.context['recent_puzzles'][1], new_puzzle1)
    #     self.assertEqual(response.context['recent_puzzles'][2], old_puzzle2)
    #
    # def test_recent_puzzles_does_not_include_same_puzzle_multiple_times(self):
    #     user2 = create_user(username="user2")
    #     user3 = create_user(username='user3')
    #     user4 = create_user(username='user4')
    #     # Single puzzle, multiple sessions
    #     puzzle = create_published_puzzle(editor=self.user, clues_pts=[1,2,1,2,1])
    #     new_session1 = create_session(solver=user2, puzzle=puzzle)
    #     new_session2 = create_session(solver=user3, puzzle=puzzle)
    #     new_session3 = create_session(solver=user4, puzzle=puzzle)
    #     response = self.client.get('/')
    #     self.assertEqual(len(response.context['recent_puzzles']), 1)
