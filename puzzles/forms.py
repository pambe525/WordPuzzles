from django.forms import ModelForm
from puzzles.models import Crossword
from django.contrib.auth.models import User


class NewCrosswordForm(ModelForm):

    class Meta:
        model = Crossword
        fields = ['size']

    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['size'].label = "Grid Size"