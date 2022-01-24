from django.contrib.auth import logout, login
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
        context = {'signin_form': form, 'signup_form': NewUserForm(),
                   'active_tab':'tabSignIn'}
        if not form.is_valid():
            return render(request, "login.html", context)
        else:
            user = form.save()
            login(request, user)
            return redirect("home")

class SignUpView(View):
    def get(self, request):
        context = {'signin_form': AuthenticationForm(), 'signup_form': NewUserForm(),
                   'active_tab': 'tabSignUp'}
        if not request.user.is_authenticated:
            return render(request, "login.html", context)
        else:
            return redirect("home")

    def post(self, request):
        form = NewUserForm(request.POST)
        context = {'signin_form': AuthenticationForm(), 'signup_form': form,
                   'active_tab':'tabSignUp'}
        if not form.is_valid():
            return render(request, "login.html", context)
        else:
            user = form.save()
            login(request, user)
            return redirect("home")

class SignOutView(View):
    def get(self, request):
        logout(request)
        return redirect("login")
