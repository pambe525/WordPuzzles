from django.db import models
from django.contrib.auth.models import User


# class Crossword(models.Model):
#     editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
#     grid_size = models.IntegerField(default=15)
#     is_ready = models.BooleanField(default=0)
#     grid_blocks = models.TextField(default="")  # blocks is a comma-separated string of cell indices
#     across_words = models.TextField(default="")  # across words as a json string
#     down_words = models.TextField(default="")  # down words as a json string
#     created_at = models.DateTimeField(auto_now_add=True, editable=False)
#     modified_at = models.DateTimeField(auto_now=True, editable=False)
#
#     def __str__(self):
#         puzzle_size = "(" + str(self.grid_size) + "x" + str(self.grid_size) + ")"
#         return "Crossword Puzzle #" + str(self.id) + " " + puzzle_size
#

class Puzzle(models.Model):
    is_xword = models.BooleanField(default=True)
    is_ready = models.BooleanField(default=False)
    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    size = models.IntegerField(default=0)
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
