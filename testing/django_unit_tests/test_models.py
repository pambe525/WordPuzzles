from datetime import datetime

from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.utils.timezone import now

from puzzles.models import Puzzle, WordPuzzle, Clue, SolverSession, GroupSession, SolvedClue
from testing.data_setup_utils import create_published_puzzle


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


class PuzzleModelTest(TransactionTestCase):
    reset_sequences = True

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


class WordPuzzleModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')

    def test_default_instance_with_editor_field(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        self.assertEqual("testuser", puzzle.editor.username)
        self.assertEqual(puzzle.type, 1)
        self.assertEqual(puzzle.size, 0)
        self.assertIsNone(puzzle.desc)
        self.assertIsNone(puzzle.shared_at)

    def test_string_representation(self):
        puzzle = WordPuzzle.objects.create(size=10, type=0, editor=self.user)
        self.assertEqual("Puzzle 1: 10 Non-cryptic Clues [0 pts]", str(puzzle))
        puzzle = WordPuzzle.objects.create(size=20, type=1, editor=self.user)
        self.assertEqual("Puzzle 2: 20 Cryptic Clues [0 pts]", str(puzzle))

    def test_add_clues_creates_new_clues_and_updates_counts(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        cleaned_input = [{'clue_num': 1, 'clue_text': 'some clue text (2-4)', 'answer': 'my-word'},
                         {'clue_num': 2, 'clue_text': 'another clue', 'answer': 'ANOTHER WORD'}]
        puzzle.add_clues(cleaned_input)
        created_clues = Clue.objects.all()
        self.assertEqual(2, len(created_clues))
        clue1 = created_clues[0]
        clue2 = created_clues[1]
        # first clue
        self.assertEqual(clue1.puzzle, puzzle)
        self.assertEqual(clue1.clue_num, 1)
        self.assertEqual(clue1.answer, 'my-word')  # NOT capitalized
        self.assertEqual(clue1.clue_text, 'some clue text (2-4)')
        self.assertIsNone(clue1.parsing)
        self.assertEqual(clue1.points, 1)
        # second clue
        self.assertEqual(clue2.puzzle, puzzle)
        self.assertEqual(clue2.clue_num, 2)
        self.assertEqual(clue2.answer, 'ANOTHER WORD')  # capitalization preserved
        self.assertEqual(clue2.clue_text, 'another clue')
        puzzle = WordPuzzle.objects.get(id=puzzle.id)
        self.assertEqual(puzzle.total_points, 2)
        self.assertEqual(puzzle.size, 2)

    def test_get_clues_returns_all_clues_as_a_list(self):
        puzzle = WordPuzzle.objects.create(editor=self.user)
        cleaned_input = [{'clue_num': 1, 'clue_text': 'some clue text (2-4)', 'answer': 'my-word'},
                         {'clue_num': 3, 'clue_text': 'another clue', 'answer': 'ANOTHER WORD'}]
        puzzle.add_clues(cleaned_input)
        clues_list = puzzle.get_clues()
        self.assertEqual(len(clues_list), 2)
        self.assertEqual(1, clues_list[0].clue_num)
        self.assertEqual(3, clues_list[1].clue_num)


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

    def test_get_decorated_clue_with_length_not_specified_in_clue(self):
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

    def test_get_decorated_clue_with_length_specified_in_clue(self):
        clue = Clue.objects.create(puzzle=self.puzzle, clue_num=1, clue_text='This is a clue (3,4)')
        clue.answer = "ONE WORD"
        self.assertEqual(clue.get_decorated_clue_text(), 'This is a clue (3,4)')


class GroupSessionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')
        self.puzzle = WordPuzzle.objects.create(editor=self.user)

    def test_puzzle_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, host=self.user)

    def test_host_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, puzzle=self.puzzle)

    def test_start_at_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, puzzle=self.puzzle, host=self.user)

    def test_default_instance(self):
        scheduled_date = now()
        session = GroupSession.objects.create(puzzle=self.puzzle, host=self.user, start_at=scheduled_date)
        self.assertEqual(session.puzzle, self.puzzle)
        self.assertEqual(session.host, self.user)
        self.assertEqual(session.start_at, scheduled_date)
        self.assertIsNone(session.finish_at)


class SolvedClueModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='secretkey')
        self.puzzle = WordPuzzle.objects.create(editor=self.user)
        self.clue = Clue.objects.create(puzzle=self.puzzle)
        self.session = SolverSession.objects.create(puzzle=self.puzzle, solver=self.user)

    def test_clue_is_required(self):
        self.assertRaises(Exception, SolvedClue.objects.create, solver=self.user)

    def test_solver_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, clue=self.clue)

    def test_session_is_required(self):
        self.assertRaises(Exception, GroupSession.objects.create, clue=self.clue, solver=self.user)

    def test_default_instance(self):
        solved_clue = SolvedClue.objects.create(clue=self.clue, solver=self.user, session=self.session)
        self.assertEqual(solved_clue.clue, self.clue)
        self.assertEqual(solved_clue.solver, self.user)
        self.assertEqual(solved_clue.session, self.session)
        self.assertFalse(solved_clue.revealed)

    def test_error_on_creating_duplicate_entry(self):
        SolvedClue.objects.create(clue=self.clue, solver=self.user, session=self.session)
        with self.assertRaises(IntegrityError):
            SolvedClue.objects.create(clue=self.clue, solver=self.user, session=self.session)


class SolveSessionModelTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345', email="abc@cde.com")
        self.puzzle1 = create_published_puzzle(editor=self.user1, clues_pts=[4, 2, 1, 2, 1, 3])
        self.puzzle2 = create_published_puzzle(editor=self.user2, clues_pts=[3, 5, 2])

    def test_puzzle_is_required_field(self):
        with self.assertRaises(Exception):
            SolverSession.objects.create(solver=self.user1)

    def test_solver_is_required_field(self):
        with self.assertRaises(IntegrityError):
            SolverSession.objects.create(puzzle=self.puzzle1)

    def test_new_creates_default_instance(self):
        session = SolverSession.new(self.puzzle1, self.user2)
        self.assertEqual(session.puzzle, self.puzzle1)
        self.assertEqual(session.solver, self.user2)
        self.assertIsNone(session.group_session)
        self.assertLessEqual(session.started_at, now())
        self.assertIsNone(session.finished_at)

    def test_puzzle_editor_cannot_be_solver(self):
        with self.assertRaises(IntegrityError):
            SolverSession.new(self.puzzle1, self.user1)

    def test_set_solved_clue_checks_if_clue_belongs_to_puzzle(self):
        session = SolverSession.new(self.puzzle1, self.user2)
        p2_clues = self.puzzle2.get_clues()
        with self.assertRaises(IntegrityError):
            session.set_solved_clue(clue=p2_clues[1])

    def test_set_solved_clue_creates_entry(self):
        session = SolverSession.new(self.puzzle1, self.user2)
        p1_clues = self.puzzle1.get_clues()
        session.set_solved_clue(clue=p1_clues[1])
        solved_clue = SolvedClue.objects.get(clue=p1_clues[1], solver=self.user2)
        self.assertEqual(solved_clue.clue, p1_clues[1])
        self.assertEqual(solved_clue.solver, self.user2)
        self.assertEqual(solved_clue.session, session)
        self.assertFalse(solved_clue.revealed)
        self.assertEqual(session.score, 2)

    def test_set_revealed_clue_checks_if_clue_belongs_to_puzzle(self):
        session = SolverSession.new(self.puzzle1, self.user2)
        p2_clues = self.puzzle2.get_clues()
        with self.assertRaises(IntegrityError):
            session.set_revealed_clue(clue=p2_clues[1])

    def test_set_revealed_clue_creates_entry(self):
        session = SolverSession.new(self.puzzle1, self.user2)
        p1_clues = self.puzzle1.get_clues()
        session.set_revealed_clue(clue=p1_clues[1])
        solved_clue = SolvedClue.objects.get(clue=p1_clues[1], solver=self.user2)
        self.assertEqual(solved_clue.clue, p1_clues[1])
        self.assertEqual(solved_clue.solver, self.user2)
        self.assertEqual(solved_clue.session, session)
        self.assertTrue(solved_clue.revealed)
        self.assertEqual(session.score, 0)

    def test_get_all_solved_clue_nums(self):
        user3 = User.objects.create_user(username='user3', password='12345', email="xyz@cde.com")
        p1_clues = self.puzzle1.get_clues()
        p2_clues = self.puzzle2.get_clues()
        session1 = SolverSession.new(self.puzzle1, self.user2)
        session2 = SolverSession.new(self.puzzle1, user3)
        session3 = SolverSession.new(self.puzzle2, user3)
        session1.set_solved_clue(clue=p1_clues[1])
        session1.set_solved_clue(clue=p1_clues[4])
        session2.set_solved_clue(clue=p1_clues[2])
        session2.set_revealed_clue(clue=p1_clues[0])
        session3.set_revealed_clue(clue=p2_clues[2])
        clue_ids_set1 = session1.get_all_solved_clue_ids()
        clue_ids_set2 = session2.get_all_solved_clue_ids()
        clue_ids_set3 = session3.get_all_solved_clue_ids()
        self.assertListEqual(clue_ids_set1, [2, 5])
        self.assertListEqual(clue_ids_set2, [3])
        self.assertListEqual(clue_ids_set3, [])

    def test_get_all_revealed_clue_nums(self):
        p1_clues = self.puzzle1.get_clues()
        p2_clues = self.puzzle2.get_clues()
        session1 = SolverSession.new(self.puzzle1, self.user2)
        session2 = SolverSession.new(self.puzzle1, self.user2)
        session3 = SolverSession.new(self.puzzle2, self.user1)
        session1.set_revealed_clue(clue=p1_clues[1])
        session1.set_revealed_clue(clue=p1_clues[4])
        session2.set_revealed_clue(clue=p1_clues[2])
        session2.set_solved_clue(clue=p1_clues[0])
        session3.set_solved_clue(clue=p2_clues[2])
        clue_ids_set1 = session1.get_all_revealed_clue_ids()
        clue_ids_set2 = session2.get_all_revealed_clue_ids()
        clue_ids_set3 = session3.get_all_revealed_clue_ids()
        self.assertListEqual(clue_ids_set1, [2, 5, 3])
        self.assertListEqual(clue_ids_set2, [2, 5, 3])
        self.assertListEqual(clue_ids_set3, [])
