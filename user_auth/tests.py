from django.test import TestCase
from .forms import NewUserForm
from django.contrib.auth.models import User


class NewUserFormTest(TestCase):
    def test_form_has_email_as_required(self):
        form = NewUserForm()
        self.assertEqual(form.fields["email"].required, True)

    def test_form_has_first_name_as_required(self):
        form = NewUserForm()
        self.assertEqual(form.fields["first_name"].required, True)

    def test_form_has_correct_fields(self):
        form = NewUserForm()
        self.assertEquals(form.Meta.fields[0], "username")
        self.assertEquals(form.Meta.fields[1], "email")
        self.assertEquals(form.Meta.fields[2], "first_name")
        self.assertEquals(form.Meta.fields[3], "password1")
        self.assertEquals(form.Meta.fields[4], "password2")

    def test_form_does_not_save_if_first_name_is_blank(self):
        data_dict = {'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!',
                     'email': 'a@b.com', 'first_name': ''
                     }
        form = NewUserForm(data_dict)
        with self.assertRaises(ValueError):
            form.save()

    def test_form_saved_with_correct_data(self):
        data_dict = {'username': 'pga', 'password1': 'tester1!', 'password2': 'tester1!',
                     'email': 'a@b.com', 'first_name': 'joe'
                     }
        form = NewUserForm(data_dict)
        user = form.save()
        self.assertEquals(type(user), User)