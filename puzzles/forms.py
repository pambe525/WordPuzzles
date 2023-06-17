import re
from unittest.case import skip

from django import forms
from django.forms import ModelForm, Form

from puzzles.models import WordPuzzle, Clue
from puzzles.text_parsers import NumberedItemsParser, ClueChecker


class WordPuzzleForm(ModelForm):
    class Meta:
        model = WordPuzzle
        fields = ['type', 'desc']

    def __init__(self, *args, **kwargs):
        super(WordPuzzleForm, self).__init__(*args, **kwargs)
        self.fields['type'].widget.attrs['style'] = 'width: 160px; height: 28px'
        self.fields['desc'].widget.attrs['style'] = "width: 100%; height:150px"
        self.fields['desc'].help_text = "Optional description, instructions or guidelines"


class AddCluesForm(Form):
    clues = forms.CharField(widget=forms.Textarea(), initial=None, label="Clues", required=True)
    answers = forms.CharField(widget=forms.Textarea(), initial=None, label="Answers", required=True)
    cleaned_data_list = []

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.fields['clues'].widget.attrs['rows'] = 5
        self.fields['clues'].widget.attrs['placeholder'] = "1. First clue"
        self.fields['clues'].help_text = "NOTE: Answer lengths at the end of each clue, are optional. " \
                                         "If omitted, they will be automatically added. "
        self.fields['answers'].widget.attrs['rows'] = 5
        self.fields['answers'].widget.attrs['placeholder'] = "1. the answer"
        self.fields['answers'].help_text = "Specify a single unique answer for each clue."
        self.cleaned_data_list = []

    def clean(self):
        clues_parser = NumberedItemsParser(self.data["clues"])
        answers_parser = NumberedItemsParser(self.data["answers"], 1)
        answers_parser.check_non_alpha_chars()
        answers_parser.cross_check_entries(clues_parser.items_dict)
        if clues_parser.error: self.add_error("clues", clues_parser.error)
        if answers_parser.error: self.add_error('answers', answers_parser.error)
        self.__build_cleaned_data(clues_parser.items_dict, answers_parser.items_dict)

    def __build_cleaned_data(self, clues_dict, answers_dict):
        if not self.has_error('clues') and not self.has_error('answers'):
            for key in clues_dict:
                clue_data = {'clue_num': key, 'clue_text': clues_dict[key], 'answer': answers_dict[key]}
                self.cleaned_data_list.append(clue_data)


class ClueForm(ModelForm):
    class Meta:
        model = Clue
        fields = ['clue_text', 'answer', 'parsing', 'points']

    def __init__(self, *args, **kwargs):
        super(ClueForm, self).__init__(*args, **kwargs)
        self.fields['answer'].help_text = "Required [< 25 chars]. Letters, spaces and hyphens only."
        self.fields['answer'].widget.attrs['style'] = 'width:200px; text-transform:uppercase'
        self.fields['clue_text'].help_text = "Required. Answer length will be auto-added, if not specified."
        self.fields['clue_text'].widget.attrs['style'] = 'height:50px'
        self.fields['parsing'].help_text = "Optional"
        self.fields['parsing'].widget.attrs['style'] = 'height:50px'
        self.fields['points'].widget.attrs['style'] = 'width: 40px; height: 28px'

    def clean_answer(self):
        answer = self.data['answer']
        clue_text = self.data['clue_text']
        if ClueChecker().has_non_alpha_chars(answer):
            self.add_error('answer', "Answer cannot contain non-alphabet characters")
        elif not ClueChecker().has_single_answer(answer):
            self.add_error('answer', "Multiple answers specified.")
        elif not ClueChecker().has_matching_answer_lengths(clue_text, answer):
            self.add_error('answer', "Answer does not match specified answer length.")
        return answer


class SortPuzzlesForm(Form):
    SORT_CHOICES = [('desc', 'Description'), ('editor__username', 'Editor'), ('size', 'No. of Clues'),
                    ('shared_at', 'Posted On'), ('id', 'Puzzle #'), ('type', 'Puzzle Type'),
                    ('total_points', 'Total Points')]
    ORDER_CHOICES = [('-', 'Descending'), ('', 'Ascending')]

    def __init__(self, *args, **kwargs):
        super(SortPuzzlesForm, self).__init__(*args, **kwargs)
        self.fields['sort_by'] = forms.ChoiceField(choices=self.SORT_CHOICES, initial='shared_at', label='Sort by:',
                                                   widget=forms.Select(
                                                       attrs={'style': 'height:26px', 'onchange': 'form.submit();'}))
        self.fields['order'] = forms.ChoiceField(choices=self.ORDER_CHOICES, label='Order', initial='-',
                                                 widget=forms.Select(
                                                     attrs={'style': 'height:26px', 'onchange': 'form.submit();'}))
