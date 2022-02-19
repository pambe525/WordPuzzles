from django.contrib import admin
from .models import Puzzle, WordPuzzle, Clue

# Register your models here.
admin.site.register(Puzzle)
admin.site.register(WordPuzzle)
admin.site.register(Clue)
