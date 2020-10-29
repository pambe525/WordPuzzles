from django.db import models
from django.contrib.auth.models import User

class Puzzle(models.Model):
    is_xword = models.BooleanField(default=True)
    is_ready = models.BooleanField(default=False)
    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    size = models.IntegerField(default=0)
    desc = models.TextField(default="")
    data = models.TextField(default="")
    shared_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        if (self.is_xword):
            puzzle_size = "(" + str(self.size) + "x" + str(self.size) + ")"
            return "#" + str(self.id) + " Crossword Puzzle " + puzzle_size
        else:
            puzzle_size = "(" + str(self.size) + " clues)"
            return "#" + str(self.id) + " Word Puzzle " + puzzle_size
