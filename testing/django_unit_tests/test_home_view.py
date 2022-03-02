from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from puzzles.models import WordPuzzle


class HomeViewTests(TestCase):

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey")
        self.client.force_login(self.user)

    def test_Renders_home_page_if_user_is_authenticated(self):
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
        self.assertContains(response, "Puzzle #1: 0 Cryptic Clues [0 pts]")
        self.assertContains(response, "Puzzle #2: 0 Cryptic Clues [0 pts]")

    def test_Draft_puzzles_filtered_for_current_user(self):
        user2 = User.objects.create_user("testuser2")
        puzzle1 = WordPuzzle.objects.create(editor=self.user)
        puzzle2 = WordPuzzle.objects.create(editor=user2)
        puzzle3 = WordPuzzle.objects.create(editor=self.user)
        response = self.client.get(reverse("home"))
        self.assertEqual(len(response.context['draft_puzzles']), 2)

    def test_Draft_puzzle_details_in_response_context(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Daily puzzle")
        response = self.client.get(reverse("home"))
        puzzle_details = response.context['draft_puzzles'][0]
        self.assertEqual(puzzle_details['id'], 1)
        self.assertEqual(puzzle_details['desc'], 'Daily puzzle')
        self.assertEqual(puzzle_details['name'], "Puzzle #1: 0 Cryptic Clues [0 pts]")
        self.assertEqual(puzzle_details['size'], 0)
        self.assertIsNotNone(puzzle_details['modified_at'])




