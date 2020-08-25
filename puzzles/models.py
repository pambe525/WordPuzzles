from django.db import models

# Create your models here.

class Puzzle(models.Model):
    title = models.CharField(max_length=100)
    editor = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.title
