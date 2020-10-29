from django.contrib.auth.models import User
from django.test import TestCase
from datetime import datetime
from puzzles.models import Puzzle

class PuzzleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_editor_field(self):
        puzzle = Puzzle.objects.create(editor=self.user)
        self.assertEqual("testuser", puzzle.editor.username)

    def test_field_defaults(self):
        puzzle = Puzzle.objects.create()
        self.assertTrue(puzzle.is_xword)
        self.assertFalse(puzzle.is_ready)
        self.assertIsNone(puzzle.editor)
        self.assertEqual(0, puzzle.size)
        self.assertEqual("", puzzle.data)
        self.assertIsNone(puzzle.shared_at)
        self.assertEqual("", puzzle.data)

    def test_string_representation(self):
        puzzle = Puzzle.objects.create(size=10)
        self.assertEqual("#1 Crossword Puzzle (10x10)", str(puzzle))
        puzzle = Puzzle.objects.create(size=20, is_xword=False)
        self.assertEqual("#2 Word Puzzle (20 clues)", str(puzzle))

