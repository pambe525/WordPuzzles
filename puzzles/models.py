from django.db import models

# Create your models here.

class Crossword(models.Model):
    size_choices = [(11,'11 x 11'),(13, '13 x 13'), (15, '15 x 15')]
    editor = models.ForeignKey('auth.User', null=True, on_delete=models.CASCADE)
    size = models.IntegerField(default=15, choices=size_choices)
    blocks = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return "Crossword Puzzle #" + str(self.id)
