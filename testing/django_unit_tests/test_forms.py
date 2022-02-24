from django.contrib.auth.models import User
from django.test import TestCase

from user_auth.forms import NewUserForm
from puzzles.forms import WordPuzzleForm, ClueForm
from puzzles.models import WordPuzzle, Clue

class NewUserFormTest(TestCase):

    def test_form_has_email_as_required(self):
        form = NewUserForm()
        self.assertEqual(form.fields["email"].required, True)

    def test_form_has_correct_fields(self):
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
        self.assertIn("Required. Use your first name (case-sensitive)", form.fields["username"].help_text)
        self.assertIn("Must contain at least 8 characters", form.fields["password1"].help_text)
        self.assertIn("Confirm Password", form.fields["password2"].help_text)

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
        puzzle_data = {'editor': user, 'type': 1, 'desc':''}
        form = WordPuzzleForm(data=puzzle_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})

class ClueFormTest(TestCase):

    def test_form_default_fields(self):
        form = ClueForm()
        self.assertEqual(form['answer'].value(), None)
        self.assertEqual(form['clue_text'].value(), None)
        self.assertEqual(form['parsing'].value(), None)
        self.assertEqual(form['points'].value(), 1)

    def test_form_with_initialized_values(self):
        form_data = {'answer':'my word', 'clue_text':'some clue text',
                     'parsing':'def', 'points': 3}
        form = ClueForm(form_data)
        self.assertEqual(form['answer'].value(), 'my word')
        self.assertEqual(form['clue_text'].value(), 'some clue text')
        self.assertEqual(form['parsing'].value(), 'def')
        self.assertEqual(form['points'].value(), 3)

    def test_form_converts_answer_to_uppercase_when_is_valid(self):
        form_data = {'answer':' my-word ', 'clue_text':'some clue text',
                     'parsing':'def', 'points': 3}
        form = ClueForm(form_data)
        form.is_valid()
        self.assertEqual(form.cleaned_data['answer'], 'MY-WORD')

    def test_form_does_not_allow_numbers_in_answer(self):
        form_data = {'answer':'word1', 'clue_text':'some clue text',
                     'parsing':'def', 'points': 3}
        form = ClueForm(form_data)
        self.assertRaises(ValueError, form.is_valid)

    def test_form_adds_answer_length_to_cluetext_when_is_valid(self):
        form_data = {'answer':'my word', 'clue_text':'some clue text',
                     'parsing':'def', 'points': 3}
        form = ClueForm(form_data)
        form.is_valid()
        self.assertEqual(form.cleaned_data['answer'], 'MY WORD')

