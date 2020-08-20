from django.test import TestCase
from .models import Puzzle

class PuzzleModelTest(TestCase):
    def test_string_representation(self):
        puzzle = Puzzle(title="My Puzzle")
        self.assertEqual(str(puzzle), puzzle.title)

