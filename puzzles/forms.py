from django.forms import ModelForm

from puzzles.models import WordPuzzle


class WordPuzzleForm(ModelForm):
    class Meta:
        model = WordPuzzle
        fields = ['type', 'desc']

    def __init__(self, *args, **kwargs):
        super(WordPuzzleForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['style'] = 'width: 160px; height: 28px'
        self.fields['desc'].widget.attrs['style'] = "width: 300px; height:100px"
        self.fields['desc'].help_text = "Optional description, instructions or guidelines"
