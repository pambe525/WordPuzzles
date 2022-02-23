from django.contrib.auth.models import User
from django.test import TestCase

from user_auth.forms import NewUserForm
from puzzles.forms import WordPuzzleForm
from puzzles.models import WordPuzzle

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
        self.assertEqual(len(form.fields), 3)
        self.assertIsNotNone(form.fields['type'])
        self.assertIsNotNone(form.fields['title'])
        self.assertIsNotNone(form.fields['desc'])

    def test_form_initialized_with_instance(self):
        user = User.objects.create_user('testuser')
        puzzle = WordPuzzle.objects.create(editor=user, title="Some title")
        form = WordPuzzleForm(instance=puzzle)
        self.assertEqual(form.initial['type'], 1)
        self.assertEqual(form.initial['title'], "Some title")
        self.assertEqual(form.initial['desc'], None)

    def test_form_has_no_error_if_title_is_blank(self):
        user = User.objects.create_user('testuser')
        puzzle_data = {'editor': user, 'type': 1, 'title': ""}
        form = WordPuzzleForm(data=puzzle_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.errors, {})
