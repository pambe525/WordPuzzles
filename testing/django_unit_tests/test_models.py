from django.db.utils import IntegrityError

from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from datetime import datetime
from puzzles.models import Puzzle, WordPuzzle, Clue, Session
from testing.django_unit_tests.unit_test_helpers import create_published_puzzle

class UserNameTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joesmith')

    def test_name_without_first_or_last_name(self):
        self.assertEqual(str(self.user), "joesmith")

    def test_name_with_last_name_only(self):
        self.user.last_name = "Smith"
        self.assertEqual(str(self.user), "joesmith")

    def test_name_with_first_name_only(self):
        self.user.first_name = "Joe"
        self.assertEqual(str(self.user), "Joe")

    def test_name_with_first_and_last_name(self):
        self.user.first_name = "Joe"
        self.user.last_name = "Smith"
        self.assertEqual(str(self.user), "Joe Smith")


class PuzzleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_editor_field(self):
        puzzle = Puzzle.objects.create(editor=self.user)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual("testuser", puzzle.editor.username)

    def test_shared_at_field(self):
        current_time_stamp = datetime.now(tz=timezone.utc).isoformat()  # timestamp as ISO string (UTC)
        puzzle = Puzzle.objects.create(shared_at=current_time_stamp)
        puzzle = Puzzle.objects.get(id=puzzle.id)
        self.assertEqual(current_time_stamp, puzzle.shared_at.isoformat())  # Convert date object to string

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
        self.assertEqual("Puzzle #1: 10 Non-cryptic Clues [0 pts]", str(puzzle))
        puzzle = WordPuzzle.objects.create(size=20, type=1, editor=self.user)
        self.assertEqual("Puzzle #2: 20 Cryptic Clues [0 pts]", str(puzzle))

    def test_add_clue_creates_new_clue_and_updates_counts(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        cleaned_data = {'answer': 'MY-WORD TWO', 'clue_text': 'some clue text',
                        'parsing': 'def', 'points': 3}
        self.assertEqual(puzzle.size, 0)
        self.assertEqual(puzzle.total_points, 0)
        puzzle.add_clue(cleaned_data)
        self.assertEqual(puzzle.size, 1)
        self.assertEqual(puzzle.total_points, 3)
        new_clue = Clue.objects.all()[0]
        self.assertEqual(new_clue.puzzle, puzzle)
        self.assertEqual(new_clue.clue_num, 1)
        self.assertEqual(new_clue.answer, 'MY-WORD TWO')  # NOTE: capitalized answer
        self.assertEqual(new_clue.clue_text, 'some clue text')
        self.assertEqual(new_clue.parsing, 'def')
        self.assertEqual(new_clue.points, 3)
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.total_points, 3)
        self.assertEqual(puzzle.size, 1)

    def test_get_clues_returns_all_clues_as_a_list(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        clue1_data = {'answer': "FIRST", 'clue_text': 'Clue for first', 'parsing': 'DEF1', 'points': 1}
        clue2_data = {'answer': "SECOND", 'clue_text': 'Clue for 2nd', 'parsing': 'DEF2', 'points': 2}
        puzzle.add_clue(clue1_data)
        puzzle.add_clue(clue2_data)
        clues_list = puzzle.get_clues()
        self.assertEqual(len(clues_list), 2)


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

    def test_get_decorated_clue(self):
        clue = Clue.objects.create(puzzle=self.puzzle, clue_num=1, clue_text='This is a clue')
        clue.answer = "ONEWORD"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (7)')
        clue.answer = "TWO WORDS"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (3,5)')
        clue.answer = "MULTIPLE  SINGLE   WORDS IN A SENTENCE"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (8,6,5,2,1,8)')
        clue.answer = "HYPHENATED-WORD"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (10-4)')
        clue.answer = "THE EDITOR-IN-CHIEF FOR ALL-IN"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (3,6-2-5,3,3-2)')

class SessionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.puzzle = create_published_puzzle(user=self.user, clues_pts=[4,2,1,2,1])

    def test_puzzle_is_required_field(self):
        self.assertRaises(IntegrityError, Session.objects.create, solver=self.user)

    def test_solver_is_required_field(self):
        self.assertRaises(IntegrityError, Session.objects.create, puzzle=self.puzzle)