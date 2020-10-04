from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Crossword(models.Model):
    editor = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    grid_size = models.IntegerField(default=15)
    grid_content = models.TextField(default="", max_length=625)  # 25x25 grid
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return "Crossword Puzzle #" + str(self.id)
