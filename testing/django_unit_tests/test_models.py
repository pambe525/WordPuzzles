from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from datetime import datetime
from puzzles.models import Puzzle

class PuzzleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_editor_field(self):
        puzzle = Puzzle.objects.create(editor=self.user)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual("testuser", puzzle.editor.username)

    def test_shared_at_field(self):
        currentTimeStamp = datetime.now(tz=timezone.utc).isoformat() # timestamp as ISO string (UTC)
        puzzle = Puzzle.objects.create(shared_at=currentTimeStamp)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual(currentTimeStamp, puzzle.shared_at.isoformat()) # Convert date object to string

    def test_field_defaults(self):
        puzzle = Puzzle.objects.create()
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertTrue(puzzle.is_xword)
        self.assertIsNone(puzzle.editor)
        self.assertEqual(0, puzzle.size)
        self.assertEqual("", puzzle.desc)
        self.assertEqual("", puzzle.data)
        self.assertIsNone(puzzle.shared_at)

    def test_string_representation(self):
        puzzle = Puzzle.objects.create(size=10)
        self.assertEqual("Puzzle #1: Crossword Puzzle (10x10)", str(puzzle))
        puzzle = Puzzle.objects.create(size=20, is_xword=False)
        self.assertEqual("Puzzle #2: Word Puzzle (20 clues)", str(puzzle))

