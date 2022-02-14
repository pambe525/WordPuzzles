from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Used for forgotten password")

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)
        self.fields['password2'].label = "Confirm"
        self.fields['username'].help_text = "Required. Use your first name (case-sensitive)"
        self.fields['password1'].help_text = "Must contain at least 8 characters"
        self.fields['password2'].help_text = "Confirm Password"
        self.fields['email'].widget.attrs['style'] = 'width:250px'

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email']

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserAccountForm(UserChangeForm):
    password = None
    email = forms.EmailField(required=True, error_messages={'required':'Email is required.'})
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']





