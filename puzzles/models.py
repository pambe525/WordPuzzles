from django.db import models
from django.contrib.auth.models import User

class Puzzle(models.Model):
    is_xword = models.BooleanField(default=True)
    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    size = models.IntegerField(default=0)
    desc = models.TextField(default="")
    data = models.TextField(default="")
    shared_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        if self.is_xword:
            puzzle_size = "(" + str(self.size) + "x" + str(self.size) + ")"
            return "Puzzle #" + str(self.id) + ": Crossword Puzzle " + puzzle_size
        else:
            puzzle_size = "(" + str(self.size) + " clues)"
            return "Puzzle #" + str(self.id) + ": Word Puzzle " + puzzle_size

class WordPuzzle(models.Model):
    TYPE_CHOICES = [(0, "Non-cryptic Clues"), (1, "Cryptic Clues")]
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    size = models.IntegerField(default=5)
    desc = models.TextField(null=True)
    shared_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        puzzle_type = str(self.TYPE_CHOICES[self.type][1]) + " (" + str(self.size) + ")"
        return "Puzzle #" + str(self.id) + ": " + puzzle_type

class Clue(models.Model):
    puzzle = models.ForeignKey(WordPuzzle, on_delete=models.CASCADE)
    clue_num = models.IntegerField()
    answer = models.CharField(null=True, max_length=32)
    clue_text = models.TextField(null=True)
    parsing = models.TextField(null=True)
