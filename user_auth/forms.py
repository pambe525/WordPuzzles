from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Needed to email forgotten password")
    first_name = forms.CharField(required=True, label="Screen Name", help_text="Use your first name")

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = "Required. Letters, digits eg. johnsmith2"
        self.fields['password1'].help_text = "Must contain at least 8 characters"
        self.fields['password2'].help_text = "Confirm Password"

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.file_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user
