from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.test import TestCase, TransactionTestCase
from django.utils.timezone import now
from puzzles.models import WordPuzzle


class MyPuzzlesViewTests(TestCase):
    target_page = "/my_puzzles"

    def setUp(self):
        # Create a logged in user
        self.user = User.objects.create_user("testuser", "abc@email.com", "secretkey")
        self.client.force_login(self.user)

    def test_renders_page_if_user_is_authenticated(self):
        response = self.client.get(self.target_page)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, "my_puzzles.html")
        self.assertContains(response, "My Puzzles")

    def test_redirects_to_login_page_if_user_is_not_authenticated(self):
        logout(self.client)
        response = self.client.get(self.target_page)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/my_puzzles")

    def test_initializes_new_puzzle_modal_form(self):
        response = self.client.get(self.target_page)
        self.assertEqual(response.context['form']['type'].initial, 1)
        self.assertIsNone(response.context['form']['desc'].initial)

    def test_posting_new_puzzle_modal_form_creates_new_puzzle_and_redirects_to_edit_page(self):
        self.assertEqual(len(WordPuzzle.objects.all()), 0)
        response = self.client.post("/new_puzzle", {'type': 0, 'desc': "Some instructions"})
        self.assertEqual(len(WordPuzzle.objects.all()), 1)
        new_puzzle = WordPuzzle.objects.all()[0]
        self.assertEqual(new_puzzle.type, 0)
        self.assertEqual(new_puzzle.desc, "Some instructions")
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(response['location'], "/edit_puzzle/" + str(new_puzzle.id) + "/")

    def test_rendered_template_with_no_draft_puzzles(self):
        response = self.client.get(self.target_page)
        self.assertEqual(len(response.context['draft_puzzles']), 0)

    def test_rendered_template_with_draft_puzzles_for_current_user(self):
        user2 = User.objects.create_user("testuser2")
        WordPuzzle.objects.create(editor=self.user)
        WordPuzzle.objects.create(editor=self.user)
        WordPuzzle.objects.create(editor=user2)
        response = self.client.get(self.target_page)
        self.assertEqual(len(response.context['draft_puzzles']), 2)

    def test_draft_puzzle_details_in_response_context(self):
        puzzle = WordPuzzle.objects.create(editor=self.user, desc="Daily puzzle")
        response = self.client.get(self.target_page)
        draft_puzzle = response.context['draft_puzzles'][0]
        self.assertEqual(draft_puzzle['id'], puzzle.id)
        self.assertEqual(draft_puzzle['title'], str(puzzle))
        self.assertEqual(draft_puzzle['type'], puzzle.type)
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
