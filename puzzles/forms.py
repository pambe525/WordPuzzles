import re

from django.forms import ModelForm

from puzzles.models import WordPuzzle, Clue


class WordPuzzleForm(ModelForm):
    class Meta:
        model = WordPuzzle
        fields = ['type', 'desc']

    def __init__(self, *args, **kwargs):
        super(WordPuzzleForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['style'] = 'width: 160px; height: 28px'
        self.fields['desc'].widget.attrs['style'] = "width: 100%; height:60px"
        self.fields['desc'].help_text = "Optional description, instructions or guidelines"


class ClueForm(ModelForm):
    class Meta:
        model = Clue
        fields = ['answer', 'clue_text', 'parsing', 'points']

    def __init__(self, *args, **kwargs):
        super(ClueForm, self).__init__(*args, **kwargs)
        self.fields['answer'].help_text = "Required. Should be < 25 chars. Letters and hyphen only."
        self.fields['answer'].widget.attrs['style'] = 'width:200px; text-transform:uppercase'
        self.fields['answer'].widget.attrs['pattern'] = '[A-Za-z \-]+'
        self.fields['clue_text'].help_text = "Required. Answer length will be auto-added"
        self.fields['clue_text'].widget.attrs['style'] = 'height:50px'
        self.fields['parsing'].help_text = "Optional"
        self.fields['parsing'].widget.attrs['style'] = 'height:50px'
        self.fields['points'].widget.attrs['style'] = 'width: 40px; height: 28px'

    def clean_answer(self):
        value = self.cleaned_data['answer']
        forbidden_char = re.compile('[0-9@_!#$%^&*()<>?/\|}{~:,]')
        if forbidden_char.search(value) is not None:
            raise ValueError("Answer cannot contain non-alphabet characters")
        return value.upper()
