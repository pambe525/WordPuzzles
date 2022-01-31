from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views import View

from .forms import NewUserForm

class SignInView(View):

    def get(self, request):
        context = {'signin_form': AuthenticationForm(), 'signup_form': NewUserForm(),
                   'active_tab': 'tabSignIn'}
        if not request.user.is_authenticated:
            return render(request, "login.html", context)
        else:
            return redirect("home")

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        context = {'signin_form': form, 'signup_form': NewUserForm(),'active_tab':'tabSignIn'}
        if not form.is_valid():
            return render(request, "login.html", context)
        else:
            user = form.get_user()
            login(request, user)
            return redirect("home")

class SignUpView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, "signup.html", {'form': NewUserForm()})
        else:
            return redirect("home")

    def post(self, request):
        form = NewUserForm(request.POST)
        if not form.is_valid():
            return render(request, "login.html", {'form': form})
        else:
            user = form.save()
            login(request, user)
            return redirect("home")

class SignOutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")

class ResetPasswordView(View):
    def get(self, request):
        logout(request)
        return redirect("login")