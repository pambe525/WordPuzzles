from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from puzzles.models import WordPuzzle
from django.utils.timezone import now
from datetime import timedelta

class DashboardViewTests(TestCase):

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey")
        self.client.force_login(self.user)

    def test_Renders_dashboard_page_if_user_is_authenticated(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "home.html")
        self.assertContains(response, "Dashboard")

    def test_Redirects_to_login_page_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/")

    def test_Rendered_template_with_no_draft_puzzles(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context['draft_puzzles']), 0)
        self.assertContains(response, "no draft puzzles")

    def test_Rendered_template_with_draft_puzzles(self):
        puzzle1 = WordPuzzle.objects.create(editor=self.user)
        puzzle2 = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed("home.html")

    def test_Draft_puzzles_filtered_for_current_user(self):
        user2 = User.objects.create_user("testuser2")
        WordPuzzle.objects.create(editor=self.user)
        WordPuzzle.objects.create(editor=user2)
        WordPuzzle.objects.create(editor=self.user)
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context['draft_puzzles']), 2)

    def test_Draft_puzzle_details_in_response_context(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Daily puzzle")
        response = self.client.get(reverse("home"))
        puzzle_details = response.context['draft_puzzles'][0]
        self.assertEqual(puzzle_details.id, puzzle.id)
        self.assertEqual(puzzle_details.desc, puzzle.desc)
        self.assertEqual(str(puzzle_details), str(puzzle))
        self.assertEqual(puzzle_details.size, puzzle.size)
        self.assertIsNotNone(puzzle_details.modified_at)
        self.assertIsNone(puzzle_details.shared_at)

    def test_Draft_puzzles_do_not_include_published_puzzles_and_sorted_last_modified_first(self):
        puzzle1 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
        puzzle2 = WordPuzzle.objects.create(editor=self.user)
        puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
        puzzle2.shared_at = now()   # PUBLISHED
        puzzle2.save()
        response = self.client.get('/')
        self.assertEqual(len(response.context['draft_puzzles']), 2)
        self.assertEqual(response.context['draft_puzzles'][0].desc, puzzle3.desc)
        self.assertEqual(response.context['draft_puzzles'][1].desc, puzzle1.desc)

    def test_Recently_posted_puzzles_include_only_published_puzzles_and_sorted_by_recent_first(self):
        WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
        puzzle2 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 2")
        puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
        puzzle2.shared_at = now()-timedelta(days=3)    # shared 3 days ago
        puzzle2.save()
        puzzle3.shared_at = now()-timedelta(days=2)    # shared 2 days ago
        puzzle3.save()
        response = self.client.get('/')
        self.assertEqual(len(response.context['recent_puzzles']), 2)
        self.assertEqual(response.context['recent_puzzles'][0].desc, puzzle3.desc)
        self.assertEqual(response.context['recent_puzzles'][1].desc, puzzle2.desc)

    def test_Recently_posted_puzzles_only_include_published_puzzles_within_last_7_days(self):
        puzzle1 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 1")
        puzzle2 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 2")
        puzzle3 = WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 3")
        WordPuzzle.objects.create(editor=self.user, desc="Daily Puzzle 4")
        puzzle2.shared_at = now()-timedelta(days=8)    # shared 8 days ago
        puzzle2.save()
        puzzle1.shared_at = now()-timedelta(days=6)    # shared 6 days ago
        puzzle3.shared_at = now()-timedelta(days=2)    # shared 2 days ago
        puzzle1.save()
        puzzle3.save()
        response = self.client.get('/')
        self.assertEqual(len(response.context['recent_puzzles']), 2)
        self.assertEqual(response.context['recent_puzzles'][1].desc, puzzle1.desc)
        self.assertEqual(response.context['recent_puzzles'][0].desc, puzzle3.desc)

