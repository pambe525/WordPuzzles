from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


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
    #INTEGER_CHOICES = [tuple([x, x]) for x in range(5, 26)]clear
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    desc = models.TextField(null=True, blank=True)
    size = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    shared_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        puzzle_type = str(self.TYPE_CHOICES[self.type][1])
        points = "[" + str(self.total_points) + " points]"
        return "Puzzle #" + str(self.id) + ": " + str(self.size) + " " + puzzle_type + " " + points

    def add_clue(self, form_data_dict):
        self.size += 1
        self.total_points += form_data_dict['points']
        new_clue = Clue.objects.create(puzzle=self, clue_num=self.size, **form_data_dict)
        self.save(update_fields=['size', 'total_points'])
        return new_clue

    def update_clue(self, clue_num, form_data_dict):
        clue = Clue.objects.filter(puzzle=self, clue_num=clue_num)
        self.total_points += (form_data_dict['points'] - clue[0].points)
        clue.update(**form_data_dict)
        self.save(update_fields=['total_points'])
        return clue

    def delete_clue(self, clue_num):
        clue = Clue.objects.get(puzzle=self, clue_num=clue_num)
        self.total_points -= clue.points
        self.size -= 1
        clue.delete()
        self.save(update_fields=['size', 'total_points'])
        self._adjust_clue_nums(clue_num)

    def _adjust_clue_nums(self, start_clue_num):
        clues = Clue.objects.filter(puzzle=self)
        new_clue_num = start_clue_num
        for index in range(start_clue_num-1, len(clues)):
            clues[index].clue_num = new_clue_num
            new_clue_num += 1
            clues[index].save(update_fields=['clue_num'])

    def get_clues(self):
        return Clue.objects.filter(puzzle=self).order_by('clue_num')

class Clue(models.Model):
    INTEGER_CHOICES = [tuple([x, x]) for x in range(1, 6)]
    puzzle = models.ForeignKey(WordPuzzle, on_delete=models.CASCADE)
    clue_num = models.IntegerField(null=True)
    answer = models.CharField(null=True, max_length=24)
    clue_text = models.TextField(null=True)
    parsing = models.TextField(null=True, blank=True)
    points = models.IntegerField(default=1, choices=INTEGER_CHOICES)

    def __str__(self):
        text = ''
        text += ("<#>" if self.clue_num is None else str(self.clue_num)) + ". "
        text += ("<clue>" if self.clue_text is None else self.clue_text) + " ["
        text += ("<answer>" if self.answer is None else self.answer) + "]"
        return text
