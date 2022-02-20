from django.contrib.auth.models import User
from django.test import TestCase

from user_auth.forms import NewUserForm

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
