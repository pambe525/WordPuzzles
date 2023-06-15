from unittest.case import skip

from django.contrib.auth.models import User
from django.test import TestCase

from puzzles.forms import WordPuzzleForm, ClueForm, AddCluesForm
from puzzles.models import WordPuzzle
from user_auth.forms import NewUserForm


class NewUserFormTest(TestCase):

    def test_form_has_all_fields_as_required(self):
        form = NewUserForm()
        self.assertEqual(form.fields["email"].required, True)
        self.assertEqual(form.fields["username"].required, True)
        self.assertEqual(form.fields["password1"].required, True)
        self.assertEqual(form.fields["password2"].required, True)

    def test_form_has_correct_meta_fields(self):
        form = NewUserForm()
        self.assertEqual(len(form.Meta.fields), 4)
        self.assertEqual(form.Meta.fields[0], "username")
        self.assertEqual(form.Meta.fields[1], "password1")
        self.assertEqual(form.Meta.fields[2], "password2")
        self.assertEqual(form.Meta.fields[3], "email")

    def test_form_saved_with_correct_data(self):
        data_dict = {
            'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!', 'email': 'a@b.com'
        }
        form = NewUserForm(data_dict)
        user = form.save()
        self.assertEqual(type(user), User)

    def test_form_label_modified_for_password2(self):
        form = NewUserForm()
        self.assertEqual(form.fields['password2'].label, "Confirm")

    def test_form_helptext_for_parent_fields(self):
        form = NewUserForm()
        self.assertIn("Must be unique with no spaces.", form.fields["username"].help_text)
        self.assertIn("Must contain at least 8 characters", form.fields["password1"].help_text)
        self.assertIn("Confirm Password", form.fields["password2"].help_text)
        self.assertIn("Required: Used for password reset", form.fields["email"].help_text)

    def test_form_email_is_cleaned_before_save(self):
        data_dict = {
            'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!', 'email': '\na@b.com'
        }
        form = NewUserForm(data_dict)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "a@b.com")


class WordPuzzleFormTest(TestCase):

    def test_form_has_needed_fields(self):
        form = WordPuzzleForm()
        self.assertEqual(len(form.fields), 2)
        self.assertIsNotNone(form.fields['type'])
        self.assertIsNotNone(form.fields['desc'])

    def test_form_initialized_with_instance(self):
        user = User.objects.create_user('testuser')
        puzzle = WordPuzzle.objects.create(editor=user, desc="Some title")
        form = WordPuzzleForm(instance=puzzle)
        self.assertEqual(form.initial['type'], 1)
        self.assertEqual(form.initial['desc'], "Some title")

    def test_form_has_no_error_if_desc_is_blank(self):
        user = User.objects.create_user('testuser')
        puzzle_data = {'editor': user, 'type': 1, 'desc': ''}
        form = WordPuzzleForm(data=puzzle_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})


class AddCluesFormTest(TestCase):

    def test_form_default_fields(self):
        form = AddCluesForm()
        self.assertTrue(form.fields['clues'].required)
        self.assertTrue(form.fields['answers'].required)

    def test_new_lines_with_no_text_in_form_fields_returns_error(self):
        form_data = {'clues': '\r\n   \n\n', 'answers': '  \n'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 1)
        self.assertEqual(len(form['answers'].errors), 1)
        self.assertEqual(form['clues'].errors[0], "This field is required.")
        self.assertEqual(form['answers'].errors[0], "This field is required.")

    def test_numbered_items_return_no_error(self):
        form_data = {'clues': '1. numbered clue', 'answers': '1 answer'}
        form = AddCluesForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(len(form['answers'].errors), 0)

    def test_non_numbered_item_num_is_flagged_in_error(self):
        form_data = {'clues': '1. numbered\n\nnot numbered\n no number', 'answers': 'not numbered\n1 answer'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 1)
        self.assertEqual(len(form['answers'].errors), 1)
        self.assertEqual(form['clues'].errors[0], "Item 2 is not numbered.")
        self.assertEqual(form['answers'].errors[0], "Item 1 is not numbered.")

    def test_duplicate_item_number_returns_error(self):
        form_data = {'clues': '1 first \n2. second \n1 third\n\n2 fourth', 'answers': '1 first \n1. second \n2 third '}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['clues'].errors[0], "Item 3 has duplicate item number 1.")
        self.assertEqual(form['answers'].errors[0], "Item 2 has duplicate item number 1.")

    def test_duplicate_item_text_returns_error(self):
        form_data = {'clues': '1 first \n2. second \n3 first\n\n4 second', 'answers': '1 first \n2. first \n3 third '}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['clues'].errors[0], "Item 3 has duplicate text.")
        self.assertEqual(form['answers'].errors[0], "Item 2 has duplicate text.")

    def test_blank_item_text_returns_error(self):
        form_data = {'clues': '1 first \n2.  \n3 third\n\n4 fourth', 'answers': '1 first \n2. second \n3'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form['clues'].errors[0], "Item 2 has no text.")
        self.assertEqual(form['answers'].errors[0], "Item 3 has no text.")

    def test_valid_form_input(self):
        form_data = {'clues': '1 first \n2. second \r\n\n3 third\n', 'answers': '\r\n1 one \n3. three \n2 two'}
        form = AddCluesForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(len(form['answers'].errors), 0)

    def test_more_than_one_answers_returns_error(self):
        form_data = {'clues': '1 first \n2. second \r\n\n', 'answers': '\r\n1 first one\n2. three1, three2'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(len(form['answers'].errors), 1)
        self.assertEqual(form['answers'].errors[0], "Item 2 has more than one entry.")

    def test_less_answers_than_clues(self):
        form_data = {'clues': '1 clue one\n2. clue two\n3 clue three', 'answers': '1 first\n3. second'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(form['answers'].errors[0], "Corresponding cross-entry for #2 missing.")

    def test_more_answers_than_clues(self):
        form_data = {'clues': '1 clue one\n2. clue two', 'answers': '1 first\n2. second\n3. third'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(form['answers'].errors[0], "Item 3 has no matching cross-entry.")

    def test_mismatch_in_answers_length(self):
        form_data = {'clues': '1 clue one\n2. clue two (7, 3)', 'answers': '1 first\n2. second one'}
        form = AddCluesForm(form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(form['answers'].errors[0], "Item 2 mismatches specified cross-entry length.")

    def test_matching_answers_length(self):
        form_data = {'clues': '1 clue one (3-2, 1, 5-2)\n2. clue two (6, 3)',
                     'answers': '1 one-of a mixed-up\n2. second one'}
        form = AddCluesForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form['clues'].errors), 0)
        self.assertEqual(len(form['answers'].errors), 0)

    def test_valid_form_is_saved_with_all_entries(self):
        form_data = {'clues': '1 clue one (8)\n3. clue two (6, 3)\n5 clue (three)',
                     'answers': '1 distance\n5. no length\n3   second one'}
        form = AddCluesForm(form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data_list), 3)
        self.assertEqual(form.cleaned_data_list[0]['clue_num'], 1)
        self.assertEqual(form.cleaned_data_list[1]['clue_num'], 3)
        self.assertEqual(form.cleaned_data_list[2]['clue_num'], 5)
        self.assertEqual(form.cleaned_data_list[0]['clue_text'], 'clue one (8)')
        self.assertEqual(form.cleaned_data_list[1]['clue_text'], 'clue two (6, 3)')
        self.assertEqual(form.cleaned_data_list[2]['clue_text'], 'clue (three)')
        self.assertEqual(form.cleaned_data_list[0]['answer'], 'distance')
        self.assertEqual(form.cleaned_data_list[1]['answer'], 'second one')
        self.assertEqual(form.cleaned_data_list[2]['answer'], 'no length')


class ClueFormTest(TestCase):

    def test_form_default_fields(self):
        form = ClueForm()
        self.assertEqual(form['answer'].value(), None)
        self.assertEqual(form['clue_text'].value(), None)
        self.assertEqual(form['parsing'].value(), None)
        self.assertEqual(form['points'].value(), 1)

    def test_form_with_initialized_values(self):
        form_data = {'answer': 'my word', 'clue_text': 'some clue text',
                     'parsing': 'def', 'points': 3}
        form = ClueForm(form_data)
        self.assertEqual(form['answer'].value(), 'my word')
        self.assertEqual(form['clue_text'].value(), 'some clue text')
        self.assertEqual(form['parsing'].value(), 'def')
        self.assertEqual(form['points'].value(), 3)

    def test_form_converts_answer_to_uppercase_when_is_valid(self):
        form_data = {'answer': ' my-word ', 'clue_text': 'some clue text',
                     'parsing': 'def', 'points': 3}
        form = ClueForm(form_data)
        form.is_valid()
        self.assertEqual(form.cleaned_data['answer'], 'MY-WORD')

    def test_form_does_not_allow_numbers_in_answer(self):
        form_data = {'answer': 'word1', 'clue_text': 'some clue text',
                     'parsing': 'def', 'points': 3}
        form = ClueForm(form_data)
        self.assertRaises(ValueError, form.is_valid)

    def test_form_adds_answer_length_to_cluetext_when_is_valid(self):
        form_data = {'answer': 'my word', 'clue_text': 'some clue text',
                     'parsing': 'def', 'points': 3}
        form = ClueForm(form_data)
        form.is_valid()
        self.assertEqual(form.cleaned_data['answer'], 'MY WORD')
