from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from datetime import datetime
from puzzles.models import Puzzle, WordPuzzle, Clue

class PuzzleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_editor_field(self):
        puzzle = Puzzle.objects.create(editor=self.user)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual("testuser", puzzle.editor.username)

    def test_shared_at_field(self):
        current_time_stamp = datetime.now(tz=timezone.utc).isoformat() # timestamp as ISO string (UTC)
        puzzle = Puzzle.objects.create(shared_at=current_time_stamp)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual(current_time_stamp, puzzle.shared_at.isoformat()) # Convert date object to string

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

class WordPuzzleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')

    def test_default_instance_with_editor_field(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.assertEqual("testuser", puzzle.editor.username)
        self.assertEqual(puzzle.type, 1)
        self.assertEqual(puzzle.size, 0)
        self.assertIsNone(puzzle.desc)
        self.assertIsNone(puzzle.shared_at)
        # current_time_stamp = datetime.now(tz=timezone.utc).isoformat() # timestamp as ISO string (UTC)
        # self.assertEqual(current_time_stamp, puzzle.created_at.isoformat())

    def test_string_representation(self):
        puzzle = WordPuzzle.objects.create(size=10, type=0, editor=self.user)
        self.assertEqual("Puzzle #1: Non-cryptic Clues (10)", str(puzzle))
        puzzle = WordPuzzle.objects.create(size=20, type=1, editor=self.user)
        self.assertEqual("Puzzle #2: Cryptic Clues (20)", str(puzzle))

class ClueModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')
        self.puzzle = WordPuzzle.objects.create(editor=self.user)

    def test_default_instance(self):
        clue = Clue.objects.create(puzzle=self.puzzle)
        self.assertIsNone(clue.clue_num)
        self.assertIsNone(clue.clue_text)
        self.assertIsNone(clue.answer)
        self.assertIsNone(clue.parsing)
        self.assertEqual(str(clue), "<#>. <clue> [<answer>]")

    def test_string_representation(self):
        clue = Clue.objects.create(puzzle=self.puzzle, clue_num=1, answer="SOME WORD", clue_text="Cryptic clue (4,4)")
        self.assertEqual(str(clue), "1. Cryptic clue (4,4) [SOME WORD]")

    def test_clues_are_deleted_if_related_puzzle_is_deleted(self):
        clue1 = Clue.objects.create(puzzle=self.puzzle, clue_num=1)
        clue2 = Clue.objects.create(puzzle=self.puzzle, clue_num=2)
        clue3 = Clue.objects.create(puzzle=self.puzzle, clue_num=3)
        self.assertEqual(Clue.objects.all().count(), 3)
        self.puzzle.delete()
        self.assertEqual(Clue.objects.all().count(), 0)
